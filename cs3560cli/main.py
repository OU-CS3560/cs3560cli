import click

from .commands.check_username import check_username
from .commands.create_gitignore import create_gitignore
from .commands.highlight import highlight
from .commands.watch_zip import watch_zip

from .commands.blackboard import blackboard


@click.group()
def cli():
    pass


cli.add_command(blackboard)
cli.add_command(check_username)
cli.add_command(watch_zip)
cli.add_command(create_gitignore)
cli.add_command(highlight)

@cli.command(name="help")
@click.pass_context
def show_help(ctx):
    """Show this help messages."""
    click.echo(cli.get_help(ctx))

if __name__ == "__main__":
    cli()
