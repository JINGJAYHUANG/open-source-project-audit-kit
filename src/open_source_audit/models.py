from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[Issue, ...]

    @property
    def errors(self) -> int:
        return sum(item.severity == "error" for item in self.issues)

    @property
    def warnings(self) -> int:
        return sum(item.severity == "warning" for item in self.issues)

    @property
    def ok(self) -> bool:
        return self.errors == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "issues": [item.as_dict() for item in self.issues],
        }


@dataclass(frozen=True)
class CriterionScore:
    criterion_id: str
    dimension: str
    weight: float
    state: str
    rating: int | None
    earned_points: float
    evidence_count: int
    confidence: float | None
    note: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuditScore:
    audit_id: str
    repository: str
    profile: str
    as_of: str
    score: float
    observed_quality: float
    coverage: float
    evidence_confidence: float
    recommendation: str
    base_recommendation: str
    gate_caps: tuple[dict[str, str], ...]
    dimensions: dict[str, dict[str, float]]
    criteria: tuple[CriterionScore, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "audit_id": self.audit_id,
            "repository": self.repository,
            "profile": self.profile,
            "as_of": self.as_of,
            "score": self.score,
            "observed_quality": self.observed_quality,
            "coverage": self.coverage,
            "evidence_confidence": self.evidence_confidence,
            "recommendation": self.recommendation,
            "base_recommendation": self.base_recommendation,
            "gate_caps": list(self.gate_caps),
            "dimensions": self.dimensions,
            "criteria": [item.as_dict() for item in self.criteria],
            "warnings": list(self.warnings),
        }
