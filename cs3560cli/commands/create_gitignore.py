"""
Add .gitignore file (replace if any exist!).

Instead of adding just the language/platform specific .gitignore
from https://github.com/github/gitignore, it will also
add all OS dependent .gitignore as well.
"""

from pathlib import Path

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


def get_path(name: str) -> str | None:
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
    bases: list[str] | None = None,
    root: str = "https://raw.githubusercontent.com/github/gitignore/main/",
    header_text_template: str = "#\n# {path}\n# Get the latest version at https://github.com/github/gitignore/{path}\n#\n",
) -> str:
    """Create .gitignore content from list of names.

    Assume that names in bases area already normalized.
    """
    if bases is None:
        bases = ["windows", "macos"]

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
        except requests.exceptions.RequestException as e:
            raise ApiError("error occur when fetching content") from e
    return final_text


@click.command("create-gitignore")
@click.argument("names", type=str, nargs=-1)
@click.option("--root", type=click.Path(exists=True), default=".")
@click.option("--base", type=str, multiple=True, default=("windows", "macos"))
@click.pass_context
def create_gitignore(
    ctx: click.Context,
    names: list[str],
    root: str | Path = ".",
    base: list[str] | tuple[str, ...] = ("windows", "macos"),
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
        ctx.fail(f"network error occured\n{e}")
    except ApiError as e:
        ctx.fail(f"api error occured\n{e}")

    outfile_path = root / ".gitignore"
    if outfile_path.exists():
        ans = click.confirm(f"'{outfile_path!s}' already exist, overwrite?")
        if not ans:
            click.echo(f"'{outfile_path!s}' is not modified")
            ctx.exit()

    with open(outfile_path, "w") as out_f:
        out_f.write(content)


if __name__ == "__main__":
    create_gitignore()
