"""Translate an agent-specific config value back to its canonical haze value."""

from typing import Any


def reverse_translate(setting: dict, agent: str, raw: Any) -> tuple[bool, Any]:
    """Return (ok, canonical).  Returns (False, None) when no mapping can be found.

    Three translation strategies, tried in order:
      1. No valueMap entry → pass-through (raw IS the canonical value).
      2. Template pattern  → strip prefix/suffix to extract the embedded value.
      3. Dict map          → build a reverse lookup (first occurrence wins for
                             collisions, e.g. Codex "on-request" ← ask|planOnly).
    """
    vm = (setting.get("valueMap") or {}).get(agent)

    if vm is None:
        return True, raw

    if isinstance(vm, str) and "{value}" in vm:
        pre, _, suf = vm.partition("{value}")
        s = str(raw)
        if s.startswith(pre) and (not suf or s.endswith(suf)):
            inner = s[len(pre) : len(s) - len(suf)] if suf else s[len(pre):]
            try:
                return True, int(inner)
            except ValueError:
                return True, inner
        return False, None

    if isinstance(vm, dict):
        rev: dict[Any, Any] = {}
        for canonical_val, agent_val in vm.items():
            if agent_val not in rev:
                rev[agent_val] = canonical_val

        if raw in rev:
            return True, rev[raw]

        # Fallback: string comparison handles bool/number edge cases across
        # JSON and TOML parsers.
        str_raw = str(raw).lower() if isinstance(raw, bool) else str(raw)
        for k, v in rev.items():
            k_str = str(k).lower() if isinstance(k, bool) else str(k)
            if k_str == str_raw:
                return True, v

        return False, None

    return False, None
