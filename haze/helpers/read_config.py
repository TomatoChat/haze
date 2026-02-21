"""Read a coding-agent config file into a plain dict.

Agent config locations:
  claude  ~/.claude/settings.json   (JSON)
  gemini  ~/.gemini/settings.json   (JSON)
  codex   ~/.codex/config.toml      (TOML)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[import]
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef,import]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

AGENT_CONFIG: dict[str, Path] = {
    "claude": Path.home() / ".claude" / "settings.json",
    "gemini": Path.home() / ".gemini" / "settings.json",
    "codex":  Path.home() / ".codex"  / "config.toml",
}

AGENT_FORMAT: dict[str, str] = {
    "claude": "json",
    "gemini": "json",
    "codex":  "toml",
}


def read_config(agent: str) -> dict[str, Any]:
    """Return the parsed config dict for *agent*, or {} if the file is absent."""
    from haze.helpers.log import warn

    path = AGENT_CONFIG[agent]
    if not path.exists():
        return {}

    if AGENT_FORMAT[agent] == "json":
        return json.loads(path.read_text(encoding="utf-8"))

    if tomllib is None:
        warn(
            f"Cannot read {agent} config: tomllib is unavailable. "
            "Install tomli (`pip install tomli`) or use Python ≥ 3.11."
        )
        return {}
    with path.open("rb") as fh:
        return tomllib.load(fh)
