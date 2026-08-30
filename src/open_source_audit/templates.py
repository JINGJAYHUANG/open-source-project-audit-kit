from __future__ import annotations

from datetime import date
from typing import Any


def blank_audit(repository: str, profile_id: str, rubric: dict[str, Any], *, as_of: str | None = None) -> dict[str, Any]:
    profile = rubric["profiles"][profile_id]
    observed_at = as_of or date.today().isoformat()
    ratings = {
        item["id"]: {"state": "unknown", "rating": None, "evidence": [], "notes": "Evidence not yet collected."}
        for item in profile["criteria"]
    }
    gates = {
        item["id"]: {"status": "unknown", "evidence": [], "notes": "Gate not yet resolved."}
        for item in rubric.get("gates", []) if profile_id in item.get("profiles", [])
    }
    return {
        "schema_version": 1,
        "audit_id": f"audit-{repository.replace('/', '-').lower()}-{observed_at}",
        "repository": repository,
        "as_of": observed_at,
        "profile": profile_id,
        "auditor": {"type": "human-led", "name": "replace-me"},
        "context": {"use_case": "Replace with the decision this audit must support.", "risk_tolerance": "replace-me", "environment": "replace-me", "time_budget": "replace-me"},
        "ratings": ratings,
        "gates": gates,
        "next_verification": ["Replace unknowns with dated, traceable evidence before relying on the recommendation."],
    }
