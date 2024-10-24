
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
