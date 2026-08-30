from __future__ import annotations

import copy
import unittest

from open_source_audit.io import load_rubric
from open_source_audit.templates import blank_audit
from open_source_audit.validation import validate_audit, validate_rubric
from helpers import ROOT


class RubricTests(unittest.TestCase):
    def test_rubric_is_strictly_valid(self):
        report = validate_rubric(load_rubric(), strict=True)
        self.assertTrue(report.ok, report.as_dict())

    def test_profile_weights_equal_100(self):
        for profile in load_rubric()["profiles"].values():
            self.assertEqual(sum(item["weight"] for item in profile["criteria"]), 100)

    def test_packaged_rubric_matches_repository(self):
        self.assertEqual(
            (ROOT / "data/rubric.json").read_bytes(),
            (ROOT / "src/open_source_audit/data/rubric.json").read_bytes(),
        )

    def test_exact_profiles(self):
        self.assertEqual(
            set(load_rubric()["profiles"]),
            {"adoption-readiness", "innovation-scouting"},
        )

    def test_bad_confidence_order_is_rejected(self):
        rubric = copy.deepcopy(load_rubric())
        rubric["evidence_confidence"] = {"low": 0.8, "medium": 0.5, "high": 1.0}
        report = validate_rubric(rubric)
        self.assertTrue(any(item.code == "confidence_order" for item in report.issues))

    def test_duplicate_recommendation_label_is_rejected(self):
        rubric = copy.deepcopy(load_rubric())
        rubric["profiles"]["adoption-readiness"]["recommendation_order"][-1] = "pilot"
        report = validate_rubric(rubric)
        self.assertTrue(any(item.code == "recommendation_order" for item in report.issues))

    def test_non_monotonic_threshold_is_rejected(self):
        rubric = copy.deepcopy(load_rubric())
        rubric["profiles"]["adoption-readiness"]["thresholds"][1]["minimum_coverage"] = 0.95
        report = validate_rubric(rubric)
        self.assertTrue(any(item.code == "threshold_order" for item in report.issues))


class AuditValidationTests(unittest.TestCase):
    def setUp(self):
        self.rubric = load_rubric()
        self.audit = blank_audit(
            "example/project",
            "adoption-readiness",
            self.rubric,
            as_of="2026-08-30",
        )

    def test_blank_template_is_valid(self):
        self.assertTrue(validate_audit(self.audit, self.rubric, strict=True).ok)

    def test_observed_rating_requires_evidence(self):
        criterion_id = next(iter(self.audit["ratings"]))
        self.audit["ratings"][criterion_id] = {
            "state": "observed",
            "rating": 3,
            "evidence": [],
            "notes": "",
        }
        report = validate_audit(self.audit, self.rubric)
        self.assertTrue(any(item.code == "unsupported_rating" for item in report.issues))

    def test_unknown_rating_must_be_null(self):
        criterion_id = next(iter(self.audit["ratings"]))
        self.audit["ratings"][criterion_id]["rating"] = 2
        self.assertFalse(validate_audit(self.audit, self.rubric).ok)

    def test_na_requires_rationale(self):
        criterion_id = next(iter(self.audit["ratings"]))
        self.audit["ratings"][criterion_id] = {
            "state": "not_applicable",
            "rating": None,
            "evidence": [],
        }
        report = validate_audit(self.audit, self.rubric)
        self.assertTrue(any(item.code == "na_rationale" for item in report.issues))

    def test_pass_gate_requires_evidence(self):
        gate = next(iter(self.audit["gates"]))
        self.audit["gates"][gate] = {"status": "pass", "evidence": []}
        report = validate_audit(self.audit, self.rubric)
        self.assertTrue(any(item.code == "unsupported_gate" for item in report.issues))

    def test_missing_criterion_is_rejected(self):
        self.audit["ratings"].pop(next(iter(self.audit["ratings"])))
        self.assertFalse(validate_audit(self.audit, self.rubric).ok)

    def test_extra_criterion_is_rejected(self):
        self.audit["ratings"]["invented.score"] = {
            "state": "unknown",
            "rating": None,
            "evidence": [],
        }
        self.assertFalse(validate_audit(self.audit, self.rubric).ok)

    def test_bad_repository_identity_is_rejected(self):
        self.audit["repository"] = "not-a-repository"
        self.assertFalse(validate_audit(self.audit, self.rubric).ok)

    def test_future_evidence_is_rejected(self):
        criterion_id = next(iter(self.audit["ratings"]))
        self.audit["ratings"][criterion_id] = {
            "state": "observed",
            "rating": 3,
            "notes": "",
            "evidence": [
                {
                    "source_type": "repository_file",
                    "locator": "README.md",
                    "observed_at": "2026-08-31",
                    "summary": "Evidence dated after the audit boundary.",
                    "confidence": "high",
                }
            ],
        }
        report = validate_audit(self.audit, self.rubric)
        self.assertTrue(any(item.code == "future_evidence" for item in report.issues))

    def test_auditor_identity_is_required(self):
        self.audit.pop("auditor")
        self.assertFalse(validate_audit(self.audit, self.rubric).ok)

    def test_all_context_fields_are_required(self):
        self.audit["context"].pop("environment")
        report = validate_audit(self.audit, self.rubric)
        self.assertTrue(any(item.code == "context_field" for item in report.issues))

    def test_unknown_nested_field_is_warning_and_strict_error(self):
        criterion_id = next(iter(self.audit["ratings"]))
        self.audit["ratings"][criterion_id]["invented"] = True
        self.assertTrue(validate_audit(self.audit, self.rubric).ok)
        self.assertFalse(validate_audit(self.audit, self.rubric, strict=True).ok)

    def test_blank_independence_group_is_rejected(self):
        criterion_id = next(iter(self.audit["ratings"]))
        evidence = {
            "source_type": "repository_file",
            "locator": "README.md",
            "observed_at": "2026-08-30",
            "summary": "A sufficiently long evidence summary.",
            "confidence": "high",
            "independence_group": "",
        }
        self.audit["ratings"][criterion_id] = {
            "state": "observed",
            "rating": 3,
            "evidence": [evidence],
        }
        report = validate_audit(self.audit, self.rubric)
        self.assertTrue(any(item.code == "independence_group" for item in report.issues))

    def test_duplicate_evidence_is_warning_and_strict_error(self):
        criterion_id = next(iter(self.audit["ratings"]))
        evidence = {
            "source_type": "repository_file",
            "locator": "README.md",
            "observed_at": "2026-08-30",
            "summary": "A sufficiently long evidence summary.",
            "confidence": "high",
        }
        self.audit["ratings"][criterion_id] = {
            "state": "observed",
            "rating": 3,
            "evidence": [evidence, copy.deepcopy(evidence)],
        }
        self.assertTrue(validate_audit(self.audit, self.rubric).ok)
        self.assertFalse(validate_audit(self.audit, self.rubric, strict=True).ok)


if __name__ == "__main__":
    unittest.main()
