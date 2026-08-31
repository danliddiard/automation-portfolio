#!/usr/bin/env python3
"""Repo guard rails.

Two things break a controls portfolio quietly, so both are checked on every push:

1. A committed L5X that is not well-formed XML. Studio 5000 rejects it at import,
   which is the worst possible time to find out.
2. A relative link in a README that points at a file that moved or was never added.
   A portfolio with dead links reads as unmaintained.

Exits non-zero with a file:line for anything it finds.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "__pycache__", ".venv", "venv"}

# [text](target) -- ignores images only in the sense that ![...] also matches, which is fine
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def walk(*suffixes: str):
    for path in sorted(ROOT.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in suffixes:
            yield path


def check_xml(errors: list[str]) -> int:
    checked = 0
    for path in walk(".l5x", ".svg", ".xml"):
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"{path.relative_to(ROOT)}: not well-formed XML -- {exc}")
        else:
            checked += 1
    return checked


def check_links(errors: list[str]) -> int:
    checked = 0
    for path in walk(".md"):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in LINK.findall(line):
                if urlparse(target).scheme or target.startswith(("#", "mailto:")):
                    continue
                resolved = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                checked += 1
                if not resolved.exists():
                    errors.append(
                        f"{path.relative_to(ROOT)}:{lineno}: dead link -> {target}"
                    )
    return checked


def main() -> int:
    errors: list[str] = []
    n_xml = check_xml(errors)
    n_links = check_links(errors)

    for err in errors:
        print(f"FAIL  {err}", file=sys.stderr)

    print(f"{n_xml} XML/L5X file(s) parsed, {n_links} relative link(s) resolved.")
    if errors:
        print(f"{len(errors)} problem(s).", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
