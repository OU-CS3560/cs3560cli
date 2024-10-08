import os
import subprocess
import typing as ty
from time import sleep

import requests


def is_team_path(text: str) -> bool:
    """Check if / is part of the string."""
    return "/" in text


def get_github_token_from_gh_cli() -> str | None:
    """Attempt to obtain GitHub's token from 'gh cli'."""
    try:
        output = subprocess.check_output(
            "gh auth token",
            shell=True,
        )
    except Exception:
        return None
    return output.decode().strip()


def get_github_token_from_environment_variable() -> str | None:
    """Attempt to obtain GitHub's token from GH_TOKEN environment variable."""

    return os.environ.get("GH_TOKEN", None)


def get_github_token() -> str | None:
    """Try to obtain GitHub token from various sources.

    1. An environment variable GH_TOKEN.
    2. 'gh auth token' command.
    """
    token = get_github_token_from_environment_variable()
    if token is not None:
        return token
    token = get_github_token_from_gh_cli()
    if token is not None:
        return token

    return token


class GetTeamByNameResponse(ty.TypedDict):
    id: int


class GitHubApi:
    def __init__(self, token: str):
        if token is None:
            if (token := get_github_token()) is None:
                raise ValueError(
                    "'token' is required. The value passed in is None and all other means to obtain the token have failed."
                )
        self._token = token

    def get_team_id_from_slug(self, org_name: str, team_slug: str) -> int | None:
        """
        Return the ID of the team in the organization.
        """
        headers = {
            "User-Agent": "cs3560cli",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        res = requests.get(
            f"https://api.github.com/orgs/{org_name}/teams/{team_slug}", headers=headers
        )
        if res.status_code == 200:
            data: GetTeamByNameResponse = res.json()
            return data["id"]
        elif res.status_code == 401 or res.status_code == 403:
            raise PermissionError(
                "Does not have enough permission to retrive the team's id."
            )
        elif res.status_code == 404:
            return None
        return None

    def get_team_id_from_team_path(self, team_path: str) -> int | None:
        """
        Return team ID from its path.
        """
        if not is_team_path(team_path):
            raise ValueError(
                "The 'team_path' must be in the '<org-name>/<team-name>' format."
            )

        org_name, team_slug = team_path.split("/")
        return self.get_team_id_from_slug(org_name, team_slug)

    def invite_to_org(self, org_name: str, team_id: int, email_address: str) -> bool:
        """
        Invite the user to a team in the organization.
        """
        headers = {
            "User-Agent": "cs3560cli",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        payload = {
            "email": email_address,
            "role": "direct_member",
            "team_ids": [team_id],
        }

        res = requests.post(
            f"https://api.github.com/orgs/{org_name}/invitations",
            headers=headers,
            json=payload,
        )
        if res.status_code == 201:
            return True
        else:
            return False

    def bulk_invite_to_org(
        self,
        org_name: str,
        team_id: int,
        email_addresses: list[str],
        delay_between_request: float = 1,
    ) -> list[str]:
        """Sending invitation to a team in the organization to multiple email addresses.

        Return the list of failed email addresses.
        """
        failed_invitations = []
        for email_address in email_addresses:
            if not self.invite_to_org(org_name, team_id, email_address):
                failed_invitations.append(email_address)
            sleep(delay_between_request)

        return failed_invitations
