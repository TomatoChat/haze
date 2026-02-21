"""Route: check and align coding-agent config files (Claude, Gemini, Codex).

For every translatable setting in settings_map.json:
  - Reads each agent's current value and reverse-translates to canonical form.
  - Conflicting canonical values (agents genuinely disagree) → exit 1.
  - Missing values (agent installed but setting absent) → auto-written + re-staged.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from haze.helpers.read_config import read_config, AGENT_CONFIG
from haze.helpers.write_config import write_config
from haze.helpers.get_nested import get_nested
from haze.helpers.set_nested import set_nested
from haze.helpers.reverse_translate import reverse_translate
from haze.helpers.forward_translate import forward_translate
from haze.helpers.stable_key import stable_key
from haze.helpers.git_add import git_add
from haze.helpers.log import info, warn, err

SETTINGS_MAP_PATH = Path(__file__).resolve().parent.parent / "settings_map.json"


def main() -> int:
    if not SETTINGS_MAP_PATH.exists():
        warn(f"settings_map.json not found at {SETTINGS_MAP_PATH}. Skipping.")
        return 0

    with SETTINGS_MAP_PATH.open(encoding="utf-8") as fh:
        settings: dict[str, dict] = json.load(fh)

    configs: dict[str, dict[str, Any]] = {agent: read_config(agent) for agent in AGENT_CONFIG}

    conflicts: list[str] = []
    modified: set[str] = set()

    for setting_name, setting in settings.items():
        if not setting.get("isTranslatable"):
            continue

        targets: dict[str, dict] = setting.get("targets", {})

        # ── 1. read + reverse-translate each agent's current value ────────────
        found: dict[str, Any] = {}
        for agent, target in targets.items():
            key = target.get("key")
            if not key:
                continue
            ok, raw = get_nested(configs[agent], key)
            if not ok:
                continue
            ok2, canonical = reverse_translate(setting, agent, raw)
            if ok2:
                found[agent] = canonical
            else:
                warn(f"'{setting_name}': cannot reverse-map {agent} value {raw!r} — skipping.")

        if not found:
            continue

        # ── 2. conflict check ─────────────────────────────────────────────────
        unique = {stable_key(v) for v in found.values()}
        if len(unique) > 1:
            lines = [f"  '{setting_name}' has conflicting values across agents:"]
            for agent, val in found.items():
                lines.append(f"    {agent:8s}  →  {val!r}")
            conflicts.append("\n".join(lines))
            continue

        # ── 3. align agents whose config exists but lacks this setting ────────
        agreed = next(iter(found.values()))
        for agent, target in targets.items():
            key = target.get("key")
            if not key:
                continue
            if not AGENT_CONFIG[agent].exists():
                continue
            if get_nested(configs[agent], key)[0]:
                continue
            ok, raw_val = forward_translate(setting, agent, agreed)
            if ok:
                set_nested(configs[agent], key, raw_val)
                modified.add(agent)
                info(f"  Set '{setting_name}' on {agent}: {raw_val!r}")
            else:
                warn(f"'{setting_name}': cannot forward-map {agreed!r} → {agent}. Skipping.")

    # ── write + re-stage ──────────────────────────────────────────────────────
    for agent in sorted(modified):
        write_config(agent, configs[agent])
        git_add(AGENT_CONFIG[agent])
        info(f"Aligned and re-staged {agent} config ({AGENT_CONFIG[agent]})")

    # ── report ────────────────────────────────────────────────────────────────
    if conflicts:
        print(file=sys.stderr)
        err(f"{len(conflicts)} conflict(s) in agent configs. Resolve before committing:\n")
        for block in conflicts:
            print(block, file=sys.stderr)
        print(file=sys.stderr)
        return 1

    if not modified:
        info("Agent configs are aligned. ✓")

    return 0
