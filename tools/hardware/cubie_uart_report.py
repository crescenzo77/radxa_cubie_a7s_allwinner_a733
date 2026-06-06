#!/usr/bin/env python3
"""Summarize pulled Cubie UART capture logs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG_DIR = REPO_ROOT / "tools" / "hardware-logs" / "cubie-uart"

BOOT_MARKER_RE = re.compile(
    r"(U-Boot|SPL|DRAM|MMC|mmc|Starting kernel|Linux version|Kernel command line|"
    r"OF:|devicetree|console|login:|panic|Oops|ERROR|WARNING)",
    re.IGNORECASE,
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_meta(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - reporter should keep going.
        return {"metadata_error": str(exc)}


def log_for_meta(path: Path) -> Path:
    if path.name.endswith(".json"):
        return path.with_suffix("")
    return path


def decode_log(path: Path, limit: int = 65536) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return ""
    data = path.read_bytes()[:limit]
    text = data.decode("utf-8", errors="replace")
    return "".join(ch if ch == "\n" or ch == "\t" or ord(ch) >= 32 else "." for ch in text)


def marker_lines(text: str, limit: int = 8) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or not BOOT_MARKER_RE.search(line):
            continue
        short = line[:180]
        if short in seen:
            continue
        seen.add(short)
        lines.append(short)
        if len(lines) >= limit:
            break
    return lines


def sha256_match(local_sha: Optional[str], remote_sha: object) -> Optional[bool]:
    if local_sha is None or not remote_sha:
        return None
    return local_sha == str(remote_sha)


def md_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def load_captures(log_dir: Path) -> list[dict[str, Any]]:
    captures: list[dict[str, Any]] = []
    for meta_path in sorted(log_dir.glob("*.uart.log.json")):
        meta = read_meta(meta_path)
        log_path = log_for_meta(meta_path)
        local_bytes = log_path.stat().st_size if log_path.exists() else None
        local_sha = sha256_file(log_path)
        remote_sha = meta.get("log_sha256")
        text = decode_log(log_path)
        captures.append(
            {
                "meta_path": str(meta_path),
                "log_path": str(log_path),
                "label": meta.get("label"),
                "captured_at_utc": meta.get("captured_at_utc"),
                "device": meta.get("device"),
                "resolved_device": meta.get("resolved_device"),
                "baud": meta.get("baud"),
                "seconds": meta.get("seconds"),
                "remote_bytes": meta.get("bytes"),
                "local_bytes": local_bytes,
                "remote_sha256": remote_sha,
                "local_sha256": local_sha,
                "sha256_match": sha256_match(local_sha, remote_sha),
                "markers": marker_lines(text),
                "excerpt": text[:1200],
                "metadata_error": meta.get("metadata_error"),
            }
        )
    return captures


def build_report(captures: list[dict[str, Any]], log_dir: Path, limit: int) -> str:
    captures = sorted(captures, key=lambda item: str(item.get("captured_at_utc") or ""))
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    marker_hits = [item for item in captures if item.get("markers")]
    sha_mismatches = [item for item in captures if item.get("sha256_match") is False]

    by_device: dict[str, int] = {}
    for item in captures:
        key = str(item.get("resolved_device") or item.get("device") or "unknown")
        by_device[key] = by_device.get(key, 0) + 1

    lines = [
        "# Cubie UART Capture Report",
        "",
        f"Generated: `{utc_now()}`",
        f"Log directory: `{log_dir}`",
        "",
        "## Summary",
        "",
        f"- captures: `{len(captures)}`",
        f"- non-empty captures: `{len(non_empty)}`",
        f"- captures with boot/login/error markers: `{len(marker_hits)}`",
        f"- local/metadata SHA256 mismatches: `{len(sha_mismatches)}`",
        "",
        "## Devices",
        "",
    ]

    if by_device:
        lines.extend(["| device | captures |", "| --- | ---: |"])
        for device, count in sorted(by_device.items()):
            lines.append(f"| `{md_escape(device)}` | {count} |")
    else:
        lines.append("No UART capture metadata found.")

    lines.extend(
        [
            "",
            f"## Latest {min(limit, len(captures))} Captures",
            "",
            "| captured_at_utc | label | resolved_device | seconds | bytes | sha | markers |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for item in captures[-limit:]:
        sha = item.get("local_sha256") or ""
        sha_short = sha[:12] if sha else "missing"
        markers = "; ".join(item.get("markers") or [])
        lines.append(
            "| "
            f"{md_escape(item.get('captured_at_utc'))} | "
            f"{md_escape(item.get('label'))} | "
            f"`{md_escape(item.get('resolved_device') or item.get('device'))}` | "
            f"{md_escape(item.get('seconds'))} | "
            f"{md_escape(item.get('local_bytes'))} | "
            f"`{sha_short}` | "
            f"{md_escape(markers or '-')}"
            " |"
        )

    lines.extend(["", "## Non-Empty Captures", ""])
    if not non_empty:
        lines.append("No non-empty UART captures are available yet.")
    else:
        for item in non_empty:
            lines.extend(
                [
                    f"### {item.get('captured_at_utc')} {item.get('label')}",
                    "",
                    f"- device: `{item.get('device')}`",
                    f"- resolved: `{item.get('resolved_device')}`",
                    f"- bytes: `{item.get('local_bytes')}`",
                    f"- sha256: `{item.get('local_sha256')}`",
                    "",
                    "```text",
                    str(item.get("excerpt") or "").rstrip(),
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize pulled Cubie UART captures.")
    parser.add_argument("--dir", default=str(DEFAULT_LOG_DIR), help="Local UART log directory.")
    parser.add_argument("--limit", type=int, default=12, help="Latest capture rows to show.")
    parser.add_argument("--write", default="", help="Optional markdown report path to write.")
    args = parser.parse_args()

    log_dir = Path(args.dir)
    captures = load_captures(log_dir)
    report = build_report(captures, log_dir, max(1, args.limit))
    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"wrote={out}")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
