from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT


def run_cli(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "open_source_audit", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def load_script(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CliTests(unittest.TestCase):
    def test_rubric_validation_command(self):
        result = run_cli("validate", "--rubric-only", "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_score_command(self):
        result = run_cli(
            "score",
            "examples/synthetic/steady-library.audit.json",
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["recommendation"], "adopt")

    def test_init_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "audit.json"
            result = run_cli(
                "init",
                "example/project",
                str(target),
                "--as-of",
                "2026-08-30",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.is_file())
            self.assertEqual(run_cli("validate", str(target), "--strict").returncode, 0)

    def test_compare_command(self):
        result = run_cli(
            "compare",
            "examples/synthetic/promising-agent.audit.json",
            "examples/synthetic/steady-library.audit.json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["score_delta"], 0)
        self.assertEqual(payload["comparison_scope"], "cross-repository")
        self.assertTrue(payload["warnings"])

    def test_rubric_inspection(self):
        result = run_cli("rubric", "profiles")
        self.assertEqual(result.returncode, 0)
        self.assertIn("adoption-readiness", result.stdout)


class PublicationTests(unittest.TestCase):
    def test_json_files_end_with_newline(self):
        for path in ROOT.rglob("*.json"):
            if ".git" not in path.parts:
                self.assertTrue(path.read_bytes().endswith(b"\n"), path)

    def test_public_audit_passes_repository(self):
        module = load_script("public_audit", "tools/public_audit.py")
        count, findings = module.scan(ROOT)
        self.assertGreater(count, 30)
        self.assertEqual(findings, [])

    def test_public_audit_detects_synthetic_token(self):
        module = load_script("public_audit_token", "tools/public_audit.py")
        with tempfile.TemporaryDirectory() as tmp:
            token = "gh" + "p_" + "A" * 36
            (Path(tmp) / "sample.txt").write_text(token)
            _, findings = module.scan(Path(tmp))
            self.assertTrue(any(item[0] == "github_token" for item in findings))

    def test_docs_check(self):
        result = subprocess.run(
            [sys.executable, "tools/check_docs.py", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_workflow_check(self):
        result = subprocess.run(
            [sys.executable, "tools/check_workflows.py", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_workflow_check_rejects_broken_embedded_python(self):
        module = load_script("workflow_check", "tools/check_workflows.py")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.yml"
            path.write_text(
                "name: Broken\non:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: |\n          python - <<'PY'\n"
                "          value = 'unterminated\n          PY\n",
                encoding="utf-8",
            )
            errors = module.check_file(path)
            self.assertTrue(any("unterminated string literal" in item for item in errors))

    def test_schema_parity(self):
        result = subprocess.run(
            [sys.executable, "tools/check_schema_parity.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generated_examples_are_current(self):
        result = subprocess.run(
            [sys.executable, "tools/generate_examples.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_release_workflow_is_version_driven_and_retry_safe(self):
        text = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn("release/v*", text)
        self.assertIn("origin/main", text)
        self.assertIn("criteria_by_profile", text)
        self.assertIn("sha256sum -c SHA256SUMS.txt", text)
        self.assertIn("gh release upload", text)
        self.assertIn("--clobber", text)
        self.assertIn("docs/release-notes/${VERSION}.md", text)
        self.assertNotIn("curl | sh", text)
        self.assertNotIn("'synthetic_examples': 4", text)


if __name__ == "__main__":
    unittest.main()
