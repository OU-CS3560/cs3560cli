"""
Data store for the sub-commands in db command.

Key formats:

- f"#{course_name}/students" - for a list of email handle of
  students for said course. course_name examples: '2024f', '2024s', etc.
- f"@{email_handle}/gh-username" - for a GitHub username of a student.
"""

import redis

STUDENTS_KEY_FORMAT = "#{course_name}/students"
TEAMS_KEY_FORMAT = "#{course_name}/teams"
TEAM_MEMBERS_KEY_FORMAT = "@{team_id}/members"
TEAM_PRESENTATION_KEY_FORMAT = "@{team_id}/{checkpoint_number}/presented"
TEAM_PRESENTATION_NOTE_KEY_FORMAT = "@{team_id}/{checkpoint_number}/note"
STUDENT_PRESENTATION_NOTE_KEY_FORMAT = (
    "@{team_id}/{checkpoint_number}/{email_handle}/note"
)
STUDENT_FULLNAME_KEY_FORMAT = "@{email_handle}/full-name"
GITHUB_USERNAME_KEY_FORMAT = "@{email_handle}/gh-username"


class BaseStore:
    def add_course(
        self, course_name: str, email_handles: list[str], overwrite: bool = False
    ) -> None:
        raise NotImplementedError()

    def set_student_github_username(
        self, email_handle: str, github_username: str, overwrite: bool = False
    ) -> None:
        raise NotImplementedError()

    def clear_student_github_username(self, email_handle: str) -> None:
        raise NotImplementedError()

    def get_github_username_mappings(self, course_name: str) -> list[tuple[str, str]]:
        raise NotImplementedError()


class RedisStore(BaseStore):
    """Data store service.

    Required Redis instance.
    """

    # If specify redis.Redis[bytes], mypy will be happy, but runtime error will occur.
    def __init__(self, client: redis.Redis) -> None:  # type: ignore
        self.client = client

    def add_course(
        self, course_name: str, email_handles: list[str], overwrite: bool = False
    ) -> None:
        key = STUDENTS_KEY_FORMAT.format(course_name=course_name)
        if self.client.exists(key) and not overwrite:
            raise ValueError(f"key '{key}' already exists")

        payload = ",".join(email_handles)
        self.client.set(key, value=payload)

    def set_student_github_username(
        self, email_handle: str, github_username: str, overwrite: bool = False
    ) -> None:
        key = GITHUB_USERNAME_KEY_FORMAT.format(email_handle=email_handle)
        if self.client.exists(key) and not overwrite:
            raise ValueError(f"key '{key}' already exists")
        self.client.set(key, value=github_username)

    def get_github_username_mappings(self, course_name: str) -> list[tuple[str, str]]:
        key = STUDENTS_KEY_FORMAT.format(course_name=course_name)
        if not self.client.exists(key):
            raise ValueError(f"key '{key}' does not exists")

        res = self.client.get(key)
        if res is None:
            raise ValueError(f"key '{key}' has a value of 'None'.")
        email_handles = res.decode().split(",")

        keys = [
            GITHUB_USERNAME_KEY_FORMAT.format(email_handle=email_handle.strip())
            for email_handle in email_handles
        ]
        github_usernames = self.client.mget(keys)

        mappings: list[tuple[str, str]] = []
        for email_handle, github_username in zip(
            email_handles, github_usernames, strict=True
        ):
            if github_username is None:
                continue
            mappings.append((email_handle, github_username.decode()))

        return mappings
