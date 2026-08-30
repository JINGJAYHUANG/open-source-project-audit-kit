# Release checklist

- [ ] profile weights sum to exactly 100;
- [ ] all observed ratings and pass/fail gates have dated evidence;
- [ ] unknowns remain visible and are not silently removed from the denominator;
- [ ] gate caps and recommendation thresholds have regression tests;
- [ ] synthetic examples and generated reports are current;
- [ ] local collector performs no network request and executes no target code;
- [ ] documentation links, workflow syntax, schema parity, and public-boundary scan pass;
- [ ] Python 3.11, 3.12, and 3.13 pass;
- [ ] two independently built Wheels are byte-identical;
- [ ] release tag points to the tested `main` commit;
- [ ] release assets include source archives, Wheel, SHA-256 manifest, and provenance.
