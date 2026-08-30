# Hard gates

Hard gates prevent arithmetic averages from hiding decisive constraints.

## Adoption profile gates

- `license_permission_clear`: failure caps the result at `avoid`; unknown caps it at `watch`.
- `no_unmitigated_critical_security_finding`: failure caps at `avoid`; unknown caps at `pilot`.
- `privileged_defaults_bounded`: failure caps at `avoid`; unknown caps at `pilot`.
- `installation_reversible`: failure caps at `watch`; unknown caps at `pilot`.
- `context_fit_confirmed`: failure caps at `avoid`; unknown caps at `watch`.

A gate `pass` or `fail` requires evidence. `unknown` is explicit and carries no invented evidence. `not_applicable` requires a written rationale.

## Gate wording is scoped

“No unmitigated critical finding” means no such finding was identified in the defined evidence scope. It is not proof that none exists. Record the reviewed version, date, advisory sources, and analysis limits.
