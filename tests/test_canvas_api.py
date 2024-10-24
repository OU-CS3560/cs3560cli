import pytest
import requests

from cs3560cli.services.canvas import CanvasApi, parse_url_for_course_id

from .mocks import (
    MockSuccessfulGroupSetResponse,
    MockSuccessfulListSubmissionsResponse,
    MockSuccessfulListUsersResponse,
)


def test_parse_url_for_course_id() -> None:
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


def test_get_users_and_students(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(*args, **kwargs):  # type: ignore
        return MockSuccessfulListUsersResponse()

    monkeypatch.setattr(requests, "request", mock_post)

    client = CanvasApi(token="fake-token")

    users = client.get_users("0")
    assert users is not None
    assert len(users) == 5

    students = client.get_students("0")
    assert students is not None
    assert len(students) == 2  # Test student is removed.


def test_get_submissions(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(*args, **kwargs):  # type: ignore
        return MockSuccessfulListSubmissionsResponse()

    monkeypatch.setattr(requests, "request", mock_post)

    client = CanvasApi(token="fake-token")

    submissions = client.get_submissions("0")
    assert submissions is not None
    assert len(submissions) == 3


def test_get_groups_by_groupset_name(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(*args, **kwargs):  # type: ignore
        return MockSuccessfulGroupSetResponse()

    monkeypatch.setattr(requests, "request", mock_post)

    client = CanvasApi(token="fake-token")

    groups = client.get_groups_by_groupset_name("0", "Term Project Teams")
    assert groups is not None
    assert len(groups) == 2
    groups = client.get_groups_by_groupset_name("0", "Homework 1")
    assert groups is None
    groups = client.get_groups_by_groupset_name("0", "Term Project Teams")
    assert groups is not None
    assert len(groups) == 2
    groups = client.get_groups_by_groupset_name("0", "Homework 1")
    assert groups is None
    assert groups is None
