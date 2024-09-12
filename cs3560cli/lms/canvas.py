"""
Collection of functions for Canvas LMS.
"""

import typing as ty
from dataclasses import dataclass
from urllib.parse import urlparse

import requests


def parse_url_for_course_id(url: str) -> ty.Optional[str]:
    """Parse Canvas' course URL for course ID."""
    u = urlparse(url)
    tokens = u.path.split("/")

    try:
        course_kw_pos = tokens.index("courses")
        if len(tokens) <= course_kw_pos + 1:
            # e.g. url ends in /courses and has nothing else after.
            raise ValueError()
        return tokens[course_kw_pos + 1]
    except ValueError:
        return None


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
    members: ty.List[GroupMember]


class CanvasApi:
    def __init__(self, token: str):
        self._token = token

    def get_students(self, course_id: str) -> ty.Optional[ty.List[ty.Any]]:
        """
        Retrive students in the course.
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
            "https://ohio.instructure.com/api/graphql",
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

    def get_submissions(self, assignment_id: str) -> ty.Optional[ty.List[Submission]]:
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
            "https://ohio.instructure.com/api/graphql",
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

    def get_groups_by_groupset_name(
        self, course_id: str, groupset_name: str
    ) -> ty.Optional[ty.List[Group]]:
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
            "https://ohio.instructure.com/api/graphql",
            headers=headers,
            data=payload,
        )

        if res.status_code == 200:
            response_data = res.json()
            groupsets = response_data["data"]["course"]["groupSetsConnection"]["nodes"]

            for groupset in groupsets:
                if groupset["name"] == groupset_name:
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
                    return groups

            return None
        else:
            return None
