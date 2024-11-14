import shutil

import click

from . import __version__
from .commands.auth import auth
from .commands.categorize import categorize
from .commands.check import check
from .commands.create import create
from .commands.db import db
from .commands.get import get
from .commands.highlight import highlight
from .commands.watch import watch
from .config import Config


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
@click.option("--config-dir", type=str, default=None)
@click.pass_context
def cli(ctx: click.Context, config_dir: str | None) -> None:
    """
    A set of internal tools for Ohio University's CS3560 course.
    """
    ctx.obj = Config(config_dir)


cli.add_command(auth)
cli.add_command(categorize)
cli.add_command(check)
cli.add_command(create)
cli.add_command(get)
cli.add_command(highlight)
cli.add_command(watch)
cli.add_command(db)


@cli.command(name="help")
@click.pass_context
def show_help(ctx: click.Context) -> None:
    """Show this help messages."""
    click.echo(cli.get_help(ctx))


@cli.command(name="version")
@click.pass_context
def show_version(ctx: click.Context) -> None:
    """Show version of the command."""
    click.echo(__version__)


if __name__ == "__main__":
    cli()
