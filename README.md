# Open Source Project Audit Kit

Evidence-first, profile-aware due diligence for deciding whether an open-source repository should be **adopted, piloted, watched, or avoided**.

The kit separates four things that are often collapsed into one misleading score:

1. **Observed quality** — how strong the rated criteria appear.
2. **Evidence coverage** — how much of the weighted rubric was actually examined.
3. **Evidence confidence** — how traceable and independent the supporting evidence is.
4. **Hard gates** — license, critical security, privileged defaults, reversibility, and context fit.

A high score cannot override a failed license or security gate. Stars are not treated as proof of adoption, safety, or fit.

## What is included

- two versioned scoring profiles: `adoption-readiness` and `innovation-scouting`;
- 18 adoption criteria and 6 innovation-scouting criteria, each weighted to 100;
- explicit evidence objects with dates, source types, confidence, and independence groups;
- fail-closed validation for unsupported ratings and incomplete gate records;
- conservative scoring in which unknown weighted criteria earn zero rather than disappearing;
- a no-network local collector that produces provisional observations, not a security verdict;
- deterministic Markdown, HTML, JSON, and spreadsheet-safe CSV reports;
- audit-to-audit comparison;
- three adoption examples plus one innovation-scouting example;
- Python 3.11–3.13 CI, public-boundary scanning, and reproducible release artifacts.

## Five-minute start

```bash
python -m pip install -e .

oss-audit validate --rubric-only --strict
oss-audit score examples/synthetic/steady-library.audit.json --format markdown
```

Create a complete audit template:

```bash
oss-audit init owner/project audit.json   --profile adoption-readiness   --as-of 2026-08-30
```

Create a provisional offline inventory from a local checkout:

```bash
oss-audit collect-local ./project   --repository owner/project   --output local.audit.json   --as-of 2026-08-30
```

The collector intentionally leaves adoption, current advisories, maintainer response, dependency-license compatibility, and context fit unresolved when local files cannot establish them.

## Score semantics

For each applicable criterion with weight \(w_i\) and rating \(r_i \in \{0,1,2,3,4\}\):

```text
earned points = w_i × r_i / 4
conservative score = sum(earned points) / sum(applicable weights) × 100
coverage = sum(observed weights) / sum(applicable weights)
observed quality = sum(earned points) / sum(observed weights) × 100
```

Unknown criteria remain in the denominator and therefore cannot inflate the conservative score. `not_applicable` requires a rationale and is removed from the denominator.

## Repository map

```text
src/open_source_audit/    scoring, validation, collector, reports, CLI
 data/rubric.json         canonical profile and gate catalog
schemas/                  JSON Schemas for audits, rubric, and results
examples/synthetic/       four fictional, public-safe audit cases
docs/                     methodology, evidence, gates, threat model, usage
tests/                    unit, integration, CLI, collector, and publication tests
tools/                    release gate, documentation check, public audit
.github/workflows/        pinned-SHA CI and release workflows
```

## Boundaries

This repository does **not** provide:

- legal advice or license compatibility certification;
- a security audit, vulnerability guarantee, or malware verdict;
- automatic claims about maintainer intent or future support;
- investment advice or expected-return forecasts;
- proof of adoption based on stars, forks, downloads, or marketing alone;
- access to private repositories, tokens, personal profiles, or production systems.

See [methodology](docs/methodology.md), [evidence model](docs/evidence-model.md), [hard gates](docs/hard-gates.md), and the [Chinese overview](docs/README.zh-CN.md).
