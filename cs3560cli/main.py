import click

from .functions.check_username import check_username
from .functions.watch_zip import watch_zip
from .functions.create_gitignore import create_gitignore
from .functions.highlight import highlight

@click.group()
def cli():
    pass

cli.add_command(check_username)
cli.add_command(watch_zip)
cli.add_command(create_gitignore)
cli.add_command(highlight)

if __name__ == "__main__":
    cli()