# Architecture

```text
rubric.json
    ├── profiles and thresholds
    ├── criteria and weights
    └── hard-gate caps
            ↓
audit.json
    ├── decision context
    ├── criterion states and evidence
    ├── gate states and evidence
    └── next-verification tasks
            ↓
semantic validator
            ↓
scoring engine
    ├── conservative score
    ├── observed quality
    ├── weighted coverage
    ├── evidence confidence
    └── gate-capped recommendation
            ↓
JSON / Markdown / HTML / CSV / comparison
```

## Module boundaries

- `io.py` owns deterministic JSON loading and packaged-rubric access.
- `validation.py` enforces schema-like semantic rules that plain JSON Schema cannot express, including exact criterion sets and evidence requirements.
- `scoring.py` contains pure, deterministic arithmetic and recommendation caps.
- `collector.py` performs a bounded, no-network local inspection and never executes target-project code.
- `reporting.py` renders escaped, deterministic outputs.
- `comparison.py` compares two validated audit results without changing either source.
- `cli.py` is a thin interface over the modules.

The scorer has no network, filesystem, subprocess, or clock dependency. The collector is isolated because its observations are weaker and more environment-dependent than the scoring logic.
