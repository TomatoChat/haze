"""Extract named haze sync blocks from markdown content.

Sync blocks are delimited by HTML comment markers:

    <!-- haze:start:BLOCKNAME -->
    ...synced content...
    <!-- haze:end:BLOCKNAME -->

Block names may contain letters, digits, hyphens, and underscores.
"""

import re
from typing import Any

_START = re.compile(r"<!--\s*haze:start:([\w-]+)\s*-->")
_END   = re.compile(r"<!--\s*haze:end:([\w-]+)\s*-->")


def extract_blocks(content: str) -> dict[str, str]:
    """Return {block_name: inner_content} for every complete sync block found."""
    from haze.helpers.log import warn

    blocks: dict[str, str] = {}
    pos = 0
    while True:
        m_start = _START.search(content, pos)
        if not m_start:
            break
        name = m_start.group(1)
        m_end = _END.search(content, m_start.end())
        if not m_end or m_end.group(1) != name:
            warn(f"Unclosed sync block '{name}' — skipping.")
            pos = m_start.end()
            continue
        blocks[name] = content[m_start.end() : m_end.start()]
        pos = m_end.end()
    return blocks
