"""
The github subcommand.
"""

import shutil
import sys
from pathlib import Path

import click

from cs3560cli.github import GitHubApi, is_team_path
from cs3560cli.lms.canvas import CanvasApi


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
def github() -> None:
    """GitHub related tools."""
    pass


@github.command(name="get-team-id")
@click.argument(
    "team_path",
)
@click.option(
    "--with-token",
    "gh_token",
    default=None,
    help="A personal access token with the 'admin:org' permission. If your organization is using SSO-SAML, "
    "your token must also be SSO-SAML authorized for that organization as well.",
)
@click.pass_context
def get_team_id_command(
    ctx: click.Context, team_path: str, gh_token: str | None
) -> int:
    """Get team's ID from its TEAM_PATH.

    TEAM_PATH must be in '<org-name>/<team-name>' format."""
    gh = GitHubApi(token=gh_token)

    if not is_team_path(team_path):
        click.echo(
            f"[error]: '{team_path}' is not in the required format, '<org-name>/<team-name>'."
        )

    try:
        team_id = gh.get_team_id_from_team_path(team_path)
        if team_id is not None:
            click.echo(f"{team_id}")
            return team_id
        else:
            click.echo(
                f"[error]: Cannot retrieve the team's ID for '{team_path}'. Please make sure the team name is correct."
            )
            ctx.exit(1)
    except PermissionError:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{team_path}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
        ctx.exit(1)


@github.command(name="bulk-invite")
@click.argument("team_path")
@click.argument("email_address_filepath")
@click.option(
    "--with-token",
    "gh_token",
    default=None,
    help="A personal access token with the 'admin:org' permission. If your organization is using SSO-SAML, "
    "your token must also be SSO-SAML authorized for that organization as well.",
)
@click.option(
    "--delay",
    type=float,
    default=1.0,
    help="A delay in second between invitation request.",
)
@click.pass_context
def bulk_invite_command(
    ctx: click.Context,
    team_path: str,
    email_address_filepath: Path | str,
    gh_token: str,
    delay: float,
) -> None:
    """
    Invite multiple email addresses to the TEAM_PATH of the organization.

    Example Usages:

    1) Pass in the email address via stdin.

        \b
        $ cs3560cli github bulk-invite --with-token gh_fake-token OU-CS3560 entire-class-24f -
        bobcat@ohio.edu

    2) Use environment variable GH_TOKEN to specify an access token for GitHub.
        \b
        $ export GH_TOKEN="gh_fake-token"
        $ cs3560cli github bulk-invite OU-CS3560 entire-class-24f -
        bobcat@ohio.edu
    """
    gh = GitHubApi(token=gh_token)

    if not is_team_path(team_path):
        click.echo(
            f"[error]: '{team_path}' is not in the required format, '<org-name>/<team-name>'."
        )

    try:
        team_id = gh.get_team_id_from_team_path(team_path)
        if team_id is None:
            click.echo(
                f"[error]: Cannot retrieve the team's ID for '{team_path}'. Please make sure the team name is correct."
            )
            ctx.exit(1)

        if isinstance(email_address_filepath, str) and email_address_filepath == "-":
            # Read in from the stdin.
            file_obj = sys.stdin
        else:
            file_obj = open(email_address_filepath)

        email_addresses = []
        for line in file_obj:
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            email_addresses.append(line)

        if email_address_filepath != "-":
            file_obj.close()

        org_name, _ = team_path.split("/")

        failed_email_addresses = gh.bulk_invite_to_org(
            org_name, team_id, email_addresses, delay_between_request=delay
        )
        for email_address in failed_email_addresses:
            print(f"Failed to invite {email_address}")

    except PermissionError:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{team_path}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )


@github.command(name="bulk-invite-from-canvas")
@click.argument("course_id")
@click.argument("team_path")
@click.option(
    "--with-canvas-token",
    "canvas_token",
    help="A Canvas access token which can be obtained from the 'Approved Integrations' section on https://ohio.instructure.com/profile/settings page.",
)
@click.option(
    "--with-github-token",
    "github_token",
    default=None,
    help="A personal access token with the 'admin:org' permission. If your organization is using SSO-SAML, "
    "your token must also be SSO-SAML authorized for that organization as well.",
)
@click.option(
    "--delay",
    type=float,
    default=1,
    help="A delay in second between invitation request.",
)
@click.pass_context
def bulk_invite_from_canvas_command(
    ctx: click.Context,
    course_id: str,
    team_path: str,
    canvas_token: str,
    github_token: str,
    delay: float,
) -> None:
    """
    Invite students from Canvas to a team in GitHub Organization.

    Example Usages:

    1) Send invitation to join OU-CS3560/entire-class-24f team to all students in a Canvas' course with ID 24840.

        \b
        $ cs3560cli github bulk-invite-from-canvas 24840 OU-CS3560/entire-class-24f --with-canvas-token fake-token --with-github-token gh_fake-token
    """
    if not is_team_path(team_path):
        click.echo(
            f"[error]: '{team_path}' is not in the required format, '<org-name>/<team-name>'."
        )

    canvas = CanvasApi(token=canvas_token)
    students = canvas.get_students(course_id)
    if students is None:
        click.echo("[error]: Cannot retrive student list from Canvas.")
        ctx.exit(1)
    email_addresses = [s["user"]["email"] for s in students]
    click.echo(f"Found {len(email_addresses)} students in course id={course_id}.")

    gh = GitHubApi(token=github_token)

    try:
        team_id = gh.get_team_id_from_team_path(team_path)
        if team_id is None:
            click.echo(
                f"[error]: Cannot retrieve the team's ID for '{team_path}'. Please make sure the team name is correct."
            )
            ctx.exit(1)

        click.echo(f"Sending invitations to join {team_path} (team_id={team_id}) ...")

        org_name, _ = team_path.split("/")
        failed_email_addresses = gh.bulk_invite_to_org(
            org_name, team_id, email_addresses, delay_between_request=delay
        )
        for email_address in failed_email_addresses:
            print(f"Failed to invite {email_address}")

    except PermissionError:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{team_path}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
