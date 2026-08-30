# Evidence model

Each evidence object records:

- `source_type` — repository file, release, commit, issue/PR, advisory, registry, adoption evidence, sandbox test, or observation;
- `locator` — a stable path, URL, tag, commit, or artifact identifier;
- `observed_at` — absolute retrieval or observation date;
- `summary` — what the evidence actually establishes;
- `confidence` — `low`, `medium`, or `high`;
- `independence_group` — optional source family used to avoid double-counting multiple pages controlled by the same party.

## Source independence

Two URLs are not automatically two independent sources. Documentation, a release post, and a maintainer blog can belong to one independence group. Independent adoption evidence should come from a downstream project, operator, institution, or reproducible external test.

## Evidence does not inherit conclusions

A `SECURITY.md` file supports the claim that a reporting policy exists. It does not prove that the code is secure. A green CI badge supports the claim that a workflow passed at a specific commit. It does not prove production reliability.

## Unknown is a valid outcome

Use `unknown` when the scoped evidence does not establish a rating. Do not convert missing evidence into a neutral score. Unknowns stay visible and reduce coverage.
