# Pick an open-source tool with evidence, not just stars
## 选择开源工具，先看证据、适配和不能妥协的条件

[Full documentation](README.md) · [Public tool collection](https://github.com/JINGJAYHUANG/JINGJAYHUANG)

**For:** developers, analysts and small teams comparing libraries or applications.  
**Input:** a structured audit record with explicit evidence and a scoring profile.  
**Output:** a report that separates observed quality, evidence coverage, confidence and hard gates.

## Inspect a fictional audit

Requires Python 3.11 or newer. Create an isolated environment:

```bash
git clone https://github.com/JINGJAYHUANG/open-source-project-audit-kit.git
cd open-source-project-audit-kit
python -m venv .venv
```

Activate with `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\Activate.ps1` in Windows PowerShell. Then:

```bash
python -m pip install -e .
oss-audit validate --rubric-only --strict
oss-audit score examples/synthetic/steady-library.audit.json --format markdown
```

Read the result alongside `examples/synthetic/steady-library.audit.json`. The project under review is fictional. The example teaches the method; it is not an endorsement of a real dependency.

## Ask four questions

How strong is the observed evidence? How much has actually been examined? How reliable and independent are the sources? Does any hard gate prevent adoption regardless of the score?

“高分”不能覆盖许可证不兼容或关键安全条件不满足；“没找到问题”也不等于“已经检查完整”。未知项应保留，而不是从分母里悄悄消失。

## Start your own record

The README describes `oss-audit init` for creating a structured audit and `oss-audit collect-local` for provisional observations from a local checkout. Use an explicit analysis date. Review generated observations before treating them as evidence.

Keep the record outside a public fork when it concerns a private repository or a confidential adoption decision. Remove identifying and restricted data before sharing an example.

## Boundaries

This is decision support, not legal advice, license certification, a vulnerability scanner or a security guarantee. An offline collector cannot establish current advisories, real-world adoption or future maintainer support. Stars alone are not evidence that a tool is safe or suitable.

See the [README](README.md) for methodology, scoring, hard gates and complete commands. This guide follows default-branch documentation reviewed on 2026-09-05; it does not claim a fresh execution of all tests or an independent audit of the featured tools.
