"""Cast a canonical haze value to the type expected by a target agent."""

from typing import Any


def cast_value(value: Any, type_name: str) -> Any:
    if type_name == "boolean":
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")
    if type_name == "integer":
        try:
            return int(value)
        except (ValueError, TypeError):
            return value
    return value
