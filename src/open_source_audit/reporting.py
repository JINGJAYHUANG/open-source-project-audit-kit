from __future__ import annotations

import csv
import html
import io
import json
from typing import Any

from .models import AuditScore


def render_markdown(result: AuditScore, audit: dict[str, Any]) -> str:
    lines = [
        f"# Open-Source Audit — {result.repository}",
        "",
        f"- Audit ID: `{result.audit_id}`",
        f"- As of: `{result.as_of}`",
        f"- Profile: `{result.profile}`",
        f"- Use case: {audit['context']['use_case']}",
        f"- Conservative score: **{result.score:.2f}/100**",
        f"- Observed-quality score: **{result.observed_quality:.2f}/100**",
        f"- Weighted evidence coverage: **{result.coverage:.1%}**",
        f"- Evidence confidence: **{result.evidence_confidence:.1%}**",
        f"- Base recommendation: **{result.base_recommendation}**",
        f"- Final recommendation: **{result.recommendation}**",
        "",
        "> Scores are decision aids, not security certifications, legal opinions, or guarantees of maintenance or adoption.",
        "",
        "## Dimensions",
        "",
        "| Dimension | Weight | Earned | Coverage |",
        "|---|---:|---:|---:|",
    ]
    for name, value in result.dimensions.items():
        lines.append(
            f"| {name} | {value['weight']:.1f} | {value['earned_points']:.2f} | {value['coverage']:.1%} |"
        )
    lines += [
        "",
        "## Criteria",
        "",
        "| Criterion | State | Rating | Weight | Earned | Evidence | Confidence |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in result.criteria:
        rating = "—" if item.rating is None else str(item.rating)
        confidence = "—" if item.confidence is None else f"{item.confidence:.1%}"
        lines.append(
            f"| `{item.criterion_id}` | {item.state} | {rating} | {item.weight:.1f} | "
            f"{item.earned_points:.2f} | {item.evidence_count} | {confidence} |"
        )
    if result.gate_caps:
        lines += ["", "## Gate effects", ""]
        for gate in result.gate_caps:
            lines.append(
                f"- `{gate['gate']}` = `{gate['status']}` capped `{gate['before']}` to `{gate['after']}`."
            )
    else:
        lines += ["", "## Gate effects", "", "- No gate lowered the base recommendation."]
    if result.warnings:
        lines += ["", "## Warnings", ""] + [f"- {warning}" for warning in result.warnings]
    lines += ["", "## Required next verification", ""]
    next_steps = audit.get("next_verification", [])
    if next_steps:
        lines.extend(f"- {item}" for item in next_steps)
    else:
        lines.append("- No next-verification items were recorded; this is not proof that no gaps remain.")
    return "\n".join(lines) + "\n"


def render_html(result: AuditScore, audit: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item.criterion_id)}</code></td>"
        f"<td>{html.escape(item.state)}</td>"
        f"<td>{'—' if item.rating is None else item.rating}</td>"
        f"<td>{item.weight:.1f}</td>"
        f"<td>{item.earned_points:.2f}</td>"
        f"<td>{item.evidence_count}</td>"
        f"<td>{'—' if item.confidence is None else f'{item.confidence:.1%}'}</td>"
        "</tr>"
        for item in result.criteria
    )
    dimension_cards = "".join(
        f"<article><h3>{html.escape(name)}</h3><p>{value['earned_points']:.2f} / {value['weight']:.1f}</p>"
        f"<small>Coverage {value['coverage']:.1%}</small></article>"
        for name, value in result.dimensions.items()
    )
    warnings = "".join(f"<li>{html.escape(item)}</li>" for item in result.warnings) or "<li>No automatic warning.</li>"
    gate_effects = "".join(
        f"<li><code>{html.escape(gate['gate'])}</code> = <code>{html.escape(gate['status'])}</code>: "
        f"<code>{html.escape(gate['before'])}</code> → <code>{html.escape(gate['after'])}</code> "
        f"(cap <code>{html.escape(gate['cap'])}</code>).</li>"
        for gate in result.gate_caps
    ) or "<li>No gate lowered the base recommendation.</li>"
    next_steps = "".join(
        f"<li>{html.escape(str(item))}</li>"
        for item in audit.get("next_verification", [])
    ) or "<li>No next-verification item was recorded; this is not proof that no gap remains.</li>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Audit — {html.escape(result.repository)}</title>
<style>
:root{{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#172033;background:#f5f7fb}}body{{margin:0}}main{{max-width:1120px;margin:auto;padding:32px 20px 64px}}header{{background:#172033;color:white;padding:32px;border-radius:20px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:20px 0}}.metrics article,.dimensions article{{background:white;border:1px solid #dbe2ee;border-radius:14px;padding:16px}}.dimensions{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:10px;border-bottom:1px solid #e5e9f0;text-align:left}}.table-wrap{{overflow-x:auto;border-radius:14px;border:1px solid #dbe2ee}}code{{overflow-wrap:anywhere}}small{{color:#566176}}li{{margin:.4rem 0}}@media(max-width:520px){{main{{padding:16px 12px 40px}}header{{padding:22px}}th,td{{font-size:13px}}}}</style></head>
<body><main><header><p>{html.escape(result.profile)}</p><h1>{html.escape(result.repository)}</h1><p>As of {html.escape(result.as_of)} · {html.escape(audit['context']['use_case'])}</p></header>
<section class="metrics"><article><h2>{result.score:.2f}</h2><small>Conservative score</small></article><article><h2>{result.observed_quality:.2f}</h2><small>Observed quality</small></article><article><h2>{result.coverage:.1%}</h2><small>Weighted coverage</small></article><article><h2>{result.evidence_confidence:.1%}</h2><small>Evidence confidence</small></article><article><h2>{html.escape(result.base_recommendation)}</h2><small>Base recommendation</small></article><article><h2>{html.escape(result.recommendation)}</h2><small>Final recommendation</small></article></section>
<h2>Gate effects</h2><ul>{gate_effects}</ul>
<h2>Dimensions</h2><section class="dimensions">{dimension_cards}</section>
<h2>Criteria</h2><div class="table-wrap"><table><thead><tr><th>Criterion</th><th>State</th><th>Rating</th><th>Weight</th><th>Earned</th><th>Evidence</th><th>Confidence</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Warnings</h2><ul>{warnings}</ul>
<h2>Required next verification</h2><ul>{next_steps}</ul>
<p><small>This report is a decision aid, not a security certification, legal opinion, or guarantee. Unknown evidence is intentionally visible.</small></p></main></body></html>"""


def render_csv(result: AuditScore) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "criterion_id",
            "dimension",
            "state",
            "rating",
            "weight",
            "earned_points",
            "evidence_count",
            "confidence",
        ]
    )
    for item in result.criteria:
        row = [
            item.criterion_id,
            item.dimension,
            item.state,
            "" if item.rating is None else item.rating,
            item.weight,
            item.earned_points,
            item.evidence_count,
            "" if item.confidence is None else item.confidence,
        ]
        writer.writerow(
            [
                ("'" + str(value)) if str(value).startswith(("=", "+", "-", "@")) else value
                for value in row
            ]
        )
    return output.getvalue()


def render(result: AuditScore, audit: dict[str, Any], format_name: str) -> str:
    if format_name == "json":
        return json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if format_name == "markdown":
        return render_markdown(result, audit)
    if format_name == "html":
        return render_html(result, audit) + "\n"
    if format_name == "csv":
        return render_csv(result)
    raise ValueError(f"unsupported format: {format_name}")
