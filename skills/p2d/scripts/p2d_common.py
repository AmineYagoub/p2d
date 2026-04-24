#!/usr/bin/env python3
"""Shared helpers for P2D scripts."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SOURCE_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".go",
    ".rs",
    ".java",
    ".cs",
    ".rb",
    ".kt",
    ".swift",
    ".scala",
    ".php",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".vue",
    ".svelte",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".venv",
    "venv",
    "__pycache__",
    "target",
    "coverage",
}


@dataclass(frozen=True)
class Reference:
    file: str
    line: int
    category: str
    text: str


def repo_root(path: str | Path = ".") -> Path:
    return Path(path).resolve()


def command_version(command: list[str]) -> dict:
    name = command[0]
    path = shutil.which(name)
    if path is None:
        return {"available": False, "path": None, "version": None}
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        version = (result.stdout or result.stderr).strip().splitlines()
        return {
            "available": result.returncode == 0,
            "path": path,
            "version": version[0] if version else None,
        }
    except Exception as exc:  # pragma: no cover - defensive for unusual shells
        return {"available": False, "path": path, "version": f"error: {exc}"}


def iter_source_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for filename in files:
            path = Path(current) / filename
            if path.suffix in SOURCE_EXTENSIONS:
                yield path


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def classify_line(symbol: str, text: str, path: Path) -> str:
    stripped = text.strip()
    suffix = path.suffix
    lower_name = path.name.lower()
    if re.search(r"\b(import|from|require|use)\b", stripped) or "import(" in stripped:
        return "import"
    if re.search(r"\b(export|module\.exports)\b", stripped):
        return "export"
    if re.search(rf"\b(class|interface|type|struct|trait|func|def|function)\s+{re.escape(symbol)}\b", stripped):
        return "definition"
    if re.search(rf"\b{re.escape(symbol)}\s*\(", stripped):
        return "call"
    if re.search(rf"[\"'`].*{re.escape(symbol)}.*[\"'`]", stripped):
        return "string"
    if any(part in lower_name for part in (".test.", ".spec.", "test_", "_test.")):
        return "test"
    if suffix in {".json", ".yaml", ".yml"}:
        return "config"
    return "reference"


def find_symbol(root: Path, symbol: str) -> list[Reference]:
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")
    matches: list[Reference] = []
    for path in iter_source_files(root):
        for idx, line in enumerate(safe_read(path).splitlines(), start=1):
            if pattern.search(line):
                matches.append(
                    Reference(
                        file=rel(path, root),
                        line=idx,
                        category=classify_line(symbol, line, path),
                        text=line.strip(),
                    )
                )
    return matches


def bucket_counts(refs: Iterable[Reference]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ref in refs:
        counts[ref.category] = counts.get(ref.category, 0) + 1
    return dict(sorted(counts.items()))


def as_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def refs_as_dicts(refs: Iterable[Reference]) -> list[dict]:
    return [asdict(ref) for ref in refs]


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Repository root to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
