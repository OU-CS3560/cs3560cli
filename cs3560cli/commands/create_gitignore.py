"""
Add .gitignore file (replace if any exist!).

Instead of adding just the language/platform specific .gitignore
from https://github.com/github/gitignore, it will also 
add all OS dependent .gitignore as well.
"""

import traceback
from pathlib import Path
from typing import Optional

import click
import requests

# TODO: add more mappings.
path_mapping = {
    "windows": "Global/Windows.gitignore",
    "macos": "Global/macOS.gitignore",
    "vscode": "Global/VisualStudioCode.gitignore",
    "python": "Python.gitignore",
    "cpp": "C++.gitignore",
    "node": "Node.gitignore",
    "unity": "Unity.gitignore",
    "rust": "Rust.gitignore",
}

aliases = {
    "c++": "cpp",
    "js": "node",
    "VisualStudioCode": "vscode",
}


class ApiError(Exception):
    pass


def get_path(name: str) -> Optional[str]:
    """Lookup the path.

    Assume name is in lowercase and is not an alias.
    """
    if name not in path_mapping.keys():
        return None

    return path_mapping[name]


def normalize(name: str) -> str:
    """Apply alias and lower the case the name."""
    name = name.lower()

    if name in aliases.keys():
        name = aliases[name]

    return name


def get_content(
    names: list[str],
    bases: list[str] = ["windows", "macos"],
    root: str = "https://raw.githubusercontent.com/github/gitignore/main/",
    header_text_template: str = "#\n# {path}\n# Get the latest version at https://github.com/github/gitignore/{path}\n#\n",
) -> str:
    """Create .gitignore content from list of names.

    Assume that names in bases area already normalized.
    """
    final_text = ""

    names = bases + [normalize(name) for name in names if normalize(name) not in bases]

    for name in names:
        if name is None:
            continue
        path = get_path(name)
        if path is None:
            continue
        try:
            res = requests.get(root + path)
            if res.status_code == 200:
                header_text = header_text_template.format(path=path)
                final_text += header_text
                final_text += res.text + "\n"
            else:
                raise ApiError(
                    f"status code from API is not as expected. Expect 200 but get {res.status_code}"
                )
        except requests.exceptions.RequestException:
            raise ApiError("error occur when fetching content")
    return final_text


@click.command("create-gitignore")
@click.argument("names", type=str, nargs=-1)
@click.option("--root", type=click.Path(exists=True), default=".")
@click.option("--base", type=str, multiple=True, default=["windows", "macos"])
@click.pass_context
def create_gitignore(
    ctx,
    names: list[str],
    root: str | Path = ".",
    base: list[str] = ["windows", "macos"],
) -> None:
    """Create .gitignore content from list of names.

    Assume that names in bases area already normalized.
    """
    if isinstance(root, str):
        root = Path(root)
    if isinstance(names, tuple):
        names = list(names)
    if isinstance(base, tuple):
        base = list(base)
    try:
        content = get_content(names, base)
    except ConnectionError as e:
        ctx.fail("network error occured", e)
    except ApiError as e:
        ctx.fail("api error occured", e)

    outfile_path = root / ".gitignore"
    if outfile_path.exists():
        ans = click.confirm(f"'{str(outfile_path)}' already exist, overwrite?")
        if not ans:
            click.echo(f"'{str(outfile_path)}' is not modified")
            ctx.exit()

    with open(outfile_path, "w") as out_f:
        out_f.write(content)


if __name__ == "__main__":
    create_gitignore()
