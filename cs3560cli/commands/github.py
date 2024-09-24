"""
The github subcommand.
"""

import sys
from pathlib import Path

import click

from cs3560cli.github import GitHubApi
from cs3560cli.lms.canvas import CanvasApi


@click.group()
def github() -> None:
    """GitHub related tools."""
    pass


@github.command(name="get-team-id")
@click.argument("org_name")
@click.argument("team_slug")
@click.option(
    "--token",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="A personal access token with the 'admin:org' permission. If your organization is using SSO-SAML, "
    "your token must also be SSO-SAML authorized for that organization as well.",
)
@click.pass_context
def get_team_id_command(
    ctx: click.Context, org_name: str, team_slug: str, token: str
) -> int:
    """Get team's ID from its slug."""
    gh = GitHubApi(token=token)
    try:
        team_id = gh.get_team_id_from_slug(org_name, team_slug)
        if team_id is not None:
            click.echo(f"{org_name}/{team_slug} ID = {team_id}")
            return team_id
        else:
            click.echo(
                f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. Please make sure the team name is correct."
            )
            ctx.exit(1)
    except PermissionError:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
        ctx.exit(1)


@github.command(name="bulk-invite")
@click.argument("org_name")
@click.argument("team_slug")
@click.argument("email_address_filepath")
@click.option(
    "--gh-token",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
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
def bulk_invite_command(
    ctx: click.Context,
    org_name: str,
    team_slug: str,
    email_address_filepath: Path | str,
    gh_token: str,
    delay: float,
) -> None:
    """
    Invite multiple email addresses to the organization.

    Example Usages:

    1) Pass in the email address via stdin.

        \b
        $ cs3560cli github bulk-invite --token OU-CS3560 entire-class-24f -
        Token: <enter your GitHub personal acces token with appropriate permission and SSO-SAML enabled>
        bobcat@ohio.edu
    """
    gh = GitHubApi(token=gh_token)

    try:
        team_id = gh.get_team_id_from_slug(org_name, team_slug)
        if team_id is None:
            click.echo(
                f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. Please make sure the team name is correct."
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

        failed_email_addresses = gh.bulk_invite_to_org(
            org_name, team_id, email_addresses, delay_between_request=delay
        )
        for email_address in failed_email_addresses:
            print(f"Failed to invite {email_address}")

    except PermissionError:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )


@github.command(name="bulk-invite-from-canvas")
@click.argument("course_id")
@click.argument("org_name")
@click.argument("team_slug")
@click.option(
    "--canvas-token",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="A Canvas access token which can be obtained from the 'Approved Integrations' section on https://ohio.instructure.com/profile/settings page.",
)
@click.option(
    "--gh-token",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
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
    org_name: str,
    team_slug: str,
    canvas_token: str,
    gh_token: str,
    delay: float,
) -> None:
    """
    Invite multiple email addresses to the organization.

    Example Usages:

    1) Send invitation to join OU-CS3560/entire-class-24f team to all students in a Canvas' course with ID 24840.

        \b
        $ cs3560cli github bulk-invite-from-canvas --token 24840 OU-CS3560 entire-class-24f
        Canvas Token: <enter your Canvas' access token>
        Gh Token: <enter your GitHub personal acces token with appropriate permission and SSO-SAML enabled>
    """
    canvas = CanvasApi(token=canvas_token)
    students = canvas.get_students(course_id)
    if students is None:
        click.echo("[error]: Cannot retrive student list from Canvas.")
        ctx.exit(1)
    email_addresses = [s["user"]["email"] for s in students]
    click.echo(f"Found {len(email_addresses)} students in course id={course_id}.")

    gh = GitHubApi(token=gh_token)

    try:
        team_id = gh.get_team_id_from_slug(org_name, team_slug)
        if team_id is None:
            click.echo(
                f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. Please make sure the team name is correct."
            )
            ctx.exit(1)

        click.echo(
            f"Sending invitations to join {org_name}/{team_slug} (team_id={team_id}) ..."
        )
        failed_email_addresses = gh.bulk_invite_to_org(
            org_name, team_id, email_addresses, delay_between_request=delay
        )
        for email_address in failed_email_addresses:
            print(f"Failed to invite {email_address}")

    except PermissionError:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
