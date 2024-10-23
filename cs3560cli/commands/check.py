"""Username Existence Checker.

Can be used to check if student's username exist on
- gh: for GitHub profile page
- cw: for Codewars profile page

This reduce the problem where student submit invalid username.
Or when the metadata was recorded incorrectly.
"""

import shutil
from pathlib import Path
from time import sleep

import click
import requests
from tqdm import tqdm

GITHUB_PROFILE_URL_TEMPLATE = "https://github.com/{username}"
CODEWARS_PROFILE_URL_TEMPLATE = "https://www.codewars.com/users/{username}"
WAIT_BEFORE_NEXT_REQUEST = 3  # [s]; delay a bit so we are not DOS the website.


def check_url(url_template: str, usernames: list[str]) -> None:
    pbar = tqdm(usernames)
    for username in pbar:
        pbar.set_description(f"Checking {username}")
        response = requests.get(url_template.format(username=username))
        if response.status_code != 200:
            tqdm.write(f"got {response.status_code} for {username}")

        sleep(WAIT_BEFORE_NEXT_REQUEST)


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
def check() -> None:
    """Check various data."""
    pass


@check.command(name="github-username")
@click.argument("username", type=str)
@click.pass_context
def check_github_username(ctx: click.Context, username: str) -> None:
    """
    Check if a given GitHub's USERNAME exist or not.

    This reduces the problem where student submit invalid username or when
    the metadata was recorded incorrectly.

    1) Check a username.

        \b
        $ cs3560cli check githuh-username krerkkiat

    2) Check usernames in a file (one username on each line).

        \b
        $ cs3560cli check githuh-username @usernames.txt
    """
    if len(username) != 0 and username[0] == "@":
        filepath = Path(username[1:])

        if not filepath.exists():
            print(f"[red]'{filepath!s}' does not exist.")
            ctx.exit(1)

        usernames = []
        with open(filepath) as f:
            lines = f.readlines()
            usernames = [line.strip() for line in lines]
    else:
        usernames = [username]

    check_url(GITHUB_PROFILE_URL_TEMPLATE, usernames)


@check.command(name="codewars-username")
@click.argument("username", type=str)
@click.pass_context
def check_codewars_username(ctx: click.Context, username: str) -> None:
    """
    Check if a given Codewars' USERNAME exist or not.

    This reduces the problem where student submit invalid username or when
    the metadata was recorded incorrectly.

    1) Check a username.

        \b
        $ cs3560cli check codewars-username krerkkiatc

    2) Check usernames in a file (one username on each line).

        \b
        $ cs3560cli check codewars-username @usernames.txt
    """
    if len(username) != 0 and username[0] == "@":
        filepath = Path(username[1:])

        if not filepath.exists():
            print(f"[red]'{filepath!s}' does not exist.")
            ctx.exit(1)

        usernames = []
        with open(filepath) as f:
            lines = f.readlines()
            usernames = [line.strip() for line in lines]
    else:
        usernames = [username]

    check_url(CODEWARS_PROFILE_URL_TEMPLATE, usernames)
