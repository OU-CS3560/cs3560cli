"""Authentication related commands."""

import shutil

import click
from rich import print

from ..config import Config, pass_config


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
def auth() -> None:
    """Authentication related commands."""
    pass


@auth.command(name="status")
@pass_config
def get_auth_status(
    config: Config,
) -> None:
    click.echo(f"auth.yaml file location: {config.auth_file!s}")

    masked_value = "****" if len(config.github_token.strip()) != 0 else "N/A"
    click.echo(f"GitHub Personal Access Token: {masked_value}")

    masked_value = "****" if len(config.canvas_token.strip()) != 0 else "N/A"
    click.echo(f"Canvas Token: {masked_value}")

    masked_value = "****" if len(config.redis_uri.strip()) != 0 else "N/A"
    click.echo(f"Redis URI: {masked_value}")


@auth.command(name="github")
@pass_config
def update_github_token(
    config: Config,
) -> None:
    if len(config.github_token.strip()) != 0:
        click.confirm(
            "Token already exists for GitHub, do you want to replace it?", abort=True
        )

    print(
        "Please visit https://github.com/settings/tokens and create a personal access token with at least "
        "[bold blue]repo[/] and [bold blue]org:admin[/] permission. If your organization is using SSO-SAML, your token must also be "
        "SSO-SAML authorized for that organization as well.\n"
    )
    token = click.prompt("GitHub Personal Access Token", hide_input=True)
    config.github_token = token
    config.save()


@auth.command(name="canvas")
@pass_config
def update_canvas_token(
    config: Config,
) -> None:
    if len(config.canvas_token.strip()) != 0:
        click.confirm(
            "Token already exists for Canvas, do you want to replace it?", abort=True
        )

    click.echo(
        "A Canvas access token which can be obtained from the 'Approved Integrations' section on https://ohio.instructure.com/profile/settings page.\n"
    )
    token = click.prompt("Canvas Token", hide_input=True)
    config.canvas_token = token
    config.save()


@auth.command(name="redis")
@pass_config
def update_redis_uri(
    config: Config,
) -> None:
    if len(config.redis_uri.strip()) != 0:
        click.confirm(
            "URI for Redis connection already exists, do you want to replace it?",
            abort=True,
        )

    uri = click.prompt("Redis URI", hide_input=True)
    config.redis_uri = uri
    config.save()
