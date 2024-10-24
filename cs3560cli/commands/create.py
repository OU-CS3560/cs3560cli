"""Create command groups."""

import itertools
import random
import shutil
import string
import sys
from pathlib import Path

import click
import requests
from rich import print
from rich.console import Console

from ..config import Config, pass_config
from ..services.canvas import CanvasApi, parse_url_for_course_id
from ..services.github import GitHubApi, is_team_path
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
    header_text_template: str = "#\n# {path}\n# Get the latest version at https://github.com/github/gitignore/tree/main/{path}\n#\n",
) -> tuple[str, bool]:
    """Create .gitignore content from list of names and bases."""
    if bases is None:
        bases = ["windows", "macos"]
    else:
        bases = [name.lower() for name in bases]

    final_text = ""
    names = bases + [name for name in names if name.lower() not in bases]

    console = Console()
    error_occurred = False
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
                    error_occurred = True
            except requests.exceptions.RequestException as e:
                raise ApiError("error occur when fetching content") from e
    return final_text, error_occurred


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

    --list-mapping can be used to view available mapping. If the provided NAMES is not part of the mappings, it will be used as is.
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
        content, error_occurred = build_gitignore_content(names, bases)
        if error_occurred:
            click.confirm(
                "One or more name failed to fetch. Do you want to continue?",
                default=False,
                abort=True,
            )
    except ConnectionError as e:
        ctx.fail(f"network error occurred\n{e}")
    except ApiError as e:
        ctx.fail(f"api error occurred\n{e}")

    if outfile.exists():
        ans = click.confirm(f"'{outfile!s}' already exist, overwrite?")
        if not ans:
            click.echo(f"'{outfile!s}' is not modified")
            ctx.exit()

    with open(outfile, "w") as out_f:
        out_f.write(content)
    click.echo(f"Content is written to '{outfile!s}'")


@create.command("password")
@click.option(
    "--style",
    "-s",
    type=click.Choice(("quiz", "ios")),
    default="quiz",
    help="Specify the style of password",
)
@click.option(
    "--length",
    type=int,
    default=None,
    help="Length of the password for the quiz style (default = 8). Length of the group in ios style (default = 6).",
)
@click.pass_context
def create_password(
    ctx: click.Context, style: str = "quiz", length: int | None = None
) -> None:
    """Create a random password with STYLE.

    CAUTION: The generated password is not for security critical use case.
    """

    result = ""
    if style == "quiz":
        if length is None:
            length = 8

        digits = "".join(random.choices(string.digits, k=length))
        indices = random.choices(range(1, length - 1), k=2)

        result = ""
        for idx, c in enumerate(digits):
            if idx in indices:
                result = result + "-"
            else:
                result = result + c

    elif style == "ios":
        if length is None:
            length = 6
        groups = []
        for _ in range(3):
            groups.append(
                "".join(
                    random.choices(
                        string.digits + string.ascii_lowercase + string.ascii_uppercase,
                        k=length,
                    )
                )
            )
        result = "-".join(groups)

    click.echo(result)


@create.command(name="gh-invite")
@click.argument("team_path", type=str)
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
def create_github_invite(
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
        ctx.exit(1)

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
            print("[red]Cannot retrieve student list from Canvas.")
            ctx.exit(1)

        email_addresses = [s.email_address for s in students]
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


@create.command(name="gh-team")
@click.argument("team_path", type=str)
@click.option("--parent", "-p", type=str, default=None, required=True)
@click.option("--description", "-d", type=str, default=None)
@click.option(
    "--privacy", type=click.Choice(choices=("closed", "secret")), default="closed"
)
@click.option("--template", "-t", type=str, default=None)
@click.option("--invite", "-i", type=str, default=None)
@click.option(
    "--permission",
    type=click.Choice(choices=("pull", "triage", "push", "maintain", "admin")),
    default="maintain",
)
# Canvas related options.
@click.option(
    "--from-canvas-course",
    "-c",
    type=str,
    default=None,
    help="The Canvas course to look for the groupset.",
)
@click.option(
    "--canvas-groupset-name",
    "-g",
    type=str,
    default=None,
    help="The groupset name containing the groups to create teams for.",
)
# Misc options.
@click.option(
    "--delay",
    type=float,
    default=1,
    help="A delay in second between request.",
)
@click.option(
    "--dry-run",
    type=bool,
    is_flag=True,
    default=False,
)
@pass_config
@click.pass_context
def create_github_team(
    ctx: click.Context,
    config: Config,
    team_path: str,
    parent: str | None = None,
    description: str | None = None,
    privacy: str = "closed",
    template: str | None = None,
    invite: str | None = None,
    permission: str = "maintain",
    from_canvas_course: str | None = None,
    canvas_groupset_name: str | None = None,
    delay: float = 1.0,
    dry_run: bool = False,
) -> None:
    """
    Create a team named TEAM_PATH under a PARENT team.

    Optionally, create a repository with the same name from TEMPLATE and allow the team to access it with PERMISSION (default: maintain).
    Optionally, invite list of comma separated email addresses in INVITE.

    Groupset named CANVAS-GROUPSET-NAME can be used as a source of teams to be created under a PARENT team. A github team
    will be created for each group found in CANVAS-GROUPSET-NAME groupset on course FROM-CANVAS-COURSE on Canvas.
    """
    # Sanity checks.
    if not is_team_path(team_path):
        click.echo(
            f"[error]: '{team_path}' is not in the required format, '<org-name>/<team-name>'."
        )
        ctx.exit(1)
    if template is not None and "/" not in template:
        click.echo(
            f"[error]: '{template}' is not in the required format, '<org-name>/<repo-name>'."
        )
        ctx.exit(1)
    if parent is not None:
        if not is_team_path(parent):
            click.echo(
                f"[error]: '{parent}' is not in the required format, '<org-name>/<team-name>'."
            )
            ctx.exit(1)

        team_org_name, team_name = team_path.split("/")
        parent_org_name, _ = parent.split("/")
        if team_org_name != parent_org_name:
            click.echo(
                f"[error]: '{team_path}' and '{parent}' must be in the same organization."
            )
            ctx.exit(1)

    # Token check.
    if not config.has_github_token():
        ctx.invoke(update_github_token)

    # Data source for group information.
    if from_canvas_course is not None:
        if not config.has_canvas_token():
            ctx.invoke(update_canvas_token)

        # TODO: Obtain list of groups from groupset on Canvas.
        # The creation flow need to be adjusted to create multiple
        # teams.

    gh = GitHubApi(token=config.github_token)
    try:
        if parent is not None:
            parent_team_id = gh.get_team_id_from_team_path(parent)
            if parent_team_id is None:
                print(
                    f"[red]Cannot retrieve the team's ID for '{parent}'. Please make sure the team name is correct."
                )
                ctx.exit(1)
        else:
            parent_team_id = None

        # Create a team under the parent (if parent is specified).
        if not gh.create_team(
            team_name,
            team_org_name,
            description=description,
            privacy=privacy,
            notification_setting="notifications_disabled",
            parent_team_id=parent_team_id,
        ):
            click.echo("[error]: failed to create team.")
            ctx.exit(1)

        # Create a repository with the template.
        if template is not None:
            if not gh.create_repository_with_template(
                team_path, template, private=True
            ):
                click.echo("[error]: failed to create a repository from the template.")
                ctx.exit(1)

            # Add team to this repository with the given permission.
            if not gh.add_team_to_repository(
                team_path, team_path, permission=permission
            ):
                click.echo("[error]: failed to add team to the repository.")
                ctx.exit(1)

        # TODO: If invite is presence, parse and invite to the team.

    except PermissionError:
        print(
            f"[red]Cannot retrieve the team's ID for '{team_path}'. "
            "Please make sure that the token has 'admin:org' permission and it is authorized with SAML SSO."
        )
