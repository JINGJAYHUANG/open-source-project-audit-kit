# Interpreting results

A result should be read in this order:

1. hard-gate effects;
2. evidence coverage;
3. evidence confidence;
4. dimension weaknesses;
5. conservative score;
6. recommendation label;
7. next-verification list.

A repository with an observed-quality score of 90 but coverage of 30% is not a 90-point repository. The conservative score and gate caps intentionally prevent that interpretation.

## Recommended language

Use:

> The scoped public evidence supports a bounded pilot as of 2026-08-30, subject to the unresolved license and context-fit checks listed below.

Avoid:

> No risks were found, so the project is safe and production-ready.

## Stars and downloads

Popularity can be an adoption signal, but it is not independent proof of maintainability, license compatibility, security, or fit. Record what the metric measures, its date, and whether a second source establishes actual use.
