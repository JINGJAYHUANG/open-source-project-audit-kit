# Extension guide

A new profile must:

1. have a stable lowercase ID;
2. define recommendation order and matching thresholds;
3. define positive integer criterion weights summing to exactly 100;
4. state a decision purpose distinct from other profiles;
5. define evidence expectations for every criterion;
6. add applicable hard gates where arithmetic should not override a blocker;
7. add synthetic positive, boundary, and failure fixtures;
8. pass strict rubric validation and all release gates.

Do not edit the scoring algorithm merely to achieve a preferred result for one project. Change the rubric transparently and version the methodology.
