from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return value


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json(path: str | Path, value: Any) -> None:
    Path(path).write_text(dump_json(value), encoding="utf-8", newline="\n")


def load_rubric(path: str | Path | None = None) -> dict[str, Any]:
    if path is not None:
        return load_json(path)
    text = (
        resources.files("open_source_audit")
        .joinpath("data", "rubric.json")
        .read_text(encoding="utf-8")
    )
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("packaged rubric must be an object")
    return value
