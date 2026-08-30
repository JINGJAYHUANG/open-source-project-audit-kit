from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import AuditScore, CriterionScore
from .validation import validate_audit


def _criterion_confidence(entry: dict[str, Any], mapping: dict[str, float]) -> float:
    groups: dict[str, list[float]] = defaultdict(list)
    for evidence in entry.get("evidence", []):
        # Missing source-family metadata is uncertainty, not independent corroboration.
        group = str(evidence.get("independence_group") or "unspecified")
        groups[group].append(float(mapping[evidence["confidence"]]))
    if not groups:
        return 0.0
    # Multiple pages from the same owner or source family do not create independent corroboration.
    independent_scores = [max(values) for values in groups.values()]
    return sum(independent_scores) / len(independent_scores)


def _base_recommendation(profile: dict[str, Any], score: float, coverage: float, confidence: float) -> str:
    for threshold in profile["thresholds"]:
        if (
            score >= threshold["minimum_score"]
            and coverage >= threshold["minimum_coverage"]
            and confidence >= threshold["minimum_confidence"]
        ):
            return threshold["label"]
    return profile["recommendation_order"][0]


def _cap_label(label: str, cap: str, order: list[str]) -> str:
    return order[min(order.index(label), order.index(cap))]


def score_audit(audit: dict[str, Any], rubric: dict[str, Any]) -> AuditScore:
    validation = validate_audit(audit, rubric, strict=True)
    if not validation.ok:
        detail = "; ".join(f"{x.code}@{x.path}: {x.message}" for x in validation.issues)
        raise ValueError(f"audit validation failed: {detail}")
    profile_id = audit["profile"]
    profile = rubric["profiles"][profile_id]
    confidence_map = rubric["evidence_confidence"]

    applicable_weight = 0.0
    observed_weight = 0.0
    earned = 0.0
    confidence_weighted = 0.0
    scores: list[CriterionScore] = []
    dimensions = defaultdict(lambda: {"weight": 0.0, "earned_points": 0.0, "observed_weight": 0.0})
    warnings: list[str] = []

    for criterion in profile["criteria"]:
        cid = criterion["id"]
        entry = audit["ratings"][cid]
        weight = float(criterion["weight"])
        state = entry["state"]
        rating = entry.get("rating")
        evidence_count = len(entry.get("evidence", [])) if state == "observed" else 0
        criterion_confidence = None
        earned_points = 0.0
        if state != "not_applicable":
            applicable_weight += weight
            dimensions[criterion["dimension"]]["weight"] += weight
        if state == "observed":
            observed_weight += weight
            dimensions[criterion["dimension"]]["observed_weight"] += weight
            earned_points = weight * int(rating) / 4.0
            earned += earned_points
            dimensions[criterion["dimension"]]["earned_points"] += earned_points
            criterion_confidence = _criterion_confidence(entry, confidence_map)
            confidence_weighted += weight * criterion_confidence
            if evidence_count == 1:
                warnings.append(f"{cid}: rating relies on one evidence item")
        scores.append(CriterionScore(
            criterion_id=cid,
            dimension=criterion["dimension"],
            weight=weight,
            state=state,
            rating=rating,
            earned_points=round(earned_points, 4),
            evidence_count=evidence_count,
            confidence=round(criterion_confidence, 4) if criterion_confidence is not None else None,
            note=str(entry.get("notes", "")),
        ))

    score = 0.0 if applicable_weight == 0 else earned / applicable_weight * 100.0
    observed_quality = 0.0 if observed_weight == 0 else earned / observed_weight * 100.0
    coverage = 0.0 if applicable_weight == 0 else observed_weight / applicable_weight
    evidence_confidence = 0.0 if observed_weight == 0 else confidence_weighted / observed_weight
    base = _base_recommendation(profile, score, coverage, evidence_confidence)
    recommendation = base
    gate_caps: list[dict[str, str]] = []
    order = profile["recommendation_order"]
    applicable_gates = [
        item
        for item in rubric.get("gates", [])
        if profile_id in item.get("profiles", [])
    ]
    for gate in applicable_gates:
        gate_id = gate["id"]
        entry = audit["gates"][gate_id]
        status = entry["status"]
        cap = gate.get(f"{status}_cap")
        if cap:
            before = recommendation
            recommendation = _cap_label(recommendation, cap, order)
            gate_caps.append({"gate": gate_id, "status": status, "cap": cap, "before": before, "after": recommendation})

    dimension_output: dict[str, dict[str, float]] = {}
    for name, values in sorted(dimensions.items()):
        weight = values["weight"]
        dimension_output[name] = {
            "weight": round(weight, 4),
            "earned_points": round(values["earned_points"], 4),
            "coverage": round(0.0 if weight == 0 else values["observed_weight"] / weight, 4),
        }
    if coverage < 0.60:
        warnings.append("coverage is below 60%; treat the recommendation as evidence-limited")
    if evidence_confidence < 0.55:
        warnings.append("evidence confidence is below 55%; independent verification is limited")

    return AuditScore(
        audit_id=audit["audit_id"],
        repository=audit["repository"],
        profile=profile_id,
        as_of=audit["as_of"],
        score=round(score, 2),
        observed_quality=round(observed_quality, 2),
        coverage=round(coverage, 4),
        evidence_confidence=round(evidence_confidence, 4),
        recommendation=recommendation,
        base_recommendation=base,
        gate_caps=tuple(gate_caps),
        dimensions=dimension_output,
        criteria=tuple(scores),
        warnings=tuple(dict.fromkeys(warnings)),
    )
