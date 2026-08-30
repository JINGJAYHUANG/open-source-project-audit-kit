# Local collector

`oss-audit collect-local` performs a deterministic, no-network inspection of a local checkout. It inventories README, license and dependency files, tests, documentation, workflows, package metadata, recent local Git history, and selected workflow controls.

It can provisionally rate objective file-presence criteria, but it deliberately leaves these areas unresolved when local files cannot establish them:

- current upstream maintenance and issue response;
- security advisories and code-level vulnerabilities;
- dependency-license compatibility;
- real downstream adoption;
- actual installation cleanup;
- fit for the evaluator's environment.

The generated document is a starting point. Its `auditor.type` is `automated-local-collector`, and each generated observation says that manual confirmation is required.
