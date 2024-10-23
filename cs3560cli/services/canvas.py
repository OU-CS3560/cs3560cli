"""
Collection of functions for Canvas LMS.
"""

import logging
import os
import typing as ty
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

GRAPHQL_ENDPOINT = "https://ohio.instructure.com/api/graphql"


def parse_url_for_course_id(url: str) -> str | None:
    """Parse Canvas' course URL for course ID."""
    u = urlparse(url)
    tokens = u.path.split("/")

    try:
        course_kw_pos = tokens.index("courses")
        if len(tokens) <= course_kw_pos + 1:
            # e.g. url ends in /courses and has nothing else after.
            return None
        return tokens[course_kw_pos + 1]
    except ValueError:
        # Exception raises by list.index().
        return None


def get_unique_names(path: Path | str) -> list[str]:
    """
    Return unique email handle in folder of submitted files.

    :param path: A path to folder containing files extracted from downloaded zip file.
    :type path: str, pathlib.Path
    :return: List of unique names.
    :rtype: list[str]
    :raises ValueError: When path is not a directory.
    """

    if isinstance(path, str):
        path = Path(path)

    if not (path.is_dir() or zipfile.is_zipfile(path)):
        raise ValueError(f"path ({path}) need to be a directory or a zip file.")

    # Get all files.
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, mode="r") as zip_f:
            files = zip_f.namelist()
    else:
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    names = []
    # Extract handles.
    for filename in files:
        tokens = filename.split("_")

        if len(tokens) != 0:
            names.append(tokens[0])

    unique_names = list(set(names))
    return unique_names


def categorize(source: Path | str, destination: Path | str) -> None:
    """
    Group files from the same student together in a folder.

    Pre-condition: A root_directory is the result of the
    extracting a files out from the archive file from Blackboard.

    Post-condition: In the destination folder, folders for each student
    will be created, and a file will be moved into its corresponding
    folder.

    :param source: A path to source directory.
    :type source: str, pathlib.Path

    :param destination: A path to destination directory.
    :type destination: str, pathlib.Path

    :raises ValueError: When path is not a directory.
    """

    if isinstance(source, str):
        source = Path(source)
    if isinstance(destination, str):
        destination = Path(destination)

    if not (source.is_dir() or zipfile.is_zipfile(source)):
        raise ValueError(f"source ({source}) is not a directory nor a zip file")

    # Get list of student email handles.
    unique_names = get_unique_names(source)

    # Create destination if not exist.
    if not destination.exists():
        os.mkdir(destination)
    elif not destination.is_dir():
        raise ValueError(f"destination ({destination}) exists and is not a directory")

    # Create folders in the destination.
    for name in unique_names:
        if not os.path.exists(os.path.join(destination, name)):
            os.mkdir(os.path.join(destination, name))

    # Renaming and move files into directory.
    if zipfile.is_zipfile(source):
        zip_f = zipfile.ZipFile(source, mode="r")
        files = zip_f.namelist()
    else:
        files = [
            f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))
        ]

    for raw_filename in files:
        logging.info("raw file name: %s" % raw_filename)  # noqa: UP031

        # Get student name.
        name = raw_filename.split("_")[0]

        # Move file
        try:
            if zipfile.is_zipfile(source):
                zip_f.extract(
                    raw_filename,
                    path=os.path.join(destination, name),
                )
            else:
                os.rename(
                    os.path.join(source, raw_filename),
                    os.path.join(destination, name, raw_filename),
                )
        except OSError:
            logging.error("oserror while operating on %s" % raw_filename)  # noqa: UP031

    if zipfile.is_zipfile(source):
        zip_f.close()


@dataclass
class Submission:
    """Represent parsed submission data from Canvas."""

    email: str
    submissionStatus: str
    url: str  # When the submission type is a website URL.


@dataclass
class GroupMember:
    name: str
    email: str


@dataclass
class Group:
    name: str
    members: list[GroupMember]


@dataclass
class GroupSet:
    name: str
    groups: list[Group]


class CanvasApi:
    def __init__(self, token: str, graphql_endpoint: str | None = None):
        self._token = token

        if graphql_endpoint is not None:
            self.graphql_endpoint = graphql_endpoint
        else:
            self.graphql_endpoint = GRAPHQL_ENDPOINT

    def get_students(self, course_id: str) -> list[ty.Any] | None:
        """
        Retrieve students in the course.
        """
        query = """
            query ListStudents($courseId: ID!) {
                course(id: $courseId) {
                    id
                    enrollmentsConnection {
                        nodes {
                            user {
                                email
                                name
                            }
                            sisRole
                        }
                    }
                }
            }
        """
        headers = {
            "User-Agent": "cs3560cli",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        payload = {"query": query, "variables[courseId]": course_id}
        res = requests.post(
            self.graphql_endpoint,
            headers=headers,
            data=payload,
        )

        if res.status_code == 200:
            response_data = res.json()
            course_members = response_data["data"]["course"]["enrollmentsConnection"][
                "nodes"
            ]
            students = []
            for member in course_members:
                # There is a "Test Student" that has no value in the email field.
                if (
                    member["sisRole"] == "student"
                    and member["user"]["email"] is not None
                ):
                    students.append(member)
            return students
        else:
            return None

    def get_submissions(self, assignment_id: str) -> list[Submission] | None:
        """Fetch submissions of the homework assignment.

        For now only the submission with type website URL is supported.
        """
        query = """
            query ListSubmission($assignmentId: ID!) {
                assignment(id: $assignmentId) {
                    submissionsConnection {
                        nodes {
                            submissionStatus
                            url
                            user {
                                email
                            }
                        }
                    }
                    name
                }
            }
        """
        headers = {
            "User-Agent": "cs3560cli",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        payload = {"query": query, "variables[assignmentId]": assignment_id}
        res = requests.post(
            self.graphql_endpoint,
            headers=headers,
            data=payload,
        )

        if res.status_code == 200:
            response_data = res.json()
            raw_submissions = response_data["data"]["assignment"][
                "submissionsConnection"
            ]["nodes"]
            submissions = []
            for data in raw_submissions:
                submission = Submission(
                    email=data["user"]["email"],
                    submissionStatus=data["submissionStatus"],
                    url=data["url"],
                )
                submissions.append(submission)
            return submissions
        else:
            return None

    def get_groupsets(self, course_id: str) -> list[GroupSet] | None:
        query = """
            query ListGroupsInGroupSet($courseId: ID!) {
                course(id: $courseId) {
                    groupSetsConnection {
                        nodes {
                            name
                            groupsConnection {
                                nodes {
                                    name
                                    membersConnection {
                                        nodes {
                                            user {
                                                email
                                                name
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        headers = {
            "User-Agent": "cs3560cli",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        payload = {"query": query, "variables[courseId]": course_id}
        res = requests.post(
            self.graphql_endpoint,
            headers=headers,
            data=payload,
        )

        if res.status_code == 200:
            response_data = res.json()
            raw_groupsets = response_data["data"]["course"]["groupSetsConnection"][
                "nodes"
            ]

            groupsets = []
            for groupset in raw_groupsets:
                groups = []
                for raw_group in groupset["groupsConnection"]["nodes"]:
                    members = []
                    for raw_member in raw_group["membersConnection"]["nodes"]:
                        members.append(
                            GroupMember(
                                name=raw_member["user"]["name"],
                                email=raw_member["user"]["email"],
                            )
                        )
                    groups.append(Group(name=raw_group["name"], members=members))
                groupsets.append(GroupSet(name=groupset["name"], groups=groups))

            return groupsets
        else:
            return None

    def get_groups_by_groupset_name(
        self, course_id: str, groupset_name: str
    ) -> list[Group] | None:
        groupsets = self.get_groupsets(course_id)
        if groupsets is None:
            return None

        for groupset in groupsets:
            if groupset.name == groupset_name:
                return groupset.groups
        return None
