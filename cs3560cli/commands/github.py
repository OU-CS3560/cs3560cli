"""
The github subcommand.
"""

import getpass

import click

from cs3560cli.github import GitHubApi


@click.group()
def github():
    """GitHub related tools."""
    pass


@github.command(name="get-team-id")
@click.argument("org_name")
@click.argument("team_slug")
@click.option("--token", default=None)
def get_team_id_command(org_name, team_slug, token):
    """Get team's ID from its slug."""
    if token is None:
        token = getpass.getpass("Token: ")

    gh = GitHubApi(token=token)
    team_id = gh.get_team_id_from_slug(org_name, team_slug)
    if team_id is not None:
        click.echo(f"{org_name}/{team_slug} ID = {team_id}")
    else:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
        click.exit(1)


@github.command(name="bulk-invite")
@click.argument("org_name")
@click.argument("team_slug")
@click.argument("email_address_file")
@click.option("--token", default=None)
def bulk_invite_command(org_name, team_slug, email_address_file, token):
    """Invite multiple email addresses to the organization."""
    if token is None:
        token = getpass.getpass("Token: ")

    gh = GitHubApi(token=token)

    team_id = gh.get_team_id_from_slug(org_name, team_slug)
    if team_id is None:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
        click.exit(1)

    if email_address_file == "-":
        # Read in from the stdin.
        pass
    else:
        # Read in from a file.
        pass
