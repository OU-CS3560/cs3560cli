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
                "Does not have enough permission to retrieve the team's id."
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

    def create_team(
        self,
        name: str,
        org_name: str,
        description: str | None = None,
        privacy: str = "closed",
        notification_setting: str = "notifications_disabled",
        parent_team_id: int | None = None,
    ) -> bool:
        headers = {
            "User-Agent": "cs3560cli",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        payload: dict[str, str | int] = {
            "name": name,
            "privacy": privacy,
            "notification_setting": notification_setting,
        }
        if description is not None:
            payload["description"] = description
        if parent_team_id is not None:
            payload["parent_team_id"] = parent_team_id

        res = requests.post(
            f"https://api.github.com/orgs/{org_name}/teams",
            headers=headers,
            json=payload,
        )
        if res.status_code == 201:
            return True
        else:
            return False

    def add_team_to_repository(
        self, team_path: str, repo_path: str, permission: str = "maintain"
    ) -> bool:
        team_org, team_name = team_path.split("/")
        repo_owner, repo_name = repo_path.split("/")

        headers = {
            "User-Agent": "cs3560cli",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        payload = {"permission": permission}

        res = requests.put(
            f"https://api.github.com/orgs/{team_org}/teams/{team_name}/repos/{repo_owner}/{repo_name}",
            headers=headers,
            json=payload,
        )
        if res.status_code == 201:
            return True
        else:
            return False

    def create_repository_with_template(
        self,
        repo_path: str,
        template_repo_path: str,
        private: bool = True,
        description: str | None = None,
    ) -> bool:
        """
        Create a repository from a template.
        """
        repo_owner, repo_name = repo_path.split("/")
        template_repo_owner, template_repo_name = template_repo_path.split("/")

        headers = {
            "User-Agent": "cs3560cli",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        payload = {"owner": repo_owner, "name": repo_name, "private": private}
        if description is not None:
            payload["description"] = description

        res = requests.post(
            f"https://api.github.com/repos/{template_repo_owner}/{template_repo_name}/generate",
            headers=headers,
            json=payload,
        )
        if res.status_code == 201:
            return True
        else:
            return False
