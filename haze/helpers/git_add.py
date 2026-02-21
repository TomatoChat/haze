"""Stage a file for commit, silently ignoring files that are not git-tracked."""

import subprocess
from pathlib import Path


def git_add(path: Path) -> None:
    try:
        subprocess.run(
            ["git", "add", str(path)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        pass
