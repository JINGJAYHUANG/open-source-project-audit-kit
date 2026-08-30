#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_source_audit.io import load_json, load_rubric
from open_source_audit.reporting import render
from open_source_audit.scoring import score_audit

ROOT = Path(__file__).resolve().parents[1]


def generated_payloads() -> dict[Path, str]:
    rubric = load_rubric()
    outputs: dict[Path, str] = {}
    for audit_path in sorted((ROOT / "examples/synthetic").glob("*.audit.json")):
        audit = load_json(audit_path)
        result = score_audit(audit, rubric)
        stem = audit_path.name.removesuffix(".audit.json")
        outputs[ROOT / "examples/generated" / f"{stem}.result.json"] = json.dumps(
            result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n"
        outputs[ROOT / "examples/generated" / f"{stem}.report.md"] = render(
            result, audit, "markdown"
        )
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches = []
    for path, content in generated_payloads().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                mismatches.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print(path.relative_to(ROOT))
    if mismatches:
        print("generated example drift:")
        print("\n".join(mismatches))
        return 1
    if args.check:
        print("generated examples are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
