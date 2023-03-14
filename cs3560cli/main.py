import click

from .functions.check_username import check_username
from .functions.watch_zip import watch_zip

@click.group()
def cli():
    pass

cli.add_command(check_username)
cli.add_command(watch_zip)

if __name__ == "__main__":
    cli()