# Scoring profiles

## Adoption Readiness

The default profile covers provenance, license, maintenance, documentation, tests and release quality, security, architecture, dependencies, community support, adoption evidence, and context-specific integration cost.

The recommendation labels are:

```text
avoid < watch < pilot < adopt
```

Thresholds also require minimum evidence coverage and confidence. Hard gates can only lower the recommendation.

## Innovation Scouting

This profile preserves a separate research-ranking logic:

- workflow delta: 25;
- engineering evidence: 20;
- practical usability: 20;
- maturity and risk control: 15;
- future leverage: 10;
- substantive novelty: 10.

The labels are:

```text
deprioritize < watch < investigate < prioritize
```

It is not an adoption verdict. A high scouting score should trigger investigation, not automatic installation.
