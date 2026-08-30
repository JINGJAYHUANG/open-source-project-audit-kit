# Data dictionary

## Audit

- `audit_id`: stable lowercase identifier.
- `repository`: `owner/name` identity.
- `as_of`: absolute date for the evidence snapshot.
- `profile`: rubric profile ID.
- `context`: use case, environment, risk tolerance, and time budget.
- `ratings`: one exact entry for every criterion in the selected profile.
- `gates`: one exact entry for every gate applicable to the selected profile.
- `next_verification`: unresolved evidence tasks.

## Rating entry

- `state`: `observed`, `unknown`, or `not_applicable`.
- `rating`: integer 0–4 only when observed.
- `evidence`: required for observed ratings.
- `rationale`: required for not-applicable entries.
- `notes`: caveats and interpretation.

## Result

- `score`: conservative weighted score with unknowns earning zero.
- `observed_quality`: quality among observed criteria only.
- `coverage`: observed weight divided by applicable weight.
- `evidence_confidence`: confidence weighted by criterion weight and independence groups.
- `base_recommendation`: threshold result before gate caps.
- `recommendation`: final result after gate caps.
