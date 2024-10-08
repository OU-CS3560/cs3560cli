"""
Add .gitignore file (replace if any exist!).

Instead of adding just the language/platform specific .gitignore
from https://github.com/github/gitignore, it will also
add all OS dependent .gitignore as well.
"""

import itertools
from pathlib import Path

import click
import requests

ALIASES = {
    "windows": "Global/Windows.gitignore",
    "macos": "Global/macOS.gitignore",
    "vscode": "Global/VisualStudioCode.gitignore",
    "python": "Python.gitignore",
    "notebook": "community/Python/JupyterNotebooks.gitignore",
    "cpp": "C++.gitignore",
    "c++": "C++.gitignore",
    "c": "C.gitignore",
    "node": "Node.gitignore",
    "js": "Node.gitignore",
    "java": "Java.gitignore",
    "kotlin": "Java.gitignore",
    "go": "Go.gitignore",
    "rust": "Rust.gitignore",
    "haskell": "Haskell.gitignore",
    "ocaml": "OCaml.gitignore",
    "unity": "Unity.gitignore",
    "tex": "TeX.gitignore",
    "latex": "TeX.gitignore",
}


class ApiError(Exception):
    pass


def build_gitignore_content(
    names: list[str],
    bases: list[str] | None = None,
    root: str = "https://raw.githubusercontent.com/github/gitignore/main/",
    header_text_template: str = "#\n# {path}\n# Get the latest version at https://github.com/github/gitignore/{path}\n#\n",
) -> tuple[str, bool]:
    """Create .gitignore content from list of names and bases."""
    if bases is None:
        bases = ["windows", "macos"]
    else:
        bases = [name.lower() for name in bases]

    final_text = ""
    names = bases + [name for name in names if name.lower() not in bases]

    error_occured = False
    for name in names:
        if name is None:
            continue
        path = ALIASES.get(name.lower(), name)
        url = root + path

        try:
            click.echo(f"Fetching '{name}' from {url} ...")
            res = requests.get(url)
            if res.status_code == 200:
                header_text = header_text_template.format(path=path)
                final_text += header_text
                final_text += res.text + "\n"
            else:
                click.echo(
                    f"[error]: failed to fetch '{name}' (HTTP code: {res.status_code}). It will be skipped."
                )
                error_occured = True
        except requests.exceptions.RequestException as e:
            raise ApiError("error occur when fetching content") from e
    return final_text, error_occured


@click.command("create-gitignore")
@click.argument("names", type=str, nargs=-1)
@click.option(
    "--outfile",
    "-o",
    type=click.Path(exists=False, dir_okay=False),
    default=".gitignore",
    help="Specify an output file.",
)
@click.option(
    "--base",
    "-b",
    type=str,
    multiple=True,
    default=("windows", "macos"),
    help='Base content of the file. Default: windows, macos. To not include any base content, use --base "". To specify multiple base, use --base name1 --base name2 ...',
)
@click.option(
    "--list-mapping",
    "-l",
    type=bool,
    is_flag=True,
    help="Show list of available mappings.",
)
@click.pass_context
def create_gitignore(
    ctx: click.Context,
    names: list[str],
    outfile: str | Path = ".",
    base: list[str] | tuple[str, ...] = ("windows", "macos"),
    list_mapping: bool = False,
) -> None:
    """Create .gitignore content from list of NAMES.

    The windows and macos content for .gitignore will be added by default. Use --base "" to disable this. The command will fetch the content
    from github/gitignore repository on GitHub using https://raw.githubusercontent.com/github/gitignore/main/.

    --list-mapping can be used to view avaialble mapping. If the provided NAMES is not part of the mappings, it will be used as is.
    """
    if list_mapping:
        click.echo("The following aliases are available:")
        for key in ALIASES:
            click.echo(f"- {key} -> {ALIASES[key]}")
        ctx.exit()

    if isinstance(outfile, str):
        outfile = Path(outfile)
    if isinstance(names, tuple):
        names = list(names)
    if isinstance(base, tuple):
        bases = list(base)

    bases = [name for name in bases if len(name.strip()) != 0]

    name_text = "\n".join(
        itertools.chain(
            [f"- {name} (from bases)" for name in bases],
            [f"- {name}" for name in names],
        )
    )

    if len(names) == 0 and len(bases) == 0:
        click.echo(f"Will create an empty '{outfile.name}' file at {outfile.parent}")
    else:
        click.echo(
            f"Will create '{outfile.name}' file at {outfile.parent} with the following content:\n{name_text}"
        )
    click.confirm("Do you want to continue?", default=True, abort=True)

    try:
        content, error_occured = build_gitignore_content(names, bases)
        if error_occured:
            click.confirm(
                "One or more name failed to fetch. Do you want to continue?",
                default=False,
                abort=True,
            )
    except ConnectionError as e:
        ctx.fail(f"network error occured\n{e}")
    except ApiError as e:
        ctx.fail(f"api error occured\n{e}")

    if outfile.exists():
        ans = click.confirm(f"'{outfile!s}' already exist, overwrite?")
        if not ans:
            click.echo(f"'{outfile!s}' is not modified")
            ctx.exit()

    with open(outfile, "w") as out_f:
        out_f.write(content)
    click.echo(f"Content is written to '{outfile!s}'")


if __name__ == "__main__":
    create_gitignore()
