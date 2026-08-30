from __future__ import annotations

import re
from datetime import date
from typing import Any

from .models import Issue, ValidationReport

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,127}$")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
EVIDENCE_TYPES = {
    "repository_file",
    "release",
    "commit",
    "issue_or_pr",
    "security_advisory",
    "package_registry",
    "independent_adoption",
    "sandbox_test",
    "manual_observation",
    "automated_observation",
    "other",
}
CONFIDENCE = {"low", "medium", "high"}
STATES = {"observed", "unknown", "not_applicable"}
GATE_STATUSES = {"pass", "fail", "unknown", "not_applicable"}
RATING_KEYS = {"state", "rating", "evidence", "notes", "rationale"}
GATE_KEYS = {"status", "evidence", "notes", "rationale"}
EVIDENCE_KEYS = {
    "source_type",
    "locator",
    "observed_at",
    "summary",
    "confidence",
    "independence_group",
}
CONTEXT_KEYS = ("use_case", "risk_tolerance", "environment", "time_budget")


def _valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_evidence(
    items: object,
    path: str,
    issues: list[Issue],
    *,
    maximum_date: str | None = None,
) -> None:
    if not isinstance(items, list):
        issues.append(Issue("error", "evidence_type", path, "evidence must be an array"))
        return
    maximum = date.fromisoformat(maximum_date) if _valid_date(maximum_date) else None
    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            issues.append(Issue("error", "evidence_item", item_path, "evidence item must be an object"))
            continue
        required = {"source_type", "locator", "observed_at", "summary", "confidence"}
        missing = sorted(required - set(item))
        if missing:
            issues.append(Issue("error", "evidence_fields", item_path, f"missing fields: {', '.join(missing)}"))
            continue
        extra = sorted(set(item) - EVIDENCE_KEYS)
        if extra:
            issues.append(Issue("warning", "evidence_unknown_fields", item_path, f"unrecognized fields: {', '.join(extra)}"))
        if item.get("source_type") not in EVIDENCE_TYPES:
            issues.append(Issue("error", "evidence_source_type", item_path, "unsupported source_type"))
        if not isinstance(item.get("locator"), str) or not item["locator"].strip():
            issues.append(Issue("error", "evidence_locator", item_path, "locator must be a non-empty string"))
        observed = item.get("observed_at")
        if not _valid_date(observed):
            issues.append(Issue("error", "evidence_date", item_path, "observed_at must be YYYY-MM-DD"))
        elif maximum is not None and date.fromisoformat(str(observed)) > maximum:
            issues.append(Issue("error", "future_evidence", item_path, "evidence date cannot be later than audit as_of"))
        if not isinstance(item.get("summary"), str) or len(item["summary"].strip()) < 12:
            issues.append(Issue("error", "evidence_summary", item_path, "summary must be at least 12 characters"))
        if item.get("confidence") not in CONFIDENCE:
            issues.append(Issue("error", "evidence_confidence", item_path, "confidence must be low, medium, or high"))
        group = item.get("independence_group")
        if group is not None and (not isinstance(group, str) or not group.strip()):
            issues.append(Issue("error", "independence_group", item_path, "independence_group must be a non-empty string when supplied"))
        key = (str(item.get("source_type")), str(item.get("locator")), str(item.get("observed_at")))
        if key in seen:
            issues.append(Issue("warning", "duplicate_evidence", item_path, "duplicate evidence locator and date"))
        seen.add(key)


def validate_rubric(rubric: dict[str, Any], *, strict: bool = False) -> ValidationReport:
    issues: list[Issue] = []
    if rubric.get("schema_version") != 1:
        issues.append(Issue("error", "schema_version", "schema_version", "rubric schema_version must be 1"))

    scale = rubric.get("rating_scale")
    if not isinstance(scale, dict) or set(scale) != {"0", "1", "2", "3", "4"}:
        issues.append(Issue("error", "rating_scale", "rating_scale", "rating scale must define exactly 0 through 4"))
    elif any(not isinstance(value, str) or len(value.strip()) < 12 for value in scale.values()):
        issues.append(Issue("error", "rating_scale_text", "rating_scale", "each rating anchor must be meaningful text"))

    confidence = rubric.get("evidence_confidence")
    if not isinstance(confidence, dict) or set(confidence) != CONFIDENCE:
        issues.append(Issue("error", "confidence_map", "evidence_confidence", "confidence map must define low, medium, and high"))
    else:
        values = []
        for key in ("low", "medium", "high"):
            value = confidence[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                issues.append(Issue("error", "confidence_value", f"evidence_confidence.{key}", "confidence value must be between 0 and 1"))
            else:
                values.append(float(value))
        if len(values) == 3 and not values[0] < values[1] < values[2]:
            issues.append(Issue("error", "confidence_order", "evidence_confidence", "confidence values must increase from low to high"))

    statuses = rubric.get("gate_statuses")
    if not isinstance(statuses, list) or set(statuses) != GATE_STATUSES or len(statuses) != len(GATE_STATUSES):
        issues.append(Issue("error", "gate_statuses", "gate_statuses", "gate statuses must define pass, fail, unknown, and not_applicable exactly once"))

    profiles = rubric.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        issues.append(Issue("error", "profiles", "profiles", "at least one profile is required"))
        return ValidationReport(tuple(issues))

    gates = rubric.get("gates")
    if not isinstance(gates, list):
        issues.append(Issue("error", "gates", "gates", "gates must be an array"))
        gates = []
    gate_ids: list[str] = []
    for index, gate in enumerate(gates):
        path = f"gates[{index}]"
        if not isinstance(gate, dict) or not ID_PATTERN.fullmatch(str(gate.get("id", ""))):
            issues.append(Issue("error", "gate_id", path, "invalid gate id"))
            continue
        gate_ids.append(gate["id"])
        if len(str(gate.get("question", "")).strip()) < 20:
            issues.append(Issue("error", "gate_question", path, "gate question is too short"))
        assigned = gate.get("profiles")
        if not isinstance(assigned, list) or not assigned or len(assigned) != len(set(assigned)):
            issues.append(Issue("error", "gate_profiles", path, "gate profiles must be a non-empty unique list"))
    if len(gate_ids) != len(set(gate_ids)):
        issues.append(Issue("error", "duplicate_gate", "gates", "gate ids must be unique"))

    for profile_id, profile in profiles.items():
        profile_path = f"profiles.{profile_id}"
        if not ID_PATTERN.fullmatch(profile_id):
            issues.append(Issue("error", "profile_id", profile_path, "invalid profile id"))
        if not isinstance(profile, dict):
            issues.append(Issue("error", "profile_type", profile_path, "profile must be an object"))
            continue
        if len(str(profile.get("title", "")).strip()) < 3:
            issues.append(Issue("error", "profile_title", profile_path, "profile title is required"))
        if len(str(profile.get("purpose", "")).strip()) < 20:
            issues.append(Issue("error", "profile_purpose", profile_path, "profile purpose is too short"))
        criteria = profile.get("criteria", [])
        if not isinstance(criteria, list) or not criteria:
            issues.append(Issue("error", "criteria", profile_path, "criteria are required"))
            continue
        ids: list[str] = []
        total = 0
        for index, criterion in enumerate(criteria):
            path = f"{profile_path}.criteria[{index}]"
            if not isinstance(criterion, dict):
                issues.append(Issue("error", "criterion_type", path, "criterion must be an object"))
                continue
            cid = str(criterion.get("id", ""))
            if not ID_PATTERN.fullmatch(cid):
                issues.append(Issue("error", "criterion_id", path, "invalid criterion id"))
            ids.append(cid)
            weight = criterion.get("weight")
            if isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0:
                issues.append(Issue("error", "weight", path, "weight must be a positive integer"))
            else:
                total += weight
            if len(str(criterion.get("dimension", "")).strip()) < 2:
                issues.append(Issue("error", "dimension", path, "criterion dimension is required"))
            if len(str(criterion.get("question", "")).strip()) < 20:
                issues.append(Issue("error", "question", path, "criterion question is too short"))
            expectations = criterion.get("evidence_expectations")
            if not isinstance(expectations, list) or not expectations or any(not isinstance(item, str) or len(item.strip()) < 3 for item in expectations):
                issues.append(Issue("error", "evidence_expectations", path, "criterion must define meaningful evidence expectations"))
        if len(ids) != len(set(ids)):
            issues.append(Issue("error", "duplicate_criterion", profile_path, "criterion ids must be unique"))
        if total != 100:
            issues.append(Issue("error", "weight_total", profile_path, f"weights must sum to 100, found {total}"))

        order = profile.get("recommendation_order", [])
        thresholds = profile.get("thresholds", [])
        if not isinstance(order, list) or not order or len(order) != len(set(order)) or any(not isinstance(item, str) or not item for item in order):
            issues.append(Issue("error", "recommendation_order", profile_path, "recommendation order must be a non-empty unique string list"))
            order = []
        if not isinstance(thresholds, list) or not thresholds:
            issues.append(Issue("error", "thresholds", profile_path, "thresholds are required"))
            thresholds = []
        labels = [item.get("label") for item in thresholds if isinstance(item, dict)]
        if len(labels) != len(thresholds) or len(labels) != len(set(labels)):
            issues.append(Issue("error", "threshold_labels", profile_path, "threshold labels must be unique and present"))
        if order and labels != list(reversed(order)):
            issues.append(Issue("error", "recommendations", profile_path, "thresholds must run from strongest to weakest and reverse recommendation_order"))

        previous = {"minimum_score": float("inf"), "minimum_coverage": float("inf"), "minimum_confidence": float("inf")}
        for index, threshold in enumerate(thresholds):
            path = f"{profile_path}.thresholds[{index}]"
            if not isinstance(threshold, dict):
                issues.append(Issue("error", "threshold_type", path, "threshold must be an object"))
                continue
            for key in previous:
                value = threshold.get(key)
                upper = 100 if key == "minimum_score" else 1
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= upper:
                    issues.append(Issue("error", "threshold_value", path, f"{key} is outside its valid range"))
                    continue
                if float(value) > previous[key]:
                    issues.append(Issue("error", "threshold_order", path, f"{key} must be non-increasing from strongest to weakest"))
                previous[key] = float(value)

    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            continue
        for profile_id in gate.get("profiles", []):
            if profile_id not in profiles:
                issues.append(Issue("error", "gate_profile", f"gates[{index}]", f"unknown profile: {profile_id}"))
                continue
            valid_labels = set(profiles[profile_id].get("recommendation_order", []))
            for key in ("fail_cap", "unknown_cap"):
                if key in gate and gate[key] not in valid_labels:
                    issues.append(Issue("error", "gate_cap", f"gates[{index}]", f"{key} is not a recommendation label for {profile_id}"))

    if strict:
        issues = [Issue("error", item.code, item.path, item.message) if item.severity == "warning" else item for item in issues]
    return ValidationReport(tuple(issues))


def validate_audit(audit: dict[str, Any], rubric: dict[str, Any], *, strict: bool = False) -> ValidationReport:
    issues: list[Issue] = []
    if audit.get("schema_version") != 1:
        issues.append(Issue("error", "schema_version", "schema_version", "audit schema_version must be 1"))
    profile_id = audit.get("profile")
    profiles = rubric.get("profiles", {})
    if profile_id not in profiles:
        issues.append(Issue("error", "profile", "profile", "unknown profile"))
        return ValidationReport(tuple(issues))
    if not ID_PATTERN.fullmatch(str(audit.get("audit_id", ""))):
        issues.append(Issue("error", "audit_id", "audit_id", "invalid audit_id"))
    if not REPOSITORY_PATTERN.fullmatch(str(audit.get("repository", ""))):
        issues.append(Issue("error", "repository", "repository", "repository must be owner/name"))
    if not _valid_date(audit.get("as_of")):
        issues.append(Issue("error", "as_of", "as_of", "as_of must be YYYY-MM-DD"))

    auditor = audit.get("auditor")
    if not isinstance(auditor, dict) or not str(auditor.get("type", "")).strip() or not str(auditor.get("name", "")).strip():
        issues.append(Issue("error", "auditor", "auditor", "auditor type and name are required"))

    context = audit.get("context")
    if not isinstance(context, dict):
        issues.append(Issue("error", "context", "context", "context must be an object"))
    else:
        for key in CONTEXT_KEYS:
            if not isinstance(context.get(key), str) or not context[key].strip():
                issues.append(Issue("error", "context_field", f"context.{key}", f"{key} is required"))

    criteria = profiles[profile_id]["criteria"]
    expected = {item["id"] for item in criteria}
    ratings = audit.get("ratings")
    if not isinstance(ratings, dict):
        issues.append(Issue("error", "ratings", "ratings", "ratings must be an object"))
        ratings = {}
    actual = set(ratings)
    for missing in sorted(expected - actual):
        issues.append(Issue("error", "missing_rating", f"ratings.{missing}", "criterion entry is missing"))
    for extra in sorted(actual - expected):
        issues.append(Issue("error", "unknown_rating", f"ratings.{extra}", "criterion is not in the selected profile"))
    for criterion in criteria:
        cid = criterion["id"]
        entry = ratings.get(cid)
        path = f"ratings.{cid}"
        if not isinstance(entry, dict):
            if entry is not None:
                issues.append(Issue("error", "rating_entry", path, "rating entry must be an object"))
            continue
        extra = sorted(set(entry) - RATING_KEYS)
        if extra:
            issues.append(Issue("warning", "rating_unknown_fields", path, f"unrecognized fields: {', '.join(extra)}"))
        state = entry.get("state")
        if state not in STATES:
            issues.append(Issue("error", "rating_state", path, "state must be observed, unknown, or not_applicable"))
            continue
        rating = entry.get("rating")
        evidence = entry.get("evidence", [])
        if state == "observed":
            if isinstance(rating, bool) or not isinstance(rating, int) or rating not in range(5):
                issues.append(Issue("error", "rating_value", path, "observed rating must be an integer from 0 to 4"))
            _validate_evidence(evidence, f"{path}.evidence", issues, maximum_date=audit.get("as_of"))
            if isinstance(evidence, list) and not evidence:
                issues.append(Issue("error", "unsupported_rating", path, "observed rating requires at least one evidence item"))
        else:
            if rating is not None:
                issues.append(Issue("error", "rating_null", path, "unknown and not_applicable ratings must be null"))
            if evidence not in ([], None):
                issues.append(Issue("warning", "unused_evidence", path, "non-observed criterion should not carry evidence"))
            if state == "not_applicable" and len(str(entry.get("rationale", "")).strip()) < 12:
                issues.append(Issue("error", "na_rationale", path, "not_applicable requires a rationale"))

    applicable_gate_order = [
        item["id"]
        for item in rubric.get("gates", [])
        if profile_id in item.get("profiles", [])
    ]
    applicable_gates = set(applicable_gate_order)
    gates = audit.get("gates")
    if not isinstance(gates, dict):
        issues.append(Issue("error", "gates", "gates", "gates must be an object"))
        gates = {}
    for missing in sorted(applicable_gates - set(gates)):
        issues.append(Issue("error", "missing_gate", f"gates.{missing}", "gate entry is missing"))
    for extra in sorted(set(gates) - applicable_gates):
        issues.append(Issue("error", "unknown_gate", f"gates.{extra}", "gate is not applicable to this profile"))
    for gate_id in applicable_gate_order:
        entry = gates.get(gate_id)
        path = f"gates.{gate_id}"
        if not isinstance(entry, dict):
            if entry is not None:
                issues.append(Issue("error", "gate_entry", path, "gate entry must be an object"))
            continue
        extra = sorted(set(entry) - GATE_KEYS)
        if extra:
            issues.append(Issue("warning", "gate_unknown_fields", path, f"unrecognized fields: {', '.join(extra)}"))
        if entry.get("status") not in rubric.get("gate_statuses", []):
            issues.append(Issue("error", "gate_status", path, "unsupported gate status"))
            continue
        status = entry["status"]
        evidence = entry.get("evidence", [])
        if status in {"pass", "fail"}:
            _validate_evidence(evidence, f"{path}.evidence", issues, maximum_date=audit.get("as_of"))
            if isinstance(evidence, list) and not evidence:
                issues.append(Issue("error", "unsupported_gate", path, "pass or fail requires evidence"))
        elif evidence not in ([], None):
            issues.append(Issue("warning", "unused_gate_evidence", path, "unknown or not_applicable gate should not carry evidence"))
        if status == "not_applicable" and len(str(entry.get("rationale", "")).strip()) < 12:
            issues.append(Issue("error", "gate_na_rationale", path, "not_applicable requires a rationale"))

    next_verification = audit.get("next_verification")
    if not isinstance(next_verification, list) or any(
        not isinstance(item, str) or len(item.strip()) < 12
        for item in next_verification
    ):
        issues.append(Issue("error", "next_verification", "next_verification", "must be an array of meaningful verification tasks"))

    if strict:
        issues = [Issue("error", item.code, item.path, item.message) if item.severity == "warning" else item for item in issues]
    return ValidationReport(tuple(issues))
