#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Classify checkpatch warnings that need human/process review.

This gate is intentionally narrower than checkpatch itself. It runs
checkpatch with warning types enabled, then refuses every warning except
FILE_PATH_CHANGES when the newly added paths have explicit MAINTAINERS
coverage.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


CHECK_RE = re.compile(r"^(ERROR|WARNING|CHECK):([A-Z0-9_]+):")
TOTAL_RE = re.compile(r"^total:\s+(\d+)\s+errors,\s+(\d+)\s+warnings,\s+(\d+)\s+checks")
DIFF_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$")
FIELD_RE = re.compile(r"^([A-Z]):\s*(.*)$")
GENERIC_FALLBACK_ENTRIES = {"THE REST"}


def run_checkpatch(checkpatch_tree: Path, patches: list[Path]) -> subprocess.CompletedProcess[str]:
    script = checkpatch_tree / "scripts" / "checkpatch.pl"
    if not script.exists():
        raise SystemExit(f"missing checkpatch script: {script}")
    command = [
        "perl",
        str(script),
        "--strict",
        "--show-types",
        "--no-tree",
        *[str(path) for path in patches],
    ]
    return subprocess.run(
        command,
        cwd=str(checkpatch_tree),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def new_files_in_patch(path: Path) -> list[str]:
    files: list[str] = []
    current: str | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = DIFF_RE.match(line)
        if match:
            current = match.group(2)
            continue
        if line.startswith("new file mode ") and current and current not in files:
            files.append(current)
    return files


def parse_maintainers(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        if not line:
            current = None
            continue
        field = FIELD_RE.match(line)
        if field:
            if current is None:
                continue
            key, value = field.groups()
            if key in {"F", "N"}:
                current.setdefault(key, []).append(value.strip())
            continue
        current = {"title": line.strip(), "F": [], "N": []}
        entries.append(current)
    return entries


def f_pattern_matches(pattern: str, path: str) -> bool:
    if pattern.endswith("/"):
        return path.startswith(pattern)
    return fnmatch.fnmatchcase(path, pattern)


def n_pattern_matches(pattern: str, path: str) -> bool:
    try:
        return re.search(pattern, path) is not None
    except re.error:
        return pattern in path


def maintainer_matches(entries: list[dict[str, Any]], path: str) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for entry in entries:
        for pattern in entry.get("F", []):
            if f_pattern_matches(pattern, path):
                matches.append({"entry": entry["title"], "field": "F", "pattern": pattern})
        for pattern in entry.get("N", []):
            if n_pattern_matches(pattern, path):
                matches.append({"entry": entry["title"], "field": "N", "pattern": pattern})
    return matches


def explicit_matches(matches: list[dict[str, str]]) -> list[dict[str, str]]:
    return [match for match in matches if match["entry"] not in GENERIC_FALLBACK_ENTRIES]


def patch_sections(output: str, patches: list[Path]) -> dict[str, str]:
    names = [str(path) for path in patches]
    sections = {name: "" for name in names}
    current: str | None = None
    for line in output.splitlines():
        if line in sections:
            current = line
            sections[current] += line + "\n"
            continue
        if current:
            sections[current] += line + "\n"
    return sections


def classify(proc: subprocess.CompletedProcess[str], patches: list[Path], maintainers: Path) -> dict[str, Any]:
    entries = parse_maintainers(maintainers)
    sections = patch_sections(proc.stdout, patches)
    patch_reports = []
    totals = {"errors": 0, "warnings": 0, "checks": 0}
    unapproved = []

    for patch in patches:
        patch_text = sections.get(str(patch), "")
        typed = [match.groups() for match in map(CHECK_RE.match, patch_text.splitlines()) if match]
        for line in patch_text.splitlines():
            total = TOTAL_RE.match(line)
            if total:
                totals["errors"] += int(total.group(1))
                totals["warnings"] += int(total.group(2))
                totals["checks"] += int(total.group(3))

        new_files = new_files_in_patch(patch)
        coverage = []
        for item in new_files:
            matches = maintainer_matches(entries, item)
            coverage.append(
                {
                    "path": item,
                    "matches": matches,
                    "explicit_matches": explicit_matches(matches),
                }
            )
        missing_coverage = [item for item in coverage if not item["explicit_matches"]]
        warning_types = [kind for level, kind in typed if level == "WARNING"]
        error_types = [kind for level, kind in typed if level == "ERROR"]
        check_types = [kind for level, kind in typed if level == "CHECK"]
        disallowed = [
            {"level": level, "type": kind}
            for level, kind in typed
            if not (level == "WARNING" and kind == "FILE_PATH_CHANGES" and not missing_coverage)
        ]
        if disallowed:
            unapproved.append({"patch": str(patch), "items": disallowed, "missing_coverage": missing_coverage})
        patch_reports.append(
            {
                "patch": str(patch),
                "new_files": new_files,
                "maintainers_coverage": coverage,
                "warnings": warning_types,
                "errors": error_types,
                "checks": check_types,
                "approved_file_path_changes": bool(warning_types)
                and set(warning_types) == {"FILE_PATH_CHANGES"}
                and not error_types
                and not check_types
                and not missing_coverage,
            }
        )

    if proc.returncode != 0 and totals["errors"] == totals["warnings"] == totals["checks"] == 0:
        unapproved.append(
            {
                "patch": "checkpatch",
                "items": [{"level": "ERROR", "type": "CHECKPATCH_OUTPUT_UNPARSED"}],
                "missing_coverage": [],
            }
        )

    if unapproved:
        status = "FAIL"
        exit_code = 1
    elif totals["errors"] == totals["warnings"] == totals["checks"] == 0:
        status = "PASS"
        exit_code = 0
    elif totals["errors"] == 0 and totals["checks"] == 0:
        status = "PASS_WITH_REVIEWED_WARNINGS"
        exit_code = 0
    else:
        status = "FAIL"
        exit_code = 1

    return {
        "status": status,
        "exit_code": exit_code,
        "checkpatch_exit_code": proc.returncode,
        "checkpatch_command": shlex.join(proc.args),
        "totals": totals,
        "maintainers_file": str(maintainers),
        "patches": patch_reports,
        "unapproved": unapproved,
        "stderr": proc.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpatch-tree", required=True, help="Linux tree containing scripts/checkpatch.pl")
    parser.add_argument("--maintainers", help="MAINTAINERS file to use for coverage checks")
    parser.add_argument("--json", action="store_true", help="Write machine-readable output")
    parser.add_argument("patches", nargs="+")
    args = parser.parse_args()

    checkpatch_tree = Path(args.checkpatch_tree).resolve()
    patches = [Path(item).resolve() for item in args.patches]
    maintainers = Path(args.maintainers).resolve() if args.maintainers else checkpatch_tree / "MAINTAINERS"
    proc = run_checkpatch(checkpatch_tree, patches)
    report = classify(proc, patches, maintainers)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']}")
        print(
            "totals="
            f"{report['totals']['errors']} errors, "
            f"{report['totals']['warnings']} warnings, "
            f"{report['totals']['checks']} checks"
        )
        for patch in report["patches"]:
            if patch["warnings"] or patch["errors"] or patch["checks"]:
                print(f"patch={patch['patch']}")
                print(f"  errors={','.join(patch['errors']) or 'none'}")
                print(f"  warnings={','.join(patch['warnings']) or 'none'}")
                print(f"  checks={','.join(patch['checks']) or 'none'}")
                for item in patch["maintainers_coverage"]:
                    matches = ", ".join(
                        f"{match['field']}:{match['pattern']} ({match['entry']})"
                        for match in item["explicit_matches"]
                    )
                    print(f"  new_file={item['path']} coverage={matches or 'missing'}")
        if report["unapproved"]:
            print("unapproved=1")
        else:
            print("unapproved=0")
    return int(report["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
