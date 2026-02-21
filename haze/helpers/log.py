"""Logging helpers shared across all haze routes."""

import sys


def info(msg: str) -> None:
    print(f"[haze] {msg}")


def warn(msg: str) -> None:
    print(f"[haze] WARNING: {msg}", file=sys.stderr)


def err(msg: str) -> None:
    print(f"[haze] ERROR:   {msg}", file=sys.stderr)
