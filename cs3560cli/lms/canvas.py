"""
Collection of functions for Canvas LMS.
"""

import typing as ty
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
                if (
                    member["sisRole"] == "student"
                    and member["user"]["email"] is not None
                ):
                    students.append(member)
            return students
        else:
            return None
