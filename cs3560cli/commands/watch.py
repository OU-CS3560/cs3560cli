"""
Use pypi/watchdog to watch for and unpack archive file.

For now it is hard coded to use 7z.exe (7z on linux) to extract the file.
"""

import subprocess
import sys
import time
from pathlib import Path

import click
from rich import print
from rich.console import Console
from watchdog.events import (
    DirCreatedEvent,
    DirMovedEvent,
    FileClosedEvent,
    FileCreatedEvent,
    FileMovedEvent,
    PatternMatchingEventHandler,
)
from watchdog.observers import Observer
from watchdog.utils import platform

WIN_KNOWN_7Z_PATH = Path(r"C:\Program Files\7-Zip\7z.exe")


def to_path(text: str | bytes) -> Path:
    if isinstance(text, bytes):
        return Path(text.decode())
    else:
        return Path(text)


def is_7z_available() -> bool:
    """Check if 7z exist."""
    if platform.is_linux():
        try:
            _ = subprocess.run("7z", shell=True, capture_output=True, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
    elif platform.is_windows():
        try:
            _ = subprocess.run(WIN_KNOWN_7Z_PATH, capture_output=True, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
    return False


def extract(path: Path, console: Console | None = None) -> None:
    dir_name = path.stem
    dir_path = path.with_name(dir_name)

    if dir_path.exists() and dir_path.is_dir():
        if console is not None:
            console.warn(
                f"[bold yellow]target folder ({dir_path!s}) already exist, skipping the extraction[/bold yellow]"
            )
        else:
            print(
                f"[bold yellow]target folder ({dir_path!s}) already exist, skipping the extraction[/bold yellow]"
            )
        return

    if platform.is_linux():
        # FIXME: The 7z will flatten the directory tree.
        try:
            subprocess.check_output(args=["7z", "x", path, f"-o{dir_path!s}"])
        except subprocess.CalledProcessError:
            if console is not None:
                console.warn(
                    f"[bold red]failed to extract file: {path!s} to {dir_path!s}[/bold red]"
                )
            else:
                print(
                    f"[bold red]failed to extract file: {path!s} to {dir_path!s}[/bold red]"
                )
    elif platform.is_windows():
        try:
            subprocess.check_output(
                args=[str(WIN_KNOWN_7Z_PATH), "x", path, f"-o{dir_path!s}"]
            )
        except subprocess.CalledProcessError:
            if console is not None:
                console.warn(
                    f"[bold red]failed to extract file: {path!s} to {dir_path!s}[/bold red]"
                )
            else:
                print(
                    f"[bold red]failed to extract file: {path!s} to {dir_path!s}[/bold red]"
                )


class ArchiveFilesEventHandler(PatternMatchingEventHandler):
    def __init__(self, console: Console) -> None:
        self.archive_suffixes = [
            ".7z",
            ".zip",
            ".tar",
            ".tar.gz",
            ".tar.xz",
            ".rar",
        ]
        super().__init__(patterns=[f"*{name}" for name in self.archive_suffixes])

        self.console = console

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        """
        Firefox creates an empty file first, so we will use on_closed
        to do the actual extraction.
        """
        if event.is_directory is False:
            src_path = to_path(event.src_path)
            self.console.log(f"on_created(file, src_path={src_path!s})")
        else:
            self.console.log(f"on_created(folder, src_path={src_path!s})")

    def on_closed(self, event: FileClosedEvent) -> None:
        if event.is_directory is False:
            # It appears that sometimes the close event is received too quickly.
            # The file will still be closing and we will get an error when we try to open
            # the target file.
            time.sleep(2)
            src_path = to_path(event.src_path)
            self.console.log(f"delayed on_closed(file, src_path={src_path!s})")

            # We can also be the one closing the file.
            extract(src_path)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        """
        Chromium-based browsers move the file from `*.crdownload` to the actual file name.
        """
        src_path = to_path(event.src_path)
        dest_path = to_path(event.dest_path)
        if event.is_directory is False:
            self.console.log(
                f"on_moved(file, src_path={src_path!s} dest_path={dest_path!s})"
            )

            file_extension = "".join(dest_path.suffixes)
            if file_extension in self.archive_suffixes:
                extract(dest_path)
        else:
            self.console.log(
                f"on_moved(folder, src_path={src_path!s}) dest_path={dest_path!s})"
            )


@click.command("watch")
@click.argument("path", type=str, default=None, required=False)
@click.pass_context
def watch(ctx: click.Context, path: Path) -> None:
    """
    Watch for a new zip file at PATH and extract it.

    If PATH is not specified, assuming the current working directory.
    """
    if not is_7z_available():
        print(
            "This command requires 7z. For Windows, please install 7z from https://www.7-zip.org/. For linux the package name should be 'p7zip' or something similar."
        )
        sys.exit(0)

    if path is None:
        path = Path.cwd()
    elif isinstance(path, str):
        path = Path(path)

    if not path.exists():
        print(f"[red]'{path}' does not exist.")
        ctx.exit(1)

    console = Console()

    event_handler = ArchiveFilesEventHandler(console)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()
    try:
        console.log("watcher started")
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
