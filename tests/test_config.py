import pytest

from cs3560cli.config import Config


def test_config_home_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    config_home = tmp_path / ".config"
    config_home.mkdir()

    # This forces win32 and darwin to have XDG_CONFIG_HOME.
    # which does not properly reflect the real-world condition.
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

    _ = Config()
    assert (config_home / "cs3560cli" / "auth.yaml").exists()


def test_config_home_arg(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    _ = Config(config_dir=dir1)
    assert (dir1 / "auth.yaml").exists()

    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    _ = Config(config_dir=str(dir2))
    assert (dir2 / "auth.yaml").exists()


def test_config_default(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    config_home = tmp_path / ".config"
    config_home.mkdir()

    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

    c = Config()
    assert c.has_canvas_token() is False
    assert c.has_github_token() is False
    assert c.has_redis_uri() is False
