import requests

from cs3560cli.lms.canvas import CanvasApi, parse_url_for_course_id


def test_parse_url_for_course_id():
    assert (
        parse_url_for_course_id("https://ohio.instructure.com/courses/24840") == "24840"
    )
    assert (
        parse_url_for_course_id(
            "https://ohio.instructure.com/courses/24840/pages/content-overview?module_item_id=500553"
        )
        == "24840"
    )
    assert (
        parse_url_for_course_id(
            "https://ohio.instructure.com/calendar#view_name=month&view_start=2024-08-29"
        )
        is None
    )


class MockSuccessfulGroupSetResponse:
    @property
    def status_code(self):
        return 200

    @staticmethod
    def json():
        return {
            "data": {
                "course": {
                    "groupSetsConnection": {
                        "nodes": [
                            {
                                "name": "Term Project Teams",
                                "groupsConnection": {
                                    "nodes": [
                                        {
                                            "name": "test-team-1",
                                            "membersConnection": {
                                                "nodes": [
                                                    {
                                                        "user": {
                                                            "email": "rb000000@ohio.edu",
                                                            "name": "Rufus Bobcat1",
                                                        }
                                                    },
                                                    {
                                                        "user": {
                                                            "email": "rb000001@ohio.edu",
                                                            "name": "Rufus Bobcat2",
                                                        }
                                                    },
                                                ]
                                            },
                                        },
                                        {
                                            "name": "test-team-2",
                                            "membersConnection": {
                                                "nodes": [
                                                    {
                                                        "user": {
                                                            "email": "rb000002@ohio.edu",
                                                            "name": "Rufus Bobcat2",
                                                        }
                                                    },
                                                    {
                                                        "user": {
                                                            "email": "rb000003@ohio.edu",
                                                            "name": "Rufus Bobcat4",
                                                        }
                                                    },
                                                ]
                                            },
                                        },
                                    ]
                                },
                            }
                        ]
                    }
                }
            }
        }


def test_get_groups_by_groupset_name(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockSuccessfulGroupSetResponse()

    monkeypatch.setattr(requests, "post", mock_post)

    client = CanvasApi(token="fake-token")

    groups = client.get_groups_by_groupset_name("0", "Term Project Teams")
    assert len(groups) == 2
    groups = client.get_groups_by_groupset_name("0", "Homework 1")
    assert groups is None
