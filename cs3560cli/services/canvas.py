"""
Collection of functions for Canvas LMS.
"""

import logging
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
import typing_extensions as ty

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


T = ty.TypeVar("T")


@dataclass
class User:
    id: str
    name: str
    email_address: str
    role: str

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(
            id=node["user"]["_id"],
            name=node["user"]["name"],
            email_address=node["user"]["email"],
            role=node["sisRole"],
        )

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


@dataclass
class Assignment:
    id: str
    name: str

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(id=node["_id"], name=node["name"])

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


@dataclass
class Comment:
    id: str
    author_email: str
    comment: str

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(
            id=node["_id"],
            author_email=node["author"]["email"],
            comment=node["comment"],
        )

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


@dataclass
class Submission:
    """Represent parsed submission data from Canvas."""

    id: str
    email: str
    submissionStatus: str
    url: str  # When the submission type is a website URL.
    comments: list[Comment]

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(
            id=node["_id"],
            email=node["user"]["email"],
            submissionStatus=node["submissionStatus"],
            url=node["url"],
            comments=Comment.from_graphql_nodes(node["commentsConnection"]["nodes"]),
        )

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


@dataclass
class GroupMember:
    name: str
    email: str

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(name=node["user"]["name"], email=node["user"]["email"])

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


@dataclass
class Group:
    name: str
    members: list[GroupMember]

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(
            name=node["name"],
            members=GroupMember.from_graphql_nodes(node["membersConnection"]["nodes"]),
        )

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


@dataclass
class GroupSet:
    name: str
    groups: list[Group]

    @classmethod
    def from_graphql_node(cls, node: dict[str, ty.Any]) -> ty.Self:
        return cls(
            name=node["name"],
            groups=Group.from_graphql_nodes(node["groupsConnection"]["nodes"]),
        )

    @classmethod
    def from_graphql_nodes(cls, nodes: list[dict[str, ty.Any]]) -> list[ty.Self]:
        return [cls.from_graphql_node(node) for node in nodes]


class CanvasApi:
    """Abstraction layer of various Graphql queries."""

    def __init__(self, token: str, graphql_endpoint: str | None = None):
        self._token = token

        if graphql_endpoint is not None:
            self.graphql_endpoint = graphql_endpoint
        else:
            self.graphql_endpoint = GRAPHQL_ENDPOINT

    def _send_request(
        self, payload: dict[str, ty.Any], method: str = "POST"
    ) -> dict[str, ty.Any] | None:
        """Send a request to the endpoint."""
        headers = {
            "User-Agent": "cs3560cli",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        res = requests.request(
            method,
            self.graphql_endpoint,
            headers=headers,
            data=payload,
        )

        if res.status_code == requests.codes.OKAY:
            return res.json()  # type: ignore[no-any-return]
        else:
            return None

    def get_users(self, course_id: str) -> list[User] | None:
        """
        Retrieve all users in the course.
        """
        query = """
            query ListUsers($courseId: ID!) {
                course(id: $courseId) {
                    _id
                    enrollmentsConnection {
                        nodes {
                            user {
                                _id
                                email
                                name
                            }
                            sisRole
                        }
                    }
                }
            }
        """
        response_data = self._send_request(
            {"query": query, "variables[courseId]": course_id}, method="POST"
        )

        if response_data is not None:
            return User.from_graphql_nodes(
                response_data["data"]["course"]["enrollmentsConnection"]["nodes"]
            )
        else:
            return None

    def get_students(self, course_id: str) -> list[User] | None:
        """
        Retrieve all students in the course.
        """
        users = self.get_users(course_id)
        if users is not None:
            students = []
            for user in users:
                # There is a "Test Student" that has no value in the email field.
                if user.role == "student" and user.email_address is not None:
                    students.append(user)
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
                            _id
                            submissionStatus
                            url
                            user {
                                email
                            }
                            commentsConnection {
                                nodes {
                                    _id
                                    comment
                                    author {
                                        email
                                    }
                                }
                            }
                        }
                    }
                    name
                }
            }
        """
        response_data = self._send_request(
            {"query": query, "variables[assignmentId]": assignment_id}, method="POST"
        )

        if response_data is not None:
            return Submission.from_graphql_nodes(
                response_data["data"]["assignment"]["submissionsConnection"]["nodes"]
            )
        else:
            return None

    def get_groupsets(self, course_id: str) -> list[GroupSet] | None:
        """Query tne GraphQL endpoint for groupsets in the course."""
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
        response_data = self._send_request(
            {"query": query, "variables[courseId]": course_id}, method="POST"
        )
        if response_data is not None:
            return GroupSet.from_graphql_nodes(
                response_data["data"]["course"]["groupSetsConnection"]["nodes"]
            )
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

    def get_assignments(self, course_id: str) -> list[Assignment] | None:
        query = """
            query ListAssignments($courseId: ID!) {
                course(id: $courseId) {
                    id
                    assignmentsConnection {
                        nodes {
                            _id
                            name
                        }
                    }
                }
            }
        """
        response_data = self._send_request(
            {"query": query, "variables[courseId]": course_id}, method="POST"
        )
        if response_data is not None:
            return Assignment.from_graphql_nodes(
                response_data["data"]["course"]["assignmentsConnection"]["nodes"]
            )
        else:
            return None
