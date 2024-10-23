"""
Authentication context.
"""

import os
from pathlib import Path

import click
from ruamel.yaml import YAML


class Config:
    def __init__(self, config_dir: Path | str | None = None) -> None:
        self.github_token = ""
        self.canvas_token = ""
        self.redis_uri = ""

        if config_dir is None:
            self.config_dir = Path.home() / ".config" / "cs3560cli"
            user_config_home = os.environ.get("XDG_CONFIG_HOME", None)

            if user_config_home is not None:
                # If XDG_CONFIG_HOME is presence, we will obey it, but
                # most likely only linux will have this variable.
                self.config_dir = Path(user_config_home) / "cs3560cli"
        elif isinstance(config_dir, str):
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = config_dir

        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.auth_file = self.config_dir / "auth.yaml"
        if self.auth_file.exists():
            self.restore()
        else:
            # save the empty tokens.
            self.save()

    def has_github_token(self) -> bool:
        return len(self.github_token) != 0

    def has_canvas_token(self) -> bool:
        return len(self.canvas_token) != 0

    def has_redis_uri(self) -> bool:
        return len(self.redis_uri) != 0

    def restore(self) -> None:
        yaml = YAML(typ="safe")
        doc = yaml.load(self.auth_file)

        self.github_token = doc["auths"]["github"]["token"]
        self.canvas_token = doc["auths"]["canvas"]["token"]
        self.redis_uri = doc["auths"]["redis"]["uri"]

    def save(self) -> None:
        yaml = YAML(typ="safe")
        data = {
            "auths": {
                "github": {"token": self.github_token},
                "canvas": {"token": self.canvas_token},
                "redis": {"uri": self.redis_uri},
            }
        }
        yaml.dump(data, self.auth_file)


pass_config = click.make_pass_decorator(Config, ensure=True)
