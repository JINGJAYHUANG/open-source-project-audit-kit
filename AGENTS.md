# Repository agent instructions

Preserve evidence-first behavior.

Before changing scoring or policy:

1. identify the decision problem;
2. update the canonical rubric, not only packaged copies;
3. add positive, boundary, and failure fixtures;
4. regenerate deterministic examples;
5. run `PYTHONPATH=src python tools/release_check.py`.

Never add credentials, private repository content, personal profiles, or real proprietary audit evidence. Do not weaken evidence requirements or hard gates merely to raise a project's score. The local collector must remain no-network and must not execute target-project code.
