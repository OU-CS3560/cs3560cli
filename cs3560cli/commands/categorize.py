"""Group student submitted files into a folder."""

from pathlib import Path

import click

from ..services.canvas import categorize as categorize_step


@click.command(name="categorize")
@click.argument(
    "source",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, writable=True
    ),
    required=True,
)
@click.argument(
    "destination",
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, readable=True, writable=True
    ),
    required=True,
)
def categorize(source: Path | str, destination: Path | str) -> None:
    """
    Group files from the same student together in a folder.

    SOURCE can be the zip file itself or the folder where the zip file
    was extracted to. Note that this only work with files downloaded from Canvas.

    DESTINATION is the folder where the grouped files to be in. If it does not
    exist, one will be created.

    Example usages:

    1) Categorize the gradebook zip file into 'hw2' folder.

        \b
        $ cs3560cli categorize submissions.zip hw2
        Categorizing files ...
        $ ls hw2/
        bobcatrufus ... output is removed for brevity ...

    2) When the zip file was already extracted to 'hw2' folder.

        \b
        $ cs3560cli categorize hw2 hw2-grouped
        Categorizing files ...
        $ ls hw2-grouped/
        bobcatrufus ... output is removed for brevity ...
    """
    click.echo("Categorizing files ...")
    categorize_step(source, destination)
