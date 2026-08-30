# Methodology

## Decision first

An audit begins with a decision context, not a repository URL. Record the intended use, environment, time budget, risk tolerance, and exit path. The same project may be suitable for a disposable research sandbox and unsuitable for a regulated production system.

## Score, coverage, confidence, and gates are separate

The conservative score treats unknown applicable criteria as zero earned points. Coverage reports how much weighted territory was actually examined. Evidence confidence reports the strength and independence of the cited observations. Hard gates can cap a recommendation even when the arithmetic score is high.

## Rating anchors

- `0`: absent, contradicted, or materially unsafe;
- `1`: weak or early evidence;
- `2`: partial implementation with important gaps;
- `3`: solid bounded evidence;
- `4`: strong, independently checkable evidence with explicit limits.

Every observed rating requires at least one dated evidence object. A number without evidence is invalid.

## No universal score

Profiles encode different decisions. `adoption-readiness` asks whether a project is suitable for a stated use. `innovation-scouting` asks whether a project deserves investigation. A project can be strategically novel but not adoption-ready.

## Time discipline

Use the event date, release date, and retrieval date distinctly. Dynamic facts should use absolute dates. Re-run an audit when a material release, maintainer change, security advisory, license change, or integration requirement changes.
