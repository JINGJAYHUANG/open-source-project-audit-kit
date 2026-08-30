#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from open_source_audit.validation import CONFIDENCE, EVIDENCE_TYPES, GATE_STATUSES, STATES


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    audit = json.loads((root / "schemas/audit.schema.json").read_text(encoding="utf-8"))
    rubric = json.loads((root / "schemas/rubric.schema.json").read_text(encoding="utf-8"))
    result = json.loads((root / "schemas/result.schema.json").read_text(encoding="utf-8"))

    errors: list[str] = []
    evidence_enum = set(audit["$defs"]["evidence"]["properties"]["source_type"]["enum"])
    if evidence_enum != EVIDENCE_TYPES:
        errors.append("audit schema evidence source types differ from semantic validation")
    state_enum = set(audit["$defs"]["rating"]["properties"]["state"]["enum"])
    if state_enum != STATES:
        errors.append("audit schema rating states differ from semantic validation")
    gate_enum = set(audit["$defs"]["gate"]["properties"]["status"]["enum"])
    if gate_enum != GATE_STATUSES:
        errors.append("audit schema gate statuses differ from semantic validation")
    confidence_enum = set(audit["$defs"]["evidence"]["properties"]["confidence"]["enum"])
    if confidence_enum != CONFIDENCE:
        errors.append("audit schema confidence levels differ from semantic validation")
    if set(rubric["properties"]["rating_scale"]["required"]) != {"0", "1", "2", "3", "4"}:
        errors.append("rubric schema does not require all five rating anchors")
    for field in ("score", "coverage", "evidence_confidence", "recommendation", "base_recommendation"):
        if field not in result["required"]:
            errors.append(f"result schema does not require {field}")

    if errors:
        print("schema parity check failed:")
        print("\n".join(f"- {item}" for item in errors))
        return 1
    print("schema parity check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
