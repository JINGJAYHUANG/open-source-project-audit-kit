from __future__ import annotations

from typing import Any

from .scoring import score_audit


def compare_audits(
    before: dict[str, Any],
    after: dict[str, Any],
    rubric: dict[str, Any],
) -> dict[str, Any]:
    left = score_audit(before, rubric)
    right = score_audit(after, rubric)
    if left.profile != right.profile:
        raise ValueError("audits must use the same profile")

    left_map = {item.criterion_id: item for item in left.criteria}
    right_map = {item.criterion_id: item for item in right.criteria}
    criterion_changes = []
    for criterion_id in sorted(left_map):
        previous = left_map[criterion_id]
        current = right_map[criterion_id]
        before_state = (
            previous.state,
            previous.rating,
            previous.evidence_count,
            previous.confidence,
            previous.earned_points,
        )
        after_state = (
            current.state,
            current.rating,
            current.evidence_count,
            current.confidence,
            current.earned_points,
        )
        if before_state != after_state:
            criterion_changes.append(
                {
                    "criterion_id": criterion_id,
                    "before": {
                        "state": previous.state,
                        "rating": previous.rating,
                        "evidence_count": previous.evidence_count,
                        "confidence": previous.confidence,
                    },
                    "after": {
                        "state": current.state,
                        "rating": current.rating,
                        "evidence_count": current.evidence_count,
                        "confidence": current.confidence,
                    },
                    "earned_delta": round(current.earned_points - previous.earned_points, 4),
                }
            )

    gate_ids = sorted(set(before.get("gates", {})) | set(after.get("gates", {})))
    gate_changes = []
    for gate_id in gate_ids:
        previous = before.get("gates", {}).get(gate_id, {})
        current = after.get("gates", {}).get(gate_id, {})
        before_summary = {
            "status": previous.get("status"),
            "evidence_count": len(previous.get("evidence", [])),
        }
        after_summary = {
            "status": current.get("status"),
            "evidence_count": len(current.get("evidence", [])),
        }
        if before_summary != after_summary:
            gate_changes.append(
                {
                    "gate_id": gate_id,
                    "before": before_summary,
                    "after": after_summary,
                }
            )

    same_repository = left.repository == right.repository
    return {
        "schema_version": 1,
        "comparison_scope": "same-repository" if same_repository else "cross-repository",
        "same_repository": same_repository,
        "repository_before": left.repository,
        "repository_after": right.repository,
        "as_of_before": left.as_of,
        "as_of_after": right.as_of,
        "profile": left.profile,
        "score_before": left.score,
        "score_after": right.score,
        "score_delta": round(right.score - left.score, 2),
        "coverage_delta": round(right.coverage - left.coverage, 4),
        "confidence_delta": round(right.evidence_confidence - left.evidence_confidence, 4),
        "base_recommendation_before": left.base_recommendation,
        "base_recommendation_after": right.base_recommendation,
        "recommendation_before": left.recommendation,
        "recommendation_after": right.recommendation,
        "criterion_changes": criterion_changes,
        "gate_changes": gate_changes,
        "warnings": (
            []
            if same_repository
            else [
                "This is a cross-repository comparison; score deltas are not a longitudinal change claim."
            ]
        ),
    }
