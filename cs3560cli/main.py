import shutil

import click

from . import __version__
from .commands.blackboard import blackboard
from .commands.check_username import check_username
from .commands.create_gitignore import create_gitignore
from .commands.github import github
from .commands.highlight import highlight
from .commands.watch_zip import watch_zip


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
def cli() -> None:
    pass


cli.add_command(blackboard)
cli.add_command(github)
cli.add_command(check_username)
cli.add_command(watch_zip)
cli.add_command(create_gitignore)
cli.add_command(highlight)


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
