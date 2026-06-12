#!/usr/bin/env python3
"""Report the current A733 patch export contract state."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import kernel_workflow_env


def git_value(repo: Path, argv: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *argv],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def subject(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("Subject:"):
            return line.removeprefix("Subject:").strip()
    return ""


def depends_on(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"^Depends-on:\s*(.+)$", text, flags=re.MULTILINE)


def build_report(export_path: Path, public_repo: Path) -> dict[str, Any]:
    patches = sorted(export_path.glob("000*.patch")) if export_path.is_dir() else []
    numbered = [item for item in patches if not item.name.startswith("0000-")]
    return {
        "export_path": str(export_path),
        "export_exists": export_path.is_dir(),
        "public_repo": str(public_repo),
        "public_repo_exists": public_repo.is_dir(),
        "git": {
            "head": git_value(public_repo, ["rev-parse", "--short", "HEAD"]) if public_repo.is_dir() else "",
            "branch": git_value(public_repo, ["branch", "--show-current"]) if public_repo.is_dir() else "",
            "dirty": bool(git_value(public_repo, ["status", "--short"])) if public_repo.is_dir() else False,
        },
        "patch_count": len(numbered),
        "cover_letter": next((item.name for item in patches if item.name.startswith("0000-")), ""),
        "patches": [
            {
                "name": item.name,
                "subject": subject(item),
                "depends_on": depends_on(item),
            }
            for item in patches
        ],
        "contract": {
            "expected_shape": "cover letter plus board binding, optional MMC binding, SoC DTSI, and board DTS patches",
            "flat_patches_are_snapshots": True,
            "mailout_source": "branch stack and b4 prep, not hand-edited patch numbering",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", help="Patch export directory; defaults to host-aware registry")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    env = kernel_workflow_env.build_env()
    public_repo = Path(env["paths"]["public_repo"]["selected"])
    export_path = Path(args.path or env["paths"]["patch_export"]["selected"])
    report = build_report(export_path, public_repo)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"export_path={report['export_path']}")
        print(f"export_exists={str(report['export_exists']).lower()}")
        print(f"patch_count={report['patch_count']}")
        print(f"cover_letter={report['cover_letter'] or '(missing)'}")
        for patch in report["patches"]:
            print(f"patch={patch['name']} subject={patch['subject'] or '(missing)'}")
    return 0 if report["export_exists"] and report["patch_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
