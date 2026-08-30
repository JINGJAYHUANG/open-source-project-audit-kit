from __future__ import annotations

import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .io import load_rubric

README_NAMES = ("README.md", "README.rst", "README.txt", "README")
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
DEPENDENCY_FILES = (
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
)
LOCK_FILES = (
    "uv.lock",
    "poetry.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.lock",
)


def _safe_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _exists(root: Path, names: tuple[str, ...]) -> list[str]:
    return [name for name in names if _safe_file(root / name)]


def _evidence(
    locator: str,
    summary: str,
    as_of: str,
    confidence: str = "medium",
    group: str = "local-tree",
) -> dict[str, str]:
    return {
        "source_type": "automated_observation",
        "locator": locator,
        "observed_at": as_of,
        "summary": summary,
        "confidence": confidence,
        "independence_group": group,
    }


def _git_output(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip()


def _normalize_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    value = remote.strip()
    if value.startswith("git" + "@github.com:"):
        value = value.split(":", 1)[1]
    elif value.startswith(("http://", "https://", "ssh://")):
        parsed = urlparse(value)
        value = parsed.path.lstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    parts = [part for part in value.split("/") if part]
    if len(parts) < 2:
        return None
    return "/".join(parts[-2:]).casefold()


def _workflow_observations(root: Path) -> tuple[bool, bool, int, list[str]]:
    directory = root / ".github" / "workflows"
    workflows = sorted(
        path
        for path in [*directory.glob("*.yml"), *directory.glob("*.yaml")]
        if _safe_file(path)
    ) if directory.is_dir() and not directory.is_symlink() else []
    if not workflows:
        return False, False, 0, []
    pinned = True
    explicit_permissions = True
    action_count = 0
    action_re = re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*[^#\s]+@([^\s#]+)")
    for path in workflows:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "permissions:" not in text:
            explicit_permissions = False
        references = action_re.findall(text)
        action_count += len(references)
        for reference in references:
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                pinned = False
    return pinned, explicit_permissions, action_count, [
        path.relative_to(root).as_posix() for path in workflows
    ]


def _validated_as_of(value: str | None) -> str:
    observed_at = value or date.today().isoformat()
    try:
        date.fromisoformat(observed_at)
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be an ISO date in YYYY-MM-DD form") from exc
    return observed_at


def collect_local(root: Path, repository: str, *, as_of: str | None = None) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    observed_at = _validated_as_of(as_of)
    rubric = load_rubric()
    criteria = rubric["profiles"]["adoption-readiness"]["criteria"]
    ratings = {
        item["id"]: {
            "state": "unknown",
            "rating": None,
            "evidence": [],
            "notes": "Manual assessment required.",
        }
        for item in criteria
    }

    readmes = _exists(root, README_NAMES)
    licenses = _exists(root, LICENSE_NAMES)
    dependencies = _exists(root, DEPENDENCY_FILES)
    locks = _exists(root, LOCK_FILES)
    tests = [
        path
        for path in (root / "tests").rglob("test*.*")
        if _safe_file(path)
    ] if (root / "tests").is_dir() and not (root / "tests").is_symlink() else []
    docs = [
        path
        for path in (root / "docs").rglob("*")
        if _safe_file(path)
    ] if (root / "docs").is_dir() and not (root / "docs").is_symlink() else []
    pinned, explicit_permissions, action_count, workflows = _workflow_observations(root)
    metadata = dependencies + _exists(root, ("CITATION.cff",))

    def observe(
        criterion_id: str,
        rating: int,
        locator: str,
        summary: str,
        confidence: str = "medium",
    ) -> None:
        ratings[criterion_id] = {
            "state": "observed",
            "rating": rating,
            "evidence": [
                _evidence(locator, summary, observed_at, confidence)
            ],
            "notes": "Provisional local-tree observation; confirm against upstream and the intended deployment.",
        }

    if readmes or metadata:
        observe(
            "provenance.identity",
            2 if readmes and metadata else 1,
            ", ".join(readmes + metadata),
            "The checkout contains repository identity and package metadata artifacts; official ownership was not independently verified.",
        )

    remote = _git_output(root, "remote", "get-url", "origin")
    head = _git_output(root, "rev-parse", "HEAD")
    expected_remote = repository.casefold()
    normalized_remote = _normalize_remote(remote)
    if head:
        if normalized_remote == expected_remote:
            rating = 3
            summary = "The local commit and origin remote match the stated repository identity."
            locator = f"git:{head}; origin:{remote}"
        elif normalized_remote is None:
            rating = 2
            summary = "The checkout has a resolvable commit, but no comparable origin remote established repository identity."
            locator = f"git:{head}"
        else:
            rating = 1
            summary = f"The checkout commit is traceable, but origin resolves to {normalized_remote}, not the stated repository."
            locator = f"git:{head}; origin:{remote}"
        observe("provenance.source_traceability", rating, locator, summary)

    if licenses:
        observe(
            "license.spdx_clarity",
            2,
            ", ".join(licenses),
            "A top-level license artifact exists; SPDX identity and consistency with package metadata still require review.",
        )
    if dependencies and (locks or _safe_file(root / "THIRD_PARTY_NOTICES.md")):
        observe(
            "license.dependency_compatibility",
            1,
            ", ".join(dependencies + locks),
            "Dependency inputs are identifiable, but file presence does not establish license compatibility.",
        )

    last_date = _git_output(root, "log", "-1", "--format=%cI")
    if last_date:
        try:
            age = (
                date.fromisoformat(observed_at)
                - datetime.fromisoformat(last_date.replace("Z", "+00:00")).date()
            ).days
            if age < 0:
                rating = 0
                summary = "The latest local commit is dated after the audit boundary; temporal provenance requires review."
            else:
                rating = 2 if age <= 90 else 1 if age <= 365 else 0
                summary = f"The latest local commit is {age} day(s) before the audit date; issue response and upstream continuity were not inspected."
            observe(
                "maintenance.recency_response",
                rating,
                f"git:last-commit:{last_date}",
                summary,
            )
        except ValueError:
            pass

    if readmes:
        readme_text = (root / readmes[0]).read_text(encoding="utf-8", errors="replace")
        quickstart = any(
            token in readme_text.casefold()
            for token in ("install", "quick start", "quickstart", "usage")
        )
        observe(
            "documentation.quickstart",
            2 if quickstart else 1,
            readmes[0],
            "A README exists and was checked for installation or usage guidance; the collector did not execute the instructions.",
        )
    if docs or _safe_file(root / "SECURITY.md") or _safe_file(root / "CHANGELOG.md"):
        observe(
            "documentation.operational_limits",
            2 if docs and _safe_file(root / "SECURITY.md") else 1,
            "docs/ and policy files",
            "The checkout contains operational or policy documentation; completeness and accuracy remain unverified.",
        )
    if tests or workflows:
        observe(
            "quality.tests_ci",
            2 if tests and workflows else 1,
            f"tests={len(tests)}, workflows={len(workflows)}",
            "Tests and/or CI files are present; the collector does not execute them or verify passing status.",
        )
    if _safe_file(root / ".github/workflows/release.yml") and _safe_file(root / "CHANGELOG.md"):
        observe(
            "quality.release_reproducibility",
            2,
            ".github/workflows/release.yml, CHANGELOG.md",
            "Release automation and a changelog exist; no clean rebuild or tag-to-asset verification was performed.",
        )
    if _safe_file(root / "SECURITY.md"):
        observe(
            "security.policy_disclosure",
            2,
            "SECURITY.md",
            "A security policy is present; policy presence is not a code-level security audit or vulnerability check.",
        )
    if workflows:
        permission_rating = 2 if explicit_permissions else 1
        observe(
            "security.permission_surface",
            permission_rating,
            ", ".join(workflows),
            "GitHub workflow permission declarations were inventoried; non-workflow runtime permissions were not assessed.",
        )
        supply_rating = 2 if pinned and action_count else 1 if action_count else 2
        observe(
            "security.supply_chain_controls",
            supply_rating,
            ", ".join(workflows),
            "Third-party GitHub Action references were checked for full commit-SHA pinning; broader build inputs were not resolved.",
        )
    if _safe_file(root / "docs/architecture.md") or _safe_file(root / "ARCHITECTURE.md"):
        observe(
            "architecture.modularity_extensibility",
            2,
            "architecture documentation",
            "Architecture documentation is present; module isolation and extension cost were not exercised.",
        )
    if dependencies:
        observe(
            "dependencies.hygiene_update_path",
            2 if locks else 1,
            ", ".join(dependencies + locks),
            "Dependency manifests and lock files were inventoried; update safety and secret isolation were not tested.",
        )
    community_files = _exists(
        root,
        ("CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "GOVERNANCE.md", ".github/CODEOWNERS"),
    )
    if community_files:
        observe(
            "community.support_governance",
            2 if len(community_files) >= 2 else 1,
            ", ".join(community_files),
            "Contribution or governance artifacts are present; maintainer response and decision behavior were not measured.",
        )

    dangerous = re.compile(r"curl\s+[^|\n]+\|\s*(?:sh|bash)", re.IGNORECASE)
    no_curl_pipe = True
    for path in root.rglob("*"):
        if not _safe_file(path) or path.suffix.lower() not in {".md", ".sh", ".bash", ".yml", ".yaml"}:
            continue
        try:
            if dangerous.search(path.read_text(encoding="utf-8")):
                no_curl_pipe = False
                break
        except (UnicodeDecodeError, OSError):
            pass

    def gate_evidence(locator: str, summary: str) -> list[dict[str, str]]:
        return [_evidence(locator, summary, observed_at)]

    workflow_text = "\n".join(
        (root / path).read_text(encoding="utf-8", errors="replace")
        for path in workflows
    )
    broad_write = bool(re.search(r"(?mi)^\s*permissions:\s*write-all\s*$", workflow_text))
    gates = {
        "license_permission_clear": {
            "status": "unknown" if licenses else "fail",
            "evidence": [] if licenses else gate_evidence(
                "local-tree",
                "No top-level license file was found in the inspected tree.",
            ),
            "notes": (
                "A license artifact was inventoried, but intended-use and dependency compatibility require human review."
                if licenses
                else "No top-level license file was found; do not assume permission to use or redistribute."
            ),
        },
        "no_unmitigated_critical_security_finding": {
            "status": "unknown",
            "evidence": [],
            "notes": "The offline collector does not query advisories or perform code analysis.",
        },
        "privileged_defaults_bounded": {
            "status": "fail" if broad_write else "unknown",
            "evidence": (
                gate_evidence(
                    ", ".join(workflows),
                    "A workflow declares repository-wide write-all permissions.",
                )
                if broad_write
                else []
            ),
            "notes": (
                "A broad write-all default was detected in a workflow."
                if broad_write
                else "Workflow permissions are only one part of the runtime permission surface; manual review is required."
            ),
        },
        "installation_reversible": {
            "status": "unknown" if no_curl_pipe else "fail",
            "evidence": (
                []
                if no_curl_pipe
                else gate_evidence(
                    "local installation surface",
                    "A curl-pipe-shell installation pattern was found in the inspected tree.",
                )
            ),
            "notes": (
                "No curl-pipe-shell pattern was found, but removal and cleanup were not executed."
                if no_curl_pipe
                else "The detected installation pattern is not suitable for an unreviewed primary environment."
            ),
        },
        "context_fit_confirmed": {
            "status": "unknown",
            "evidence": [],
            "notes": "Fit can only be established for a stated environment through a bounded pilot.",
        },
    }

    next_steps = [
        "Confirm license identity, intended-use permission, and dependency-license compatibility.",
        "Review current upstream releases, issue response, maintainer continuity, and security advisories.",
        "Run installation, core behavior, failure-path, and removal tests in a disposable environment.",
        "Verify the actual filesystem, network, subprocess, account, and secret permission footprint.",
        "Measure integration cost and exit cost for the stated production context.",
    ]
    if normalized_remote not in {None, expected_remote}:
        next_steps.insert(
            0,
            "Resolve the mismatch between the stated repository identity and the checkout origin remote.",
        )

    return {
        "schema_version": 1,
        "audit_id": f"local-{repository.replace('/', '-').lower()}-{observed_at}",
        "repository": repository,
        "as_of": observed_at,
        "profile": "adoption-readiness",
        "auditor": {"type": "automated-local-collector", "name": "oss-audit collect-local"},
        "context": {
            "use_case": "Provisional local-checkout inventory; replace with the actual adoption decision.",
            "risk_tolerance": "unspecified",
            "environment": "local checkout; target environment not assessed",
            "time_budget": "automated inventory only",
        },
        "ratings": ratings,
        "gates": gates,
        "next_verification": next_steps,
    }
