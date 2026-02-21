"""Find agent instruction markdown files in the current working directory."""

from pathlib import Path

DOC_FILES = ["CLAUDE.md", "GEMINI.md", "AGENTS.md"]


def find_doc_files() -> dict[str, Path]:
    """Return {filename: path} for every agent doc file that exists in cwd."""
    cwd = Path.cwd()
    return {name: cwd / name for name in DOC_FILES if (cwd / name).exists()}
