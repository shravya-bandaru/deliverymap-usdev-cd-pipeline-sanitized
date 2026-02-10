#!/usr/bin/env python3
"""Replace <{VAR}> tokens in files with environment variables."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"<\{([A-Za-z0-9_]+)\}>")


def replace_tokens(text: str) -> str:
    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        return os.environ.get(key, "")

    return TOKEN_RE.sub(_sub, text)


def process_file(path: Path) -> None:
    if not path.exists():
        print(f"[replace-tokens] Skipping missing file: {path}")
        return

    original = path.read_text(encoding="utf-8")
    updated = replace_tokens(original)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"[replace-tokens] Updated: {path}")
    else:
        print(f"[replace-tokens] No changes: {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: replace-tokens.py <file1> [file2 ...]")
        sys.exit(0)

    for arg in sys.argv[1:]:
        process_file(Path(arg))
