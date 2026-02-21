"""Set a value in a nested dict via a dotted key path, creating missing dicts."""

from typing import Any


def set_nested(obj: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value
