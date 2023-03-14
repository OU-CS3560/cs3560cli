"""
Use pypi/watchdog to watch for and unpack archive file.

For now it is hard coded to use 7z.exe to extract the file.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

import click

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.utils import platform

WIN_KNOWN_7Z_PATH = Path(r"C:\Program Files\7-Zip\7z.exe")

def is_7z_available() -> bool:
    """Check if 7z exist."""
    if platform.is_linux():
        try:
            subprocess.run("7z", shell=True, capture_output=True, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
    elif platform.is_windows():
        try:
            output = subprocess.run(WIN_KNOWN_7Z_PATH, capture_output=True, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False


def extract(path: Path):
    dir_path = Path(path.stem)

    if dir_path.exists() and dir_path.is_dir():
        print("[warn] target folder already exist, skipping the extraction")
        return

    if platform.is_linux():
        # FIXME: The 7z will flatten the directory tree.
        subprocess.check_output(args=["7z", "e", path, f"-o{path.stem}"])
    elif platform.is_windows():
        subprocess.check_output(args=[str(WIN_KNOWN_7Z_PATH), "e", path, f"-o{path.stem}"])

class ArchiveFilesEvenHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(patterns=[
            "*.7z",
            "*.zip",
            "*.tar",
            "*.tar.gz"
        ])

    def on_created(self, event):
        if event.is_directory is False:
            path = Path(event.src_path)
            print(f"detected (on created) {str(path)}")

    def on_closed(self, event):
        """
        With created, firefox create an empty file first.
        Chrome / Edge move the file from crdownload to the actual file name.
        """
        if event.is_directory is False:
            # Close event is received too quickly.
            time.sleep(2)
            path = Path(event.src_path)
            print(f"extracting (on closed delayed) {str(path)}")

            # We can also be the one closing the file.
            extract(path)

    def on_moved(self, event):
        if event.is_directory is False:
            path = Path(event.dest_path)
            print(f"extracting (on moved) {str(path)}")
            extract(path)


@click.command("watch-zip")
@click.option("--path", default=None, type=click.Path(exists=True))
def watch_zip(path):
    """Watch for new zip file and extract it."""
    if not is_7z_available():
        print("The program requires 7z")
        sys.exit(0)

    if path is None:
        path = os.getcwd()

    event_handler = ArchiveFilesEvenHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        print("watcher started")
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    watch_zip()