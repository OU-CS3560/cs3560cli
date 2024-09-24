import typing as ty
from time import sleep

import requests


class GetTeamByNameResponse(ty.TypedDict):
    id: int


class GitHubApi:
    def __init__(self, token: str):
        self._token = token

    def get_team_id_from_slug(self, org_name: str, team_slug: str) -> int | None:
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
        elif res.status_code == 401:
            raise PermissionError(
                "Does not have enough permission to retrive the team's id."
            )
        elif res.status_code == 404:
            return None
        return None

    def invite_to_org(self, org_name: str, team_id: int, email_address: str) -> bool:
        """
        Invite a user to the organization.
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
        """Sending invitation to multiple email addresses.

        Return the list of failed email addresses.
        """
        failed_invitations = []
        for email_address in email_addresses:
            if not self.invite_to_org(org_name, team_id, email_address):
                failed_invitations.append(email_address)
            sleep(delay_between_request)

        return failed_invitations
