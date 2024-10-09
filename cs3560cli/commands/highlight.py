"""
Perform syntax highlighting and output as HTML file

This is base on the assumption that pygments's own CLI tool
does not support specifying inline the style for HTML formatter.
(This may not be true anymore since `-O noclasses=true -f html` may
solve the problem).

Another reason is we want to use content of the file to determine
the lexer instead of just a file name.

Specification:
- Must produce HTML with inline CSS, so it can be used in LMS.

Dependencies:
- Pygments
"""

import io
import sys
from pathlib import Path
from typing import TextIO

import click
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name, guess_lexer


def highlight_inline(code: str, lexer: Lexer, linenos: str | bool = "inline") -> str:
    """Return syntax highlighted HTML fragments of the code with inline style."""
    formatter = HtmlFormatter(linenos=linenos)
    formatter.noclasses = True

    return pygments_highlight(code, lexer, formatter)


@click.command("highlight")
@click.argument("in-file", default="-", type=str)
@click.option(
    "-o",
    "--out-file",
    default="-",
    type=str,
    help="Output file path. Use '-' for stdout. Default is to output to stdout.",
)
@click.option("-l", "--lexer", default="", type=str, help="E.g. python, cpp.")
@click.option(
    "--line-number/--no-line-number",
    default=True,
    type=bool,
    help="Show or hide line numbers.",
)
@click.pass_context
def highlight(
    ctx: click.Context,
    in_file: str | Path | TextIO = "-",
    out_file: str | Path | TextIO = "-",
    lexer: Lexer | str = "",
    line_number: bool = False,
) -> None:
    """Generate syntax highlighted HTML fragments for the given code with inline style for LMS.

    IN_FILE can be a path to a file or '-' for the command to read from stdin. If LEXER is provided,
    said lexer will be used. If not, the lexer will be guessed based on the content.
    """
    content = ""
    if isinstance(in_file, str):
        if in_file == "-":
            in_file = sys.stdin
        else:
            in_file = Path(in_file)

    if isinstance(in_file, Path):
        if not in_file.exists():
            ctx.fail(f"'{in_file!s}' does not exist")

        with open(in_file) as in_f:
            content = in_f.read()

    elif isinstance(in_file, io.TextIOBase):
        for line in sys.stdin:
            content += line

    if isinstance(lexer, str):
        if lexer == "":
            lexer = guess_lexer(content)
        else:
            lexer = get_lexer_by_name(lexer)

    result = highlight_inline(
        content, lexer, linenos="inline" if line_number else False
    )

    if isinstance(out_file, str):
        if out_file == "-":
            out_file = sys.stdout
        else:
            out_file = Path(out_file)

    if isinstance(out_file, Path):
        if out_file.exists():
            ans = click.confirm(f"'{out_file!s}' already exist, overwrite?")
            if not ans:
                click.echo(f"'{out_file!s}' is not modified")
                ctx.exit()

        with open(out_file, "w") as out_f:
            out_f.write(result)

    elif isinstance(out_file, io.TextIOBase):
        print(result, end="", file=out_file)
