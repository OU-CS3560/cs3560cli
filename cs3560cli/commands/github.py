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
@click.pass_context
def get_team_id_command(ctx, org_name, team_slug, token):
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
        ctx.exit(1)


@github.command(name="bulk-invite")
@click.argument("org_name")
@click.argument("team_slug")
@click.argument("email_address_file")
@click.option(
    "--token",
    default=None,
    help="A personal access token with 'admin:org' permission. If your organization is using SSO-SAML, "
    "your token must also be authorized for that organization as well. If this option is not given, "
    "the program will ask for it before the operation.",
)
@click.pass_context
def bulk_invite_command(ctx, org_name, team_slug, email_address_file, token):
    """
    Invite multiple email addresses to the organization.

    Example Usages:

    1) Pass in the email address via stdin.

        \b
        $ cs3560cli github bulk-invite OU-CS3560 entire-class-24f -
    """
    if token is None:
        token = getpass.getpass(
            "Personal Access Token (with 'admin:org' permission, and is authorized for SSO-SAML if the organization is using it): "
        )

    gh = GitHubApi(token=token)

    team_id = gh.get_team_id_from_slug(org_name, team_slug)
    if team_id is None:
        click.echo(
            f"[error]: Cannot retrieve the team's ID for '{org_name}/{team_slug}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
        ctx.exit(1)

    if email_address_file == "-":
        # Read in from the stdin.
        pass
    else:
        # Read in from a file.
        pass
