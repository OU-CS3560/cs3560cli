import click

from .commands.check_username import check_username
from .commands.create_gitignore import create_gitignore
from .commands.highlight import highlight
from .commands.watch_zip import watch_zip


@click.group()
def cli():
    pass


cli.add_command(check_username)
cli.add_command(watch_zip)
cli.add_command(create_gitignore)
cli.add_command(highlight)

if __name__ == "__main__":
    cli()
