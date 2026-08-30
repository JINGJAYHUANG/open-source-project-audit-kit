#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

SKIP = {".git", ".venv", "dist", "build", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {"", ".cff", ".csv", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{30,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{30,}\b"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "personal_email": re.compile(r"\b[A-Z0-9._%+-]+@(?!example\.(?:com|org|net)\b)[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "windows_home": re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"),
    "mac_home": re.compile(r"(?<![\w.-])/" + r"Users/[^/\s]+"),
    "linux_home": re.compile(r"(?<![\w.-])/" + r"home/[^/\s]+"),
}
FORBIDDEN = {
    "private_strategy_repository": "goal49" + "-cloud-morning",
    "private_incubator_repository": "JINGJAYHUANG/" + "try",
}


def scan(root: Path):
    findings = []
    count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP for part in path.relative_to(root).parts) or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        count += 1
        for number, line in enumerate(text.splitlines(), 1):
            for code, pattern in PATTERNS.items():
                match = pattern.search(line)
                if match:
                    findings.append((code, path.relative_to(root).as_posix(), number, match.group(0)[:100]))
            for code, marker in FORBIDDEN.items():
                if marker in line:
                    findings.append((code, path.relative_to(root).as_posix(), number, marker))
    return count, findings


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    count, findings = scan(root)
    if findings:
        print(f"public audit failed: {len(findings)} finding(s) in {count} file(s)")
        for item in findings:
            print(f"{item[0]} {item[1]}:{item[2]} {item[3]}")
        return 1
    print(f"public audit passed: {count} text file(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
