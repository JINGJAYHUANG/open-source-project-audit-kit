#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = []
    count = 0
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv", "build", "dist"} for part in path.relative_to(root).parts):
            continue
        count += 1
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                errors.append(f"{path.relative_to(root)} -> {target}")
    if errors:
        print("broken local documentation links:")
        print("\n".join(errors))
        return 1
    print(f"documentation check passed: {count} Markdown file(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
