from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .collector import collect_local
from .comparison import compare_audits
from .io import dump_json, load_json, load_rubric, write_json
from .reporting import render
from .scoring import score_audit
from .templates import blank_audit
from .validation import validate_audit, validate_rubric


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oss-audit", description="Evidence-first open-source repository auditing.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--rubric", help="Optional rubric JSON path.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a complete unknown-state audit template.")
    init.add_argument("repository")
    init.add_argument("output")
    init.add_argument("--profile", default="adoption-readiness")
    init.add_argument("--as-of")

    collect = sub.add_parser("collect-local", help="Create a provisional, offline audit from a local checkout.")
    collect.add_argument("path")
    collect.add_argument("--repository", required=True)
    collect.add_argument("--output", required=True)
    collect.add_argument("--as-of")

    validate = sub.add_parser("validate", help="Validate an audit file or the rubric.")
    validate.add_argument("path", nargs="?")
    validate.add_argument("--rubric-only", action="store_true")
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--json", action="store_true")

    score = sub.add_parser("score", help="Score and report a validated audit.")
    score.add_argument("audit")
    score.add_argument("--format", choices=["json", "markdown", "html", "csv"], default="markdown")
    score.add_argument("--output")

    compare = sub.add_parser("compare", help="Compare two audits using the same profile.")
    compare.add_argument("before")
    compare.add_argument("after")
    compare.add_argument("--output")

    rubric_cmd = sub.add_parser("rubric", help="Inspect profiles, criteria, and gates.")
    rubric_cmd.add_argument("kind", choices=["profiles", "criteria", "gates"])
    rubric_cmd.add_argument("--profile", default="adoption-readiness")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rubric = load_rubric(args.rubric)

    if args.command == "init":
        if args.profile not in rubric["profiles"]:
            print(f"unknown profile: {args.profile}", file=sys.stderr)
            return 2
        write_json(args.output, blank_audit(args.repository, args.profile, rubric, as_of=args.as_of))
        print(args.output)
        return 0

    if args.command == "collect-local":
        audit = collect_local(Path(args.path), args.repository, as_of=args.as_of)
        write_json(args.output, audit)
        print(args.output)
        return 0

    if args.command == "validate":
        report = validate_rubric(rubric, strict=args.strict) if args.rubric_only else validate_audit(load_json(args.path), rubric, strict=args.strict)
        if args.json:
            print(dump_json(report.as_dict()), end="")
        else:
            print(f"validation: {'PASS' if report.ok else 'FAIL'} | errors={report.errors} warnings={report.warnings}")
            for issue in report.issues:
                print(f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}")
        return 0 if report.ok else 1

    if args.command == "score":
        audit = load_json(args.audit)
        result = score_audit(audit, rubric)
        output = render(result, audit, args.format)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8", newline="\n")
            print(args.output)
        else:
            print(output, end="")
        return 0

    if args.command == "compare":
        result = compare_audits(load_json(args.before), load_json(args.after), rubric)
        output = dump_json(result)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8", newline="\n")
            print(args.output)
        else:
            print(output, end="")
        return 0

    if args.command == "rubric":
        if args.kind == "profiles":
            payload = {key: {"title": value["title"], "purpose": value["purpose"]} for key, value in rubric["profiles"].items()}
        elif args.kind == "gates":
            payload = rubric["gates"]
        else:
            if args.profile not in rubric["profiles"]:
                print(f"unknown profile: {args.profile}", file=sys.stderr)
                return 2
            payload = rubric["profiles"][args.profile]["criteria"]
        print(dump_json(payload), end="")
        return 0
    raise AssertionError(args.command)
