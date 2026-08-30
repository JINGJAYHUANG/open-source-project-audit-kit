# Open-Source Audit — synthetic-labs/abandoned-plugin

- Audit ID: `synthetic-abandoned-plugin-2026-08-30`
- As of: `2026-08-30`
- Profile: `adoption-readiness`
- Use case: Evaluate whether a synthetic abandoned plugin should be introduced into a production workstation.
- Conservative score: **10.00/100**
- Observed-quality score: **13.51/100**
- Weighted evidence coverage: **74.0%**
- Evidence confidence: **70.1%**
- Base recommendation: **avoid**
- Final recommendation: **avoid**

> Scores are decision aids, not security certifications, legal opinions, or guarantees of maintenance or adoption.

## Dimensions

| Dimension | Weight | Earned | Coverage |
|---|---:|---:|---:|
| Adoption | 4.0 | 1.00 | 100.0% |
| Architecture | 6.0 | 1.50 | 100.0% |
| Community | 7.0 | 0.00 | 100.0% |
| Dependencies | 6.0 | 0.00 | 100.0% |
| Documentation | 12.0 | 1.50 | 50.0% |
| Fit | 4.0 | 1.00 | 100.0% |
| License | 10.0 | 0.00 | 60.0% |
| Maintenance | 12.0 | 0.00 | 58.3% |
| Provenance | 10.0 | 3.75 | 100.0% |
| Quality | 14.0 | 0.00 | 50.0% |
| Security | 15.0 | 1.25 | 73.3% |

## Criteria

| Criterion | State | Rating | Weight | Earned | Evidence | Confidence |
|---|---|---:|---:|---:|---:|---:|
| `provenance.identity` | observed | 2 | 5.0 | 2.50 | 1 | 67.0% |
| `provenance.source_traceability` | observed | 1 | 5.0 | 1.25 | 1 | 67.0% |
| `license.spdx_clarity` | observed | 0 | 6.0 | 0.00 | 1 | 100.0% |
| `license.dependency_compatibility` | unknown | — | 4.0 | 0.00 | 0 | — |
| `maintenance.recency_response` | observed | 0 | 7.0 | 0.00 | 1 | 100.0% |
| `maintenance.bus_factor_governance` | unknown | — | 5.0 | 0.00 | 0 | — |
| `documentation.quickstart` | observed | 1 | 6.0 | 1.50 | 1 | 67.0% |
| `documentation.operational_limits` | unknown | — | 6.0 | 0.00 | 0 | — |
| `quality.tests_ci` | observed | 0 | 7.0 | 0.00 | 1 | 100.0% |
| `quality.release_reproducibility` | unknown | — | 7.0 | 0.00 | 0 | — |
| `security.policy_disclosure` | observed | 0 | 6.0 | 0.00 | 1 | 100.0% |
| `security.permission_surface` | observed | 1 | 5.0 | 1.25 | 1 | 34.0% |
| `security.supply_chain_controls` | unknown | — | 4.0 | 0.00 | 0 | — |
| `architecture.modularity_extensibility` | observed | 1 | 6.0 | 1.50 | 1 | 34.0% |
| `dependencies.hygiene_update_path` | observed | 0 | 6.0 | 0.00 | 1 | 67.0% |
| `community.support_governance` | observed | 0 | 7.0 | 0.00 | 1 | 67.0% |
| `adoption.evidence` | observed | 1 | 4.0 | 1.00 | 1 | 34.0% |
| `fit.integration_cost` | observed | 1 | 4.0 | 1.00 | 1 | 34.0% |

## Gate effects

- `license_permission_clear` = `fail` capped `avoid` to `avoid`.
- `no_unmitigated_critical_security_finding` = `unknown` capped `avoid` to `avoid`.
- `privileged_defaults_bounded` = `fail` capped `avoid` to `avoid`.
- `installation_reversible` = `unknown` capped `avoid` to `avoid`.
- `context_fit_confirmed` = `fail` capped `avoid` to `avoid`.

## Warnings

- provenance.identity: rating relies on one evidence item
- provenance.source_traceability: rating relies on one evidence item
- license.spdx_clarity: rating relies on one evidence item
- maintenance.recency_response: rating relies on one evidence item
- documentation.quickstart: rating relies on one evidence item
- quality.tests_ci: rating relies on one evidence item
- security.policy_disclosure: rating relies on one evidence item
- security.permission_surface: rating relies on one evidence item
- architecture.modularity_extensibility: rating relies on one evidence item
- dependencies.hygiene_update_path: rating relies on one evidence item
- community.support_governance: rating relies on one evidence item
- adoption.evidence: rating relies on one evidence item
- fit.integration_cost: rating relies on one evidence item

## Required next verification

- Do not install in the primary environment.
- Find a maintained alternative with a clear license.
