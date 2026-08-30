from __future__ import annotations

import copy
import unittest

from open_source_audit.io import load_json, load_rubric
from open_source_audit.scoring import score_audit
from helpers import ROOT


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.rubric = load_rubric()

    def example(self, name: str):
        return load_json(ROOT / "examples/synthetic" / name)

    def test_steady_example_is_adopt(self):
        result = score_audit(self.example("steady-library.audit.json"), self.rubric)
        self.assertEqual(result.recommendation, "adopt")
        self.assertEqual(result.coverage, 1.0)
        self.assertGreater(result.score, 90)

    def test_promising_example_is_gate_capped(self):
        result = score_audit(self.example("promising-agent.audit.json"), self.rubric)
        self.assertEqual(result.base_recommendation, "pilot")
        self.assertEqual(result.recommendation, "watch")
        self.assertTrue(result.gate_caps)

    def test_abandoned_example_is_avoid(self):
        result = score_audit(self.example("abandoned-plugin.audit.json"), self.rubric)
        self.assertEqual(result.recommendation, "avoid")

    def test_scouting_example_prioritizes_investigation_only(self):
        result = score_audit(self.example("novel-workflow.audit.json"), self.rubric)
        self.assertEqual(result.profile, "innovation-scouting")
        self.assertEqual(result.recommendation, "prioritize")
        self.assertNotIn(result.recommendation, {"adopt", "pilot"})

    def test_unknowns_reduce_conservative_score(self):
        audit = self.example("steady-library.audit.json")
        criterion_id = self.rubric["profiles"]["adoption-readiness"]["criteria"][0]["id"]
        full = score_audit(audit, self.rubric)
        audit["ratings"][criterion_id] = {
            "state": "unknown",
            "rating": None,
            "evidence": [],
            "notes": "removed",
        }
        reduced = score_audit(audit, self.rubric)
        self.assertLess(reduced.score, full.score)
        self.assertLess(reduced.coverage, full.coverage)

    def test_not_applicable_changes_denominator(self):
        audit = self.example("steady-library.audit.json")
        criterion_id = "adoption.evidence"
        audit["ratings"][criterion_id] = {
            "state": "not_applicable",
            "rating": None,
            "evidence": [],
            "rationale": "The synthetic internal-only use case has no adoption requirement.",
            "notes": "",
        }
        result = score_audit(audit, self.rubric)
        self.assertEqual(result.coverage, 1.0)

    def test_independence_groups_prevent_page_count_inflation(self):
        audit = self.example("steady-library.audit.json")
        criterion_id = "provenance.identity"
        entry = audit["ratings"][criterion_id]
        base = score_audit(audit, self.rubric)
        duplicate = copy.deepcopy(entry["evidence"][0])
        duplicate["locator"] += "?mirror=1"
        duplicate["confidence"] = "low"
        entry["evidence"].append(duplicate)
        after = score_audit(audit, self.rubric)
        self.assertEqual(base.evidence_confidence, after.evidence_confidence)

    def test_missing_independence_groups_do_not_imply_corroboration(self):
        audit = self.example("steady-library.audit.json")
        criterion_id = "provenance.identity"
        entry = audit["ratings"][criterion_id]
        for evidence in entry["evidence"]:
            evidence.pop("independence_group", None)
        duplicate = copy.deepcopy(entry["evidence"][0])
        duplicate["locator"] += "?another-page=1"
        duplicate["confidence"] = "low"
        entry["evidence"].append(duplicate)
        result = score_audit(audit, self.rubric)
        criterion = next(item for item in result.criteria if item.criterion_id == criterion_id)
        self.assertEqual(criterion.confidence, 1.0)

    def test_gate_effect_order_follows_rubric_not_input_order(self):
        audit = self.example("promising-agent.audit.json")
        audit["gates"] = dict(reversed(list(audit["gates"].items())))
        result = score_audit(audit, self.rubric)
        expected = [
            gate["id"]
            for gate in self.rubric["gates"]
            if audit["profile"] in gate["profiles"] and gate.get(f"{audit['gates'][gate['id']]['status']}_cap")
        ]
        self.assertEqual([item["gate"] for item in result.gate_caps], expected)

    def test_score_is_deterministic(self):
        audit = self.example("steady-library.audit.json")
        self.assertEqual(
            score_audit(audit, self.rubric).as_dict(),
            score_audit(audit, self.rubric).as_dict(),
        )


if __name__ == "__main__":
    unittest.main()
