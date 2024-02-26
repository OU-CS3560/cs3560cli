from typing import Optional

import requests


class GitHubApi:

    def __init__(self, token: str):
        self._token = token

    def get_team_id_from_slug(self, org_name: str, team_slug: str) -> Optional[int]:
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
            data = res.json()
            return data["id"]
        return None

    def invite_to_org(self, org_name: str, email_address: str, team_id: int) -> bool:
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
            data=payload,
        )
        if res.status_code == 201:
            return True
        else:
            return False

    def bulk_invite_to_org(
        self, org_name: str, email_addresses: list[str]
    ) -> list[str]:
        """Sending invitation to multiple email addresses.

        Return the list of failed email addresses.
        """
        pass
