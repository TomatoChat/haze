"""Append a named haze sync block to the end of a markdown file's content.

Sync blocks use HTML comment markers so they are invisible when rendered:

    <!-- haze:start:BLOCKNAME -->
    ...synced content...
    <!-- haze:end:BLOCKNAME -->
"""


def insert_block(content: str, name: str, inner: str) -> str:
    """Return *content* with a new named sync block appended at the end."""
    marker_start = f"<!-- haze:start:{name} -->"
    marker_end   = f"<!-- haze:end:{name} -->"
    return content.rstrip("\n") + f"\n\n{marker_start}{inner}{marker_end}\n"
