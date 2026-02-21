"""Return a deterministic string key for any value, used for equality comparisons."""

import json
from typing import Any


def stable_key(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
