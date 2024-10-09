"""Get related commands."""

import shutil

import click
from rich import print

from ..config import Config, pass_config
from ..services.github import GitHubApi, is_team_path
from .auth import update_github_token


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
def get() -> None:
    """Get or obtain various data."""
    pass


@get.command(name="team-id")
@click.argument(
    "team_path",
)
@pass_config
@click.pass_context
def get_team_id_command(
    ctx: click.Context,
    config: Config,
    team_path: str,
) -> int:
    """Get GitHub team's ID from its TEAM_PATH.

    TEAM_PATH must be in '<org-name>/<team-name>' format."""
    if not config.has_github_token():
        ctx.invoke(update_github_token)

    gh = GitHubApi(token=config.github_token)

    if not is_team_path(team_path):
        print(
            f"[red]'{team_path}' is not in the required format, '<org-name>/<team-name>'."
        )

    try:
        team_id = gh.get_team_id_from_team_path(team_path)
        if team_id is not None:
            click.echo(f"{team_id}")
            return team_id
        else:
            print(
                f"[red]'{team_path}' is not in the required format, '<org-name>/<team-name>'."
            )
            ctx.exit(1)
    except PermissionError:
        print(
            f"[red]Cannot retrieve the team's ID for '{team_path}'. "
            "Please make sure that the token has at least 'admin:org' permission and it is authorized with SAML SSO."
        )
        ctx.exit(1)
