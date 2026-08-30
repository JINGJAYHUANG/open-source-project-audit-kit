from __future__ import annotations

import copy
import json
import unittest

from open_source_audit.comparison import compare_audits
from open_source_audit.io import load_json, load_rubric
from open_source_audit.reporting import render
from open_source_audit.scoring import score_audit
from helpers import ROOT


class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.rubric = load_rubric()
        self.audit = load_json(ROOT / "examples/synthetic/steady-library.audit.json")
        self.result = score_audit(self.audit, self.rubric)

    def test_markdown_contains_boundaries(self):
        text = render(self.result, self.audit, "markdown")
        self.assertIn("not security certifications", text)
        self.assertIn("Weighted evidence coverage", text)
        self.assertIn("Base recommendation", text)
        self.assertIn("Required next verification", text)

    def test_html_escapes_context_and_shows_gates(self):
        audit = load_json(ROOT / "examples/synthetic/promising-agent.audit.json")
        audit["context"]["use_case"] = "<script>alert(1)</script>"
        result = score_audit(audit, self.rubric)
        text = render(result, audit, "html")
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn("Gate effects", text)
        self.assertIn("context_fit_confirmed", text)
        self.assertIn("Required next verification", text)
        self.assertNotIn("<script>", text)

    def test_csv_has_header(self):
        text = render(self.result, self.audit, "csv")
        self.assertTrue(text.startswith("criterion_id,dimension"))

    def test_json_is_parseable(self):
        json.loads(render(self.result, self.audit, "json"))

    def test_compare_detects_criterion_and_gate_changes(self):
        before = load_json(ROOT / "examples/synthetic/promising-agent.audit.json")
        after = load_json(ROOT / "examples/synthetic/steady-library.audit.json")
        after["repository"] = before["repository"]
        comparison = compare_audits(before, after, self.rubric)
        self.assertGreater(comparison["score_delta"], 0)
        self.assertTrue(comparison["criterion_changes"])
        self.assertTrue(comparison["gate_changes"])
        self.assertEqual(comparison["comparison_scope"], "same-repository")
        self.assertFalse(comparison["warnings"])

    def test_compare_detects_confidence_only_change(self):
        before = load_json(ROOT / "examples/synthetic/steady-library.audit.json")
        after = copy.deepcopy(before)
        after["ratings"]["provenance.identity"]["evidence"][0]["confidence"] = "low"
        comparison = compare_audits(before, after, self.rubric)
        changed = {item["criterion_id"] for item in comparison["criterion_changes"]}
        self.assertIn("provenance.identity", changed)

    def test_cross_repository_comparison_is_labeled(self):
        before = load_json(ROOT / "examples/synthetic/promising-agent.audit.json")
        after = load_json(ROOT / "examples/synthetic/steady-library.audit.json")
        comparison = compare_audits(before, after, self.rubric)
        self.assertFalse(comparison["same_repository"])
        self.assertTrue(comparison["warnings"])

    def test_compare_rejects_profile_mismatch(self):
        before = load_json(ROOT / "examples/synthetic/steady-library.audit.json")
        after = dict(before)
        after["profile"] = "innovation-scouting"
        with self.assertRaises(ValueError):
            compare_audits(before, after, self.rubric)


if __name__ == "__main__":
    unittest.main()
