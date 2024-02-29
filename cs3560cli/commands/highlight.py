"""
Perform syntax highlighting and output as HTML file

This is base on the assumption that pygments's own CLI tool
does not support specifying inline the style for HTML formatter.
(This may not be true anymore since `-O noclasses=true -f html` may
solve the problem).

Another reason is we want to use content of the file to determine
the lexer instead of just a file name.

Specification:
- Must produce HTML with inline CSS, so it can be used in Blackboard.

Dependencies:
- Pygments
"""

import sys
from pathlib import Path

import click
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name, guess_lexer


def highlight_inline(code: str, lexer):
    formatter = HtmlFormatter()
    formatter.noclasses = True

    return pygments_highlight(code, lexer, formatter)


@click.command("highlight")
@click.argument("in-file", default="-", type=str)
@click.option("-o", "--out-file", default="-", type=str)
@click.option("-l", "--lexer", default="", type=str)
@click.pass_context
def highlight(
    ctx, in_file: str | Path = "-", out_file: str | Path = "-", lexer: Lexer | str = ""
):
    """Get syntax highlighted code with inline style"""
    content = ""
    if isinstance(in_file, str):
        if in_file == "-":
            for line in sys.stdin:
                content += line
        else:
            in_file = Path(in_file)
            if not in_file.exists():
                ctx.fail(f"'{str(in_file)}' does not exist")

            with open(in_file, "r") as in_f:
                content = in_f.read()

    if isinstance(lexer, str):
        if lexer == "":
            lexer = guess_lexer(content)
        else:
            lexer = get_lexer_by_name(lexer)

    result = highlight_inline(content, lexer)

    if isinstance(out_file, str):
        if out_file == "-":
            # Pad the input and output a bit.
            print("\n")
            print(result)
        else:
            outfile_path = Path(out_file)
            if outfile_path.exists():
                ans = click.confirm(f"'{str(outfile_path)}' already exist, overwrite?")
                if not ans:
                    click.echo(f"'{str(outfile_path)}' is not modified")
                    ctx.exit()

            with open(outfile_path, "w") as out_f:
                out_f.write(result)


if __name__ == "__main__":
    highlight()
