"""Write a coding-agent config dict back to its file on disk."""

from __future__ import annotations

import json
from typing import Any

try:
    import tomli_w  # type: ignore[import]
except ImportError:
    tomli_w = None  # type: ignore[assignment]

from haze.helpers.read_config import AGENT_CONFIG, AGENT_FORMAT


def write_config(agent: str, data: dict[str, Any]) -> None:
    """Persist *data* to the config file for *agent*, creating directories as needed."""
    from haze.helpers.log import warn

    path = AGENT_CONFIG[agent]
    path.parent.mkdir(parents=True, exist_ok=True)

    if AGENT_FORMAT[agent] == "json":
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return

    if tomli_w is None:
        warn(
            f"Cannot write {agent} config: tomli-w is unavailable. "
            "Install it with `pip install tomli-w`."
        )
        return
    with path.open("wb") as fh:
        tomli_w.dump(data, fh)
