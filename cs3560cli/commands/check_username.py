"""Username Existance Checker.

Can be used to check if student's username exist on
- gh: for GitHub profile page
- cw: for Codewars profile page

This reduce the problem where student submit invalid username.
Or when the metadata was recorded incorrectly.
"""

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
        pbar.set_description("Checking %s" % username)
        response = requests.get(url_template.format(username=username))
        if response.status_code != 200:
            tqdm.write(f"got {response.status_code} for {username}")

        sleep(WAIT_BEFORE_NEXT_REQUEST)


@click.command(name="check-username")
@click.argument("filepath", type=click.Path(exists=True, readable=True))
@click.option(
    "-s",
    "--site",
    default="gh",
    show_default=True,
    type=click.Choice(("gh", "cw")),
    help="Which website the username should be checked on (gh for GitHub, cw for Codewars)",
)
def check_username(filepath, site):
    """
    Username Existance Checker.

    \b
    Can be used to check if student's username exist on
    - gh: for GitHub profile page
    - cw: for Codewars profile page

    This reduce the problem where student submit invalid username.
    Or when the metadata was recorded incorrectly.
    """
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    if filepath.exists() and filepath.is_file():
        with open(filepath, "r") as f:
            lines = f.readlines()
            usernames = [line.strip() for line in lines]

            if site == "gh":
                print("Checking GitHub Profiles")
                check_url(GITHUB_PROFILE_URL_TEMPLATE, usernames)
            elif site == "cw":
                print("Checking Codewars Profiles")
                check_url(CODEWARS_PROFILE_URL_TEMPLATE, usernames)
    else:
        print(f"[error]: cannot open file '{str(filepath)}'")


if __name__ == "__main__":
    check_username()
