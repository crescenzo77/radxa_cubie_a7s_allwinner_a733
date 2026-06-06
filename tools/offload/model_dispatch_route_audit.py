#!/usr/bin/env python3
"""Audit model-dispatch source routes against current direct kernel lanes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_HOST = "192.168.50.11"
DEFAULT_SOURCE_DIR = "/srv/projects/model-dispatch"
DEFAULT_THINKCENTRE_HOST = "192.168.50.225"

EXPECTED_KERNEL_LANES = [
    {
        "lane": "amd-fast",
        "role": "RTX 3090 fast coding/review",
        "endpoint": "http://192.168.50.252:8001/v1",
        "served_model": "qwen3.6-27b-q4km-amd-rtx3090-vulkan",
    },
    {
        "lane": "amd-research",
        "role": "RX 7900 XT batch research",
        "endpoint": "http://192.168.50.252:8092/v1",
        "served_model": "qwen36-27b-7900xt-research",
    },
    {
        "lane": "strix-review",
        "role": "Strix long review",
        "endpoint": "http://192.168.50.11:8082/v1",
        "served_model": "qwen3.6-27b-q4km-native-vulkan",
    },
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def run(command: list[str], *, timeout: int = 60, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if check and proc.returncode != 0:
        raise SystemExit(
            f"command failed ({proc.returncode}): {' '.join(command)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def ssh(host: str, command: str, *, timeout: int = 60, check: bool = True) -> str:
    proc = run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host, command],
        timeout=timeout,
        check=check,
    )
    return proc.stdout


def fetch_source(source_host: str, source_dir: str) -> dict[str, Any]:
    command = (
        f"cd {source_dir!r} && "
        "printf '%s\n' '---STATUS---' && git status --short && "
        "printf '%s\n' '---HEAD---' && git rev-parse HEAD && "
        "printf '%s\n' '---CONFIG---' && cat config.json"
    )
    raw = ssh(source_host, command, timeout=30)
    parts = raw.split("---CONFIG---\n", 1)
    if len(parts) != 2:
        raise SystemExit("could not read source config")
    preamble, config_raw = parts
    status = ""
    head = ""
    if "---STATUS---\n" in preamble and "---HEAD---\n" in preamble:
        status_part = preamble.split("---STATUS---\n", 1)[1].split("---HEAD---\n", 1)[0]
        head_part = preamble.split("---HEAD---\n", 1)[1]
        status = status_part.strip()
        head = head_part.strip().splitlines()[0] if head_part.strip() else ""
    return {
        "source_host": source_host,
        "source_dir": source_dir,
        "source_status": status,
        "source_commit": head,
        "config": json.loads(config_raw),
    }


def probe_endpoint(endpoint: str, *, probe_host: str = "", timeout: int = 8) -> dict[str, Any]:
    if probe_host:
        code = r"""
import json
import sys
import urllib.error
import urllib.request

endpoint = sys.argv[1]
url = endpoint.rstrip("/") + "/models"
try:
    with urllib.request.urlopen(url, timeout=8) as response:
        raw = response.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    ids = []
    for item in data.get("data", []) or data.get("models", []):
        if not isinstance(item, dict):
            continue
        for key in ("id", "name", "model"):
            value = item.get(key)
            if value and value not in ids:
                ids.append(value)
        for alias in item.get("aliases", []) or []:
            if alias not in ids:
                ids.append(alias)
    print(json.dumps({"ok": True, "url": url, "model_ids": ids, "error": ""}))
except Exception as exc:
    print(json.dumps({"ok": False, "url": url, "model_ids": [], "error": f"{type(exc).__name__}: {exc}"}))
"""
        raw = ssh(
            probe_host,
            f"python3 -c {shlex.quote(code)} {shlex.quote(endpoint)}",
            timeout=timeout + 8,
        )
        return json.loads(raw)

    url = endpoint.rstrip("/") + "/models"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        ids = []
        for item in data.get("data", []) or data.get("models", []):
            for key in ("id", "name", "model"):
                value = item.get(key) if isinstance(item, dict) else None
                if value and value not in ids:
                    ids.append(value)
            if isinstance(item, dict):
                for alias in item.get("aliases", []) or []:
                    if alias not in ids:
                        ids.append(alias)
        return {"ok": True, "url": url, "model_ids": ids, "error": ""}
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"ok": False, "url": url, "model_ids": [], "error": f"{type(exc).__name__}: {exc}"}


def model_records(config: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for item in config.get("models", []):
        endpoint = item.get("endpoint")
        if not endpoint:
            continue
        records.append(
            {
                "id": item.get("id", ""),
                "display": item.get("display", ""),
                "role": item.get("role", ""),
                "endpoint": endpoint,
                "served_model": item.get("served_model", ""),
                "context": item.get("context"),
            }
        )
    return records


def route_references(config: dict[str, Any], model_id: str) -> list[str]:
    refs = []
    for route, targets in (config.get("routes") or {}).items():
        if model_id in targets:
            refs.append(route)
    return refs


def audit(source: dict[str, Any], thinkcentre_host: str) -> dict[str, Any]:
    config = source["config"]
    records = model_records(config)
    endpoint_cache: dict[str, dict[str, Any]] = {}

    def endpoint_info(endpoint: str) -> dict[str, Any]:
        if endpoint not in endpoint_cache:
            endpoint_cache[endpoint] = probe_endpoint(endpoint, probe_host=thinkcentre_host)
        return endpoint_cache[endpoint]

    for record in records:
        info = endpoint_info(record["endpoint"])
        record["reachable"] = info["ok"]
        record["advertised_models"] = info["model_ids"]
        record["endpoint_error"] = info["error"]
        record["served_model_advertised"] = record["served_model"] in info["model_ids"]
        record["referenced_by_routes"] = route_references(config, record["id"])

    expected = []
    for lane in EXPECTED_KERNEL_LANES:
        info = endpoint_info(lane["endpoint"])
        matching_config = [
            record
            for record in records
            if record["endpoint"].rstrip("/") == lane["endpoint"].rstrip("/")
            and record["served_model"] == lane["served_model"]
        ]
        expected.append(
            {
                **lane,
                "reachable": info["ok"],
                "advertised_models": info["model_ids"],
                "endpoint_error": info["error"],
                "served_model_advertised": lane["served_model"] in info["model_ids"],
                "configured_exactly": bool(matching_config),
                "configured_ids": [record["id"] for record in matching_config],
            }
        )

    stale_records = [
        record
        for record in records
        if not record["reachable"] or not record["served_model_advertised"]
    ]
    missing_expected = [
        lane
        for lane in expected
        if not lane["reachable"] or not lane["served_model_advertised"] or not lane["configured_exactly"]
    ]
    status = "ready" if not stale_records and not missing_expected else "needs-reconciliation"
    return {
        "generated_at_utc": utc_now(),
        "status": status,
        "source": {
            "host": source["source_host"],
            "dir": source["source_dir"],
            "commit": source["source_commit"],
            "status": source["source_status"] or "clean",
        },
        "thinkcentre_host": thinkcentre_host,
        "expected_kernel_lanes": expected,
        "configured_endpoint_models": records,
        "stale_configured_models": stale_records,
        "missing_expected_lanes": missing_expected,
        "notes": [
            "read-only audit; no live service, systemd unit, or config was changed",
            "model-dispatch repair remains operator-gated",
        ],
    }


def md(value: object) -> str:
    return str(value if value is not None else "").replace("|", "/").replace("\n", " ")


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# model-dispatch Route Audit",
        "",
        f"Generated: `{data['generated_at_utc']}`",
        f"Status: `{data['status']}`",
        "",
        "## Source",
        "",
        "| field | value |",
        "| --- | --- |",
        f"| host | `{md(data['source']['host'])}` |",
        f"| dir | `{md(data['source']['dir'])}` |",
        f"| commit | `{md(data['source']['commit'])}` |",
        f"| status | `{md(data['source']['status'])}` |",
        f"| probe host | `{md(data['thinkcentre_host'])}` |",
        "",
        "## Expected Kernel Lanes",
        "",
        "| lane | endpoint | expected model | reachable from probe host | model advertised | configured exactly |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for lane in data["expected_kernel_lanes"]:
        lines.append(
            "| "
            f"{md(lane['lane'])} | "
            f"`{md(lane['endpoint'])}` | "
            f"`{md(lane['served_model'])}` | "
            f"{yes_no(lane['reachable'])} | "
            f"{yes_no(lane['served_model_advertised'])} | "
            f"{yes_no(lane['configured_exactly'])} |"
        )
    lines.extend(
        [
            "",
            "## Configured Endpoint Models",
            "",
            "| id | endpoint | served model | reachable | served model advertised | routes | error |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in data["configured_endpoint_models"]:
        routes = ", ".join(record.get("referenced_by_routes") or [])
        lines.append(
            "| "
            f"`{md(record['id'])}` | "
            f"`{md(record['endpoint'])}` | "
            f"`{md(record['served_model'])}` | "
            f"{yes_no(record['reachable'])} | "
            f"{yes_no(record['served_model_advertised'])} | "
            f"{md(routes or '-')} | "
            f"{md(record.get('endpoint_error') or '-')} |"
        )
    lines.extend(
        [
            "",
            "## Required Action",
            "",
        ]
    )
    if data["status"] == "ready":
        lines.append("The source routes match the expected direct kernel lanes.")
    else:
        lines.append(
            "Do not deploy `model-dispatch` for the kernel workflow until stale "
            "configured models are reconciled and all expected lanes are configured exactly."
        )
        lines.append("")
        lines.append(
            "If expected endpoints are reachable only through host-local "
            "`127.0.0.1` bindings, choose an explicit access pattern before repair: "
            "LAN-bind those services, add reviewed tunnels, or keep `model-dispatch` "
            "outside the kernel workflow."
        )
    lines.extend(
        [
            "",
            "This audit is read-only and does not change live services, systemd, Open WebUI, or model routes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-host", default=DEFAULT_SOURCE_HOST)
    parser.add_argument("--source-dir", default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--thinkcentre-host", default=DEFAULT_THINKCENTRE_HOST)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    source = fetch_source(args.source_host, args.source_dir)
    data = audit(source, args.thinkcentre_host)
    output = json.dumps(data, indent=2, sort_keys=True) + "\n" if args.json else render_markdown(data)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"wrote={args.out}")
        print(f"status={data['status']}")
    else:
        print(output, end="")
    return 1 if data["status"] != "ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
