"""Translate a canonical haze value to the raw value expected by a target agent."""

from typing import Any

from haze.helpers.cast_value import cast_value


def forward_translate(setting: dict, agent: str, canonical: Any) -> tuple[bool, Any]:
    """Return (ok, raw).  Returns (False, None) when no mapping can be found.

    Three translation strategies, tried in order:
      1. No valueMap entry → cast the canonical value to the agent's target type.
      2. Template pattern  → substitute {value} with the canonical value.
      3. Dict map          → direct lookup by canonical key.
    """
    vm = (setting.get("valueMap") or {}).get(agent)
    target_type: str = setting["targets"][agent].get("type", "string")

    if vm is None:
        return True, cast_value(canonical, target_type)

    if isinstance(vm, str) and "{value}" in vm:
        return True, vm.replace("{value}", str(canonical))

    if isinstance(vm, dict):
        key = str(canonical)
        if key in vm:
            return True, vm[key]
        return False, None

    return False, None
