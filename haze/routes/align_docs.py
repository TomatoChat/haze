"""Route: align named sync blocks across CLAUDE.md, GEMINI.md, and AGENTS.md.

Any content wrapped in haze sync markers is kept identical across all three files:

    <!-- haze:start:BLOCKNAME -->
    ...content that stays in sync across every agent doc...
    <!-- haze:end:BLOCKNAME -->

Rules:
  - Block present in all files with the same content → already aligned, nothing to do.
  - Block present in some files, absent in others    → auto-inserted + re-staged.
  - Block present in multiple files with different content → conflict, exit 1.

Block names may contain letters, digits, hyphens, and underscores.
Multiple independent blocks per file are supported.
"""

from __future__ import annotations

import sys

from haze.helpers.find_doc_files import find_doc_files
from haze.helpers.extract_blocks import extract_blocks
from haze.helpers.insert_block import insert_block
from haze.helpers.git_add import git_add
from haze.helpers.log import info, err


def main() -> int:
    doc_paths = find_doc_files()

    if len(doc_paths) < 2:
        return 0  # nothing to align with fewer than 2 files present

    contents = {name: path.read_text(encoding="utf-8") for name, path in doc_paths.items()}
    blocks_by_file = {name: extract_blocks(content) for name, content in contents.items()}

    all_block_names: set[str] = set()
    for blocks in blocks_by_file.values():
        all_block_names.update(blocks.keys())

    if not all_block_names:
        return 0  # no sync blocks defined anywhere; nothing to do

    conflicts: list[str] = []
    modified: dict[str, str] = {}  # filename → updated content

    for block_name in sorted(all_block_names):
        present = {
            fname: blocks[block_name]
            for fname, blocks in blocks_by_file.items()
            if block_name in blocks
        }

        # ── 1. conflict check ─────────────────────────────────────────────────
        unique = {v.strip() for v in present.values()}
        if len(unique) > 1:
            lines = [f"  Block '{block_name}' has conflicting content:"]
            for fname, inner in present.items():
                preview = inner.strip()[:60].replace("\n", "↵")
                ellipsis = "…" if len(inner.strip()) > 60 else ""
                lines.append(f"    {fname}: {preview!r}{ellipsis}")
            conflicts.append("\n".join(lines))
            continue

        # ── 2. insert block into files that are missing it ────────────────────
        agreed_inner = next(iter(present.values()))
        for fname in doc_paths:
            if fname in present:
                continue
            current = modified.get(fname, contents[fname])
            modified[fname] = insert_block(current, block_name, agreed_inner)
            info(f"  Added block '{block_name}' to {fname}")

    # ── write + re-stage ──────────────────────────────────────────────────────
    for fname, new_content in modified.items():
        doc_paths[fname].write_text(new_content, encoding="utf-8")
        git_add(doc_paths[fname])
        info(f"Aligned and re-staged {fname}")

    # ── report ────────────────────────────────────────────────────────────────
    if conflicts:
        print(file=sys.stderr)
        err(f"{len(conflicts)} conflict(s) in doc files. Resolve before committing:\n")
        for block in conflicts:
            print(block, file=sys.stderr)
        print(file=sys.stderr)
        return 1

    if not modified:
        info("Doc files are aligned. ✓")

    return 0
