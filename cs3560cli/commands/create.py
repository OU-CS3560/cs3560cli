"""Create command groups."""

import itertools
import shutil
import sys
from pathlib import Path

import click
import requests
from rich import print
from rich.console import Console

from ..config import Config, pass_config
from ..github import GitHubApi, is_team_path
from ..lms.canvas import CanvasApi, parse_url_for_course_id
from .auth import update_canvas_token, update_github_token


@click.group(
    context_settings={"max_content_width": shutil.get_terminal_size().columns - 10}
)
def create() -> None:
    """Create various things"""
    pass


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

    console = Console()
    error_occured = False
    with console.status("[bold green]Fetching .gitignore content...") as status:
        for name in names:
            if name is None:
                continue
            path = ALIASES.get(name.lower(), name)
            url = root + path

            try:
                status.update(status=f"Fetching {name} from {url} ...")
                res = requests.get(url)
                if res.status_code == 200:
                    header_text = header_text_template.format(path=path)
                    final_text += header_text
                    final_text += res.text + "\n"
                    console.log(f"Fetched {name} from {url}")
                else:
                    console.log(
                        f"[red]Failed to fetch '{name}' (HTTP code: {res.status_code}). It will be skipped."
                    )
                    error_occured = True
            except requests.exceptions.RequestException as e:
                raise ApiError("error occur when fetching content") from e
    return final_text, error_occured


@create.command("gitignore")
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
    help='Base content of the file. Default: windows, macos. To not include any base content, use --base "". To specify multiple bases, use --base name1 --base name2 ...',
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


@create.command(name="gh-invite")
@click.argument("team_path")
@click.option("--from-canvas-course", "-c", type=str, default=None)
@click.option("--from-file", "-f", type=str, default=None)
@click.option(
    "--delay",
    type=float,
    default=1,
    help="A delay in second between invitation request.",
)
@click.option(
    "--dry-run",
    type=bool,
    is_flag=True,
    default=False,
    help="Print out the email addresses instead of actually sending invite to them.",
)
@pass_config
@click.pass_context
def craete_github_invite(
    ctx: click.Context,
    config: Config,
    team_path: str,
    from_canvas_course: str | None,
    from_file: str | None,
    delay: float,
    dry_run: bool = False,
) -> None:
    """
    Invite students from Canvas (or list of email addresses) to a team in GitHub Organization.

    The TEAM_PATH must be in a format <org-name>/<team-name> and the team itself must be created
    beforehand.

    Example usages:

    1) Send invitation to join OU-CS3560/entire-class-24f team to all students in a Canvas' course with ID 24840.

        \b
        $ cs3560cli create gh-invite --from-canvas-course 24840 OU-CS3560/entire-class-24f

    2) Using the course's URL instead of ID.

        \b
        $ cs3560cli create gh-invite --from-canvas-course https://ohio.instructure.com/courses/24840 OU-CS3560/entire-class-24f

    3) Use a file with email addresses. Each on a line.

        \b
        $ cs3560cli create gh-invite OU-CS3560 entire-class-24f --from-file emails.txt

    4) Pass in the email addresses via stdin. Use Ctrl+d (on linux) or Ctrl+z then Enter (on Windows) to
       signify the end of input.

        \b
        $ cs3560cli create gh-invite OU-CS3560 entire-class-24f --from-file -
        bobcat@ohio.edu
        <Ctrl+d> or <Ctrl+z> then <Enter>
    """
    if not is_team_path(team_path):
        click.echo(
            f"[error]: '{team_path}' is not in the required format, '<org-name>/<team-name>'."
        )

    if not config.has_github_token():
        ctx.invoke(update_github_token)

    if from_canvas_course is not None and from_file is not None:
        print(
            "[red]Please either specify '--from-canvas-course' or '--from-file', but not both."
        )

    if from_canvas_course is not None:
        if not config.has_canvas_token():
            ctx.invoke(update_canvas_token)

        if from_canvas_course.startswith("http"):
            course_id = parse_url_for_course_id(from_canvas_course)
            if course_id is None:
                print(
                    f"[red]Failed to parse '{from_canvas_course}' for course ID. We think that it is a URL, "
                    "please make sure the course id is part of it."
                )
                ctx.exit(1)
        else:
            course_id = from_canvas_course

        canvas = CanvasApi(token=config.canvas_token)
        students = canvas.get_students(course_id)
        if students is None:
            print("[red]Cannot retrive student list from Canvas.")
            ctx.exit(1)

        email_addresses = [s["user"]["email"] for s in students]
        click.echo(f"Found {len(email_addresses)} students in course id={course_id}.")

    elif from_file is not None:
        if isinstance(from_file, str) and from_file == "-":
            # Read in from the stdin.
            file_obj = sys.stdin
        else:
            file_obj = open(from_file)

        email_addresses = []
        for line in file_obj:
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            email_addresses.append(line)

        if from_file != "-":
            file_obj.close()
    else:
        print("[red]Please either specify '--from-canvas-course' or '--from-file'")
        ctx.exit(1)

    gh = GitHubApi(token=config.github_token)

    try:
        team_id = gh.get_team_id_from_team_path(team_path)
        if team_id is None:
            print(
                f"[red]Cannot retrieve the team's ID for '{team_path}'. Please make sure the team name is correct."
            )
            ctx.exit(1)

        click.echo(f"Sending invitations to join {team_path} (team_id={team_id}) ...")

        org_name, _ = team_path.split("/")
        if not dry_run:
            failed_email_addresses = gh.bulk_invite_to_org(
                org_name, team_id, email_addresses, delay_between_request=delay
            )
            for email_address in failed_email_addresses:
                print(f"Failed to invite {email_address}")
        else:
            for email_address in email_addresses:
                print(f"(dry-run) Inviting {email_address} ...")

    except PermissionError:
        print(
            f"[red]Cannot retrieve the team's ID for '{team_path}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
