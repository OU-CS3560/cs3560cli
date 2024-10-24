import typing as ty

import pytest

from cs3560cli.config import Config


@pytest.fixture
def config_home_with_fake_tokens(tmp_path):
    config_home = tmp_path / ".config"
    config_home.mkdir()

    config_dir = config_home / "cs3560cli"
    config_dir.mkdir()

    config = Config(config_dir=config_dir)
    config.github_token = "fake-token"
    config.canvas_token = "fake-token"
    config.save()

    return config_home


class MockSuccessfulListUsersResponse:
    @property
    def status_code(self) -> int:
        return 200

    @staticmethod
    def json() -> dict[str, ty.Any]:
        return {
            "data": {
                "course": {
                    "_id": "20001",
                    "enrollmentsConnection": {
                        "nodes": [
                            {
                                "user": {
                                    "_id": "5000",
                                    "email": "st000001@ohio.edu",
                                    "name": "Student 1",
                                },
                                "sisRole": "student",
                            },
                            {
                                "user": {
                                    "_id": "5001",
                                    "email": "st000002@ohio.edu",
                                    "name": "Student 2",
                                },
                                "sisRole": "student",
                            },
                            {
                                "user": {
                                    "_id": "5002",
                                    "email": None,
                                    "name": "Test Student",
                                },
                                "sisRole": "student",
                            },
                            {
                                "user": {
                                    "_id": "100",
                                    "email": "bobcatr@ohio.edu",
                                    "name": "Rufus Bobcat",
                                },
                                "sisRole": "teacher",
                            },
                            {
                                "user": {
                                    "_id": "5003",
                                    "email": "kc000000@ohio.edu",
                                    "name": "Krerkkiat Chusap",
                                },
                                "sisRole": "ta",
                            },
                        ]
                    },
                }
            }
        }


class MockSuccessfulListSubmissionsResponse:
    @property
    def status_code(self) -> int:
        return 200

    @staticmethod
    def json() -> dict[str, ty.Any]:
        return {
            "data": {
                "assignment": {
                    "submissionsConnection": {
                        "nodes": [
                            {
                                "_id": "0",
                                "submissionStatus": "submitted",
                                "url": "https://github.com/OU-CS3560/hw-make-rb000000",
                                "user": {"email": "rb000000@ohio.edu"},
                                "commentsConnection": {"nodes": []},
                            },
                            {
                                "_id": "1",
                                "submissionStatus": "submitted",
                                "url": "https://github.com/OU-CS3560/hw-make-rb000000.git",
                                "user": {"email": "rb000001@ohio.edu"},
                                "commentsConnection": {"nodes": []},
                            },
                            {
                                "_id": "2",
                                "submissionStatus": "submitted",
                                "url": "https://github.com/OU-CS3560/hw-make-rb000000?tab=readme-ov-file",
                                "user": {"email": "rb000002@ohio.edu"},
                                "commentsConnection": {
                                    "nodes": [
                                        {
                                            "_id": "3",
                                            "comment": "I am surprised that the project's detail is not on NDA.",
                                            "author": {"email": "bobcat@ohio.edu"},
                                        }
                                    ]
                                },
                            },
                        ]
                    }
                }
            }
        }


class MockSuccessfulGroupSetResponse:
    @property
    def status_code(self) -> int:
        return 200

    @staticmethod
    def json() -> dict[str, ty.Any]:
        return {
            "data": {
                "course": {
                    "groupSetsConnection": {
                        "nodes": [
                            {
                                "name": "Term Project Teams",
                                "groupsConnection": {
                                    "nodes": [
                                        {
                                            "name": "test-team-1",
                                            "membersConnection": {
                                                "nodes": [
                                                    {
                                                        "user": {
                                                            "email": "rb000000@ohio.edu",
                                                            "name": "Rufus Bobcat1",
                                                        }
                                                    },
                                                    {
                                                        "user": {
                                                            "email": "rb000001@ohio.edu",
                                                            "name": "Rufus Bobcat2",
                                                        }
                                                    },
                                                ]
                                            },
                                        },
                                        {
                                            "name": "test-team-2",
                                            "membersConnection": {
                                                "nodes": [
                                                    {
                                                        "user": {
                                                            "email": "rb000002@ohio.edu",
                                                            "name": "Rufus Bobcat2",
                                                        }
                                                    },
                                                    {
                                                        "user": {
                                                            "email": "rb000003@ohio.edu",
                                                            "name": "Rufus Bobcat4",
                                                        }
                                                    },
                                                ]
                                            },
                                        },
                                    ]
                                },
                            }
                        ]
                    }
                }
            }
        }
