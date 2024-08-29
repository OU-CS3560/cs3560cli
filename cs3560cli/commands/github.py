"""
The github subcommand.
"""

import sys

import click

from cs3560cli.github import GitHubApi


@click.group()
def github():
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
def get_team_id_command(ctx, org_name, team_slug, token):
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
    type=int,
    default=1,
    help="A delay in second between invitation request.",
)
@click.pass_context
def bulk_invite_command(
    ctx, org_name, team_slug, email_address_filepath, gh_token, delay
):
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

        if email_address_filepath == "-":
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
