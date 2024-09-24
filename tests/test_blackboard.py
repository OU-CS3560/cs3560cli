# type: ignore
import pytest

from cs3560cli.lms.blackboard import filter_by_role, parse_url_for_course_id


@pytest.fixture
def sample_response():
    return {
        "results": [
            {
                "id": "_1_1",
                "userId": "_1_1",
                "user": {
                    "id": "_1_1",
                    "uuid": "1",
                    "userName": "aa000001",
                    "modified": "2024-02-22T00:00:00.000Z",
                    "systemRoleIds": ["User"],
                    "availability": {"available": "Yes"},
                    "name": {
                        "given": "A",
                        "family": "A",
                        "preferredDisplayName": "GivenName",
                    },
                    "contact": {"email": "aa000001@ohio.edu"},
                    "avatar": {
                        "viewUrl": "https://blackboard.ohio.edu/learn/api/public/v1/users/_1_1/avatar",
                        "source": "Default",
                    },
                },
                "courseRoleId": "TeachingAssistant",
            },
            {
                "id": "_2_1",
                "userId": "_2_1",
                "user": {
                    "id": "_2_1",
                    "uuid": "2",
                    "userName": "bb000002",
                    "modified": "2024-02-24T00:00:00.000Z",
                    "systemRoleIds": ["User"],
                    "availability": {"available": "Yes"},
                    "name": {
                        "given": "B",
                        "family": "B",
                        "middle": "B",
                        "preferredDisplayName": "GivenName",
                    },
                    "contact": {"email": "bb000002@ohio.edu"},
                    "avatar": {
                        "viewUrl": "https://blackboard.ohio.edu/learn/api/public/v1/users/_2_1/avatar",
                        "source": "Default",
                    },
                },
                "courseRoleId": "Student",
            },
            {
                "id": "_3_1",
                "userId": "_3_1",
                "user": {
                    "id": "_3_1",
                    "uuid": "3",
                    "userName": "cc000110",
                    "modified": "2024-02-24T00:00:00.000Z",
                    "systemRoleIds": ["User"],
                    "availability": {"available": "Yes"},
                    "name": {
                        "given": "C",
                        "family": "C",
                        "middle": "C",
                        "preferredDisplayName": "GivenName",
                    },
                    "contact": {"email": "cc000110@ohio.edu"},
                    "avatar": {
                        "viewUrl": "https://blackboard.ohio.edu/learn/api/public/v1/users/_3_1/avatar",
                        "source": "Default",
                    },
                },
                "courseRoleId": "Instructor",
            },
        ]
    }


def test_parse_url_for_course_id():
    assert parse_url_for_course_id("https://blackboard.ohio.edu/ultra/courses") is None
    assert (
        parse_url_for_course_id(
            "https://blackboard.ohio.edu/ultra/courses/_631022_1/cl/outline"
        )
        == "_631022_1"
    )
    assert (
        parse_url_for_course_id(
            "https://blackboard.ohio.edu/webapps/blackboard/content/listContentEditable.jsp?content_id=_14346954_1&course_id=_631022_1&mode=reset"
        )
        == "_631022_1"
    )
    assert (
        parse_url_for_course_id(
            "https://blackboard.ohio.edu/ultra/courses/_642196_1/cl/outline"
        )
        == "_642196_1"
    )


def test_filter_by_role(sample_response):
    assert len(filter_by_role(sample_response["results"])) == 1
