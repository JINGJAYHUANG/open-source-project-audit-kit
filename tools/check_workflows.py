#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

RUN_BLOCK = re.compile(r"^(?P<indent>\s*)(?:-\s*)?run:\s*\|[-+]?\s*$")
HEREDOC = re.compile(r"(?:^|\s)python(?:[0-9.]*)?\s+-\s+<<-?['\"]?(?P<tag>[A-Za-z_][A-Za-z0-9_]*)['\"]?\s*$")
ACTION = re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*[^#\s]+@([^\s#]+)")
EXPRESSION = re.compile(r"\$\{\{.*?\}\}")


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def extract_run_blocks(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    blocks: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        match = RUN_BLOCK.match(lines[index])
        if not match:
            index += 1
            continue
        parent_indent = len(match.group("indent"))
        block_lines: list[str] = []
        start_line = index + 2
        index += 1
        while index < len(lines):
            line = lines[index]
            if line.strip() and _indent_width(line) <= parent_indent:
                break
            block_lines.append(line)
            index += 1
        nonblank = [_indent_width(line) for line in block_lines if line.strip()]
        content_indent = min(nonblank) if nonblank else parent_indent + 2
        normalized = "\n".join(
            line[content_indent:] if line.strip() else ""
            for line in block_lines
        ) + "\n"
        blocks.append((start_line, normalized))
    return blocks


def python_heredocs(script: str, *, label: str) -> list[str]:
    lines = script.splitlines()
    bodies: list[str] = []
    index = 0
    while index < len(lines):
        match = HEREDOC.search(lines[index])
        if not match:
            index += 1
            continue
        tag = match.group("tag")
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != tag:
            body.append(lines[index])
            index += 1
        if index >= len(lines):
            raise ValueError(f"{label}: unterminated Python heredoc {tag}")
        source = "\n".join(body) + "\n"
        compile(source, f"{label}:{tag}", "exec")
        bodies.append(source)
        index += 1
    return bodies


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        errors.append(f"{path}: file must end with a newline")
    if "\t" in text:
        errors.append(f"{path}: tabs are not allowed in workflow YAML")
    if not re.search(r"(?m)^name:\s*\S", text):
        errors.append(f"{path}: missing workflow name")
    if not re.search(r"(?m)^on:\s*(?:$|\S)", text):
        errors.append(f"{path}: missing on trigger")
    if not re.search(r"(?m)^jobs:\s*$", text):
        errors.append(f"{path}: missing jobs mapping")
    for reference in ACTION.findall(text):
        if not re.fullmatch(r"[0-9a-f]{40}", reference):
            errors.append(f"{path}: third-party action is not pinned to a 40-character SHA: {reference}")

    bash = shutil.which("bash")
    for start_line, script in extract_run_blocks(text):
        label = f"{path}:run@{start_line}"
        try:
            python_heredocs(script, label=label)
        except (SyntaxError, ValueError) as exc:
            errors.append(f"{label}: {exc}")
        if bash:
            sanitized = EXPRESSION.sub("GITHUB_EXPRESSION", script)
            with tempfile.NamedTemporaryFile("w", suffix=".sh", encoding="utf-8", delete=False) as handle:
                handle.write(sanitized)
                temporary = Path(handle.name)
            try:
                result = subprocess.run(
                    [bash, "-n", str(temporary)],
                    text=True,
                    capture_output=True,
                    timeout=10,
                )
                if result.returncode:
                    detail = (result.stderr or result.stdout).strip()
                    errors.append(f"{label}: bash syntax check failed: {detail}")
            finally:
                temporary.unlink(missing_ok=True)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate pinned actions and embedded shell/Python syntax in GitHub workflows.")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    workflow_dir = root / ".github" / "workflows"
    paths = sorted([*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")])
    if not paths:
        print("workflow check failed: no workflow files found")
        return 1
    errors: list[str] = []
    for path in paths:
        errors.extend(check_file(path))
    if errors:
        print(f"workflow check failed: {len(errors)} issue(s)")
        print("\n".join(errors))
        return 1
    print(f"workflow check passed: {len(paths)} workflow file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
