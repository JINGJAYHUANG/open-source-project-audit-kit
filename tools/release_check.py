#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    run(sys.executable, "-m", "compileall", "-q", "src", "tools", "tests")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    run(sys.executable, "-m", "open_source_audit", "validate", "--rubric-only", "--strict")
    run(sys.executable, "tools/generate_examples.py", "--check")
    for example in sorted((ROOT / "examples/synthetic").glob("*.audit.json")):
        run(sys.executable, "-m", "open_source_audit", "validate", str(example), "--strict")
        with tempfile.NamedTemporaryFile(suffix=".json") as handle:
            run(sys.executable, "-m", "open_source_audit", "score", str(example), "--format", "json", "--output", handle.name)
            payload = json.loads(Path(handle.name).read_text())
            if not payload.get("recommendation"):
                raise SystemExit(f"missing recommendation for {example}")
    run(sys.executable, "tools/check_docs.py", ".")
    run(sys.executable, "tools/check_workflows.py", ".")
    run(sys.executable, "tools/check_schema_parity.py")
    run(sys.executable, "tools/public_audit.py", ".")
    print("release gate passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
