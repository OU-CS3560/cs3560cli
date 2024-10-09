import typing as ty

import pytest
import requests

from cs3560cli.services.github import GitHubApi, is_team_path


class MockSuccessfulGetTeamIdResponse:
    @property
    def status_code(self) -> int:
        return 200

    @staticmethod
    def json() -> dict[str, ty.Any]:
        return {"id": 1000}


class MockSuccessfulInviteResponse:
    @property
    def status_code(self) -> int:
        return 201

    @staticmethod
    def json() -> dict[str, ty.Any]:
        return {}


def test_is_team_path() -> None:
    assert is_team_path("A/B")
    assert not is_team_path("A B")


def test_githubapi_get_team_id_from_slug(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(*args, **kwargs):  # type: ignore
        return MockSuccessfulGetTeamIdResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    client = GitHubApi(token="fake-token")
    assert client.get_team_id_from_slug("OU-CS3560", "entire-class-20f") == 1000


def test_githubapi_get_team_id_from_team_path(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(*args, **kwargs):  # type: ignore
        return MockSuccessfulGetTeamIdResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    client = GitHubApi(token="fake-token")
    assert client.get_team_id_from_team_path("OU-CS3560/entire-class-20f") == 1000
    with pytest.raises(ValueError):
        client.get_team_id_from_team_path("OU-CS3560 entire-class-20f")


def test_githubapi_invite_to_org(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(*args, **kwargs):  # type: ignore
        return MockSuccessfulInviteResponse()

    monkeypatch.setattr(requests, "post", mock_post)

    client = GitHubApi(token="fake-token")
    assert client.invite_to_org("OU-CS3560", 3000, "rb000000@ohio.edu")
