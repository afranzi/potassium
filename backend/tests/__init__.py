import os
from pathlib import Path

fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))


def fixture_file_path(fixture: str) -> Path:
    return Path(os.path.join(fixtures_dir, fixture))
