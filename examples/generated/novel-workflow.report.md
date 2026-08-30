# Open-Source Audit — synthetic-labs/novel-workflow

- Audit ID: `synthetic-novel-workflow-2026-08-30`
- As of: `2026-08-30`
- Profile: `innovation-scouting`
- Use case: Rank a synthetic workflow tool for a bounded technical investigation.
- Conservative score: **80.00/100**
- Observed-quality score: **80.00/100**
- Weighted evidence coverage: **100.0%**
- Evidence confidence: **81.8%**
- Base recommendation: **prioritize**
- Final recommendation: **prioritize**

> Scores are decision aids, not security certifications, legal opinions, or guarantees of maintenance or adoption.

## Dimensions

| Dimension | Weight | Earned | Coverage |
|---|---:|---:|---:|
| Engineering Evidence | 20.0 | 15.00 | 100.0% |
| Future Leverage | 10.0 | 10.00 | 100.0% |
| Maturity & Risk | 15.0 | 7.50 | 100.0% |
| Novelty | 10.0 | 7.50 | 100.0% |
| Practical Usability | 20.0 | 15.00 | 100.0% |
| Workflow Delta | 25.0 | 25.00 | 100.0% |

## Criteria

| Criterion | State | Rating | Weight | Earned | Evidence | Confidence |
|---|---|---:|---:|---:|---:|---:|
| `scouting.workflow_delta` | observed | 4 | 25.0 | 25.00 | 1 | 100.0% |
| `scouting.engineering_evidence` | observed | 3 | 20.0 | 15.00 | 1 | 100.0% |
| `scouting.practical_usability` | observed | 3 | 20.0 | 15.00 | 1 | 67.0% |
| `scouting.maturity_risk` | observed | 2 | 15.0 | 7.50 | 1 | 67.0% |
| `scouting.future_leverage` | observed | 4 | 10.0 | 10.00 | 1 | 67.0% |
| `scouting.novelty` | observed | 3 | 10.0 | 7.50 | 1 | 67.0% |

## Gate effects

- No gate lowered the base recommendation.

## Warnings

- scouting.workflow_delta: rating relies on one evidence item
- scouting.engineering_evidence: rating relies on one evidence item
- scouting.practical_usability: rating relies on one evidence item
- scouting.maturity_risk: rating relies on one evidence item
- scouting.future_leverage: rating relies on one evidence item
- scouting.novelty: rating relies on one evidence item

## Required next verification

- Run the core workflow in a disposable environment.
- Compare the mechanism with mature alternatives.
- Complete an adoption-readiness audit before any production use.
