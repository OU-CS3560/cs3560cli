import os

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    version = version_file.read().strip()

__version__ = version
