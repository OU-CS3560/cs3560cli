from pathlib import Path

import pytest
from click.testing import CliRunner

from cs3560cli.main import cli
from cs3560cli.services.canvas import CanvasApi, User
from cs3560cli.services.github import GitHubApi

from .fixtures import config_home_with_fake_tokens  # noqa: F401


@pytest.mark.skip(reason="live data")
def test_create_gitignore_command(config_home_with_fake_tokens: Path) -> None:
    runner = CliRunner(env={"XDG_CONFIG_HOME": str(config_home_with_fake_tokens)})
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            args=[
                "create",
                "gitignore",
                "python",
            ],
        )
        # print(result.output)
        assert result.exit_code == 0
        assert not result.exception
        assert "Windows.gitignore" in result.output
        assert "macOS.gitignore" in result.output
        assert "Python.gitignore" in result.output


@pytest.mark.parametrize("style_val", ["quiz", "ios"])
def test_create_password_command(
    style_val: str, config_home_with_fake_tokens: Path
) -> None:
    runner = CliRunner(env={"XDG_CONFIG_HOME": str(config_home_with_fake_tokens)})
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            args=[
                "create",
                "password",
                "--style",
                style_val,
            ],
        )
        # print(result.output)
        assert result.exit_code == 0
        assert not result.exception
        assert "-" in result.output


@pytest.mark.parametrize(
    "course_id_val", ["0", "https://ohio.instructure.com/courses/0/"]
)
def test_create_github_invite_command(
    course_id_val: str,
    monkeypatch: pytest.MonkeyPatch,
    config_home_with_fake_tokens: Path,
) -> None:
    def mock_get_students(*args, **kwargs):  # type: ignore[no-untyped-def]
        return [User("0", "Rufus Bobcat", "br000001@ohio.edu", "student")]

    def mock_get_team_id_from_team_path(*args, **kwargs):  # type: ignore[no-untyped-def]
        return "0"

    monkeypatch.setattr(CanvasApi, "get_students", mock_get_students)
    monkeypatch.setattr(
        GitHubApi, "get_team_id_from_team_path", mock_get_team_id_from_team_path
    )

    runner = CliRunner(env={"XDG_CONFIG_HOME": str(config_home_with_fake_tokens)})
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            args=[
                "create",
                "gh-invite",
                "--dry-run",
                "--from-canvas-course",
                course_id_val,
                "ou-cs3560/entire-class-2050f",
            ],
        )
        # print(result.output)
        assert result.exit_code == 0
        assert not result.exception
        assert "Sending invitations" in result.output


def test_create_github_invite_command_invalid_team_name(
    monkeypatch: pytest.MonkeyPatch,
    config_home_with_fake_tokens: Path,
) -> None:
    def mock_get_students(*args, **kwargs):  # type: ignore[no-untyped-def]
        return [User("0", "Rufus Bobcat", "br000001@ohio.edu", "student")]

    def mock_get_team_id_from_team_path(*args, **kwargs):  # type: ignore[no-untyped-def]
        return "0"

    monkeypatch.setattr(CanvasApi, "get_students", mock_get_students)
    monkeypatch.setattr(
        GitHubApi, "get_team_id_from_team_path", mock_get_team_id_from_team_path
    )

    runner = CliRunner(env={"XDG_CONFIG_HOME": str(config_home_with_fake_tokens)})
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            args=[
                "create",
                "gh-invite",
                "--dry-run",
                "--from-canvas-course",
                "0",
                "entire-class-2050f",
            ],
        )
        assert result.exit_code == 1
        assert result.exit_code == 1
