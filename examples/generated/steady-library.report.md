# Open-Source Audit — synthetic-labs/steady-library

- Audit ID: `synthetic-steady-library-2026-08-30`
- As of: `2026-08-30`
- Profile: `adoption-readiness`
- Use case: Evaluate a synthetic library for a reversible internal production dependency.
- Conservative score: **96.75/100**
- Observed-quality score: **96.75/100**
- Weighted evidence coverage: **100.0%**
- Evidence confidence: **100.0%**
- Base recommendation: **adopt**
- Final recommendation: **adopt**

> Scores are decision aids, not security certifications, legal opinions, or guarantees of maintenance or adoption.

## Dimensions

| Dimension | Weight | Earned | Coverage |
|---|---:|---:|---:|
| Adoption | 4.0 | 3.00 | 100.0% |
| Architecture | 6.0 | 6.00 | 100.0% |
| Community | 7.0 | 7.00 | 100.0% |
| Dependencies | 6.0 | 6.00 | 100.0% |
| Documentation | 12.0 | 12.00 | 100.0% |
| Fit | 4.0 | 3.00 | 100.0% |
| License | 10.0 | 10.00 | 100.0% |
| Maintenance | 12.0 | 10.75 | 100.0% |
| Provenance | 10.0 | 10.00 | 100.0% |
| Quality | 14.0 | 14.00 | 100.0% |
| Security | 15.0 | 15.00 | 100.0% |

## Criteria

| Criterion | State | Rating | Weight | Earned | Evidence | Confidence |
|---|---|---:|---:|---:|---:|---:|
| `provenance.identity` | observed | 4 | 5.0 | 5.00 | 1 | 100.0% |
| `provenance.source_traceability` | observed | 4 | 5.0 | 5.00 | 1 | 100.0% |
| `license.spdx_clarity` | observed | 4 | 6.0 | 6.00 | 1 | 100.0% |
| `license.dependency_compatibility` | observed | 4 | 4.0 | 4.00 | 1 | 100.0% |
| `maintenance.recency_response` | observed | 4 | 7.0 | 7.00 | 1 | 100.0% |
| `maintenance.bus_factor_governance` | observed | 3 | 5.0 | 3.75 | 1 | 100.0% |
| `documentation.quickstart` | observed | 4 | 6.0 | 6.00 | 1 | 100.0% |
| `documentation.operational_limits` | observed | 4 | 6.0 | 6.00 | 1 | 100.0% |
| `quality.tests_ci` | observed | 4 | 7.0 | 7.00 | 1 | 100.0% |
| `quality.release_reproducibility` | observed | 4 | 7.0 | 7.00 | 1 | 100.0% |
| `security.policy_disclosure` | observed | 4 | 6.0 | 6.00 | 1 | 100.0% |
| `security.permission_surface` | observed | 4 | 5.0 | 5.00 | 1 | 100.0% |
| `security.supply_chain_controls` | observed | 4 | 4.0 | 4.00 | 1 | 100.0% |
| `architecture.modularity_extensibility` | observed | 4 | 6.0 | 6.00 | 1 | 100.0% |
| `dependencies.hygiene_update_path` | observed | 4 | 6.0 | 6.00 | 1 | 100.0% |
| `community.support_governance` | observed | 4 | 7.0 | 7.00 | 1 | 100.0% |
| `adoption.evidence` | observed | 3 | 4.0 | 3.00 | 1 | 100.0% |
| `fit.integration_cost` | observed | 3 | 4.0 | 3.00 | 1 | 100.0% |

## Gate effects

- No gate lowered the base recommendation.

## Warnings

- provenance.identity: rating relies on one evidence item
- provenance.source_traceability: rating relies on one evidence item
- license.spdx_clarity: rating relies on one evidence item
- license.dependency_compatibility: rating relies on one evidence item
- maintenance.recency_response: rating relies on one evidence item
- maintenance.bus_factor_governance: rating relies on one evidence item
- documentation.quickstart: rating relies on one evidence item
- documentation.operational_limits: rating relies on one evidence item
- quality.tests_ci: rating relies on one evidence item
- quality.release_reproducibility: rating relies on one evidence item
- security.policy_disclosure: rating relies on one evidence item
- security.permission_surface: rating relies on one evidence item
- security.supply_chain_controls: rating relies on one evidence item
- architecture.modularity_extensibility: rating relies on one evidence item
- dependencies.hygiene_update_path: rating relies on one evidence item
- community.support_governance: rating relies on one evidence item
- adoption.evidence: rating relies on one evidence item
- fit.integration_cost: rating relies on one evidence item

## Required next verification

- Repeat the sandbox test on the actual target platform.
- Verify the next upstream release before production rollout.
