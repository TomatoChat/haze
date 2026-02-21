"""Navigate a nested dict via a dotted key path and return the value."""

from typing import Any


def get_nested(obj: dict[str, Any], dotted: str) -> tuple[bool, Any]:
    """Return (found, value).  Returns (False, None) if any segment is missing."""
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur
