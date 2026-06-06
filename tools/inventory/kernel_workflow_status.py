#!/usr/bin/env python3
"""Summarize the current local kernel workflow state."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REPO = Path(
    os.environ.get("KERNEL_PUBLIC_REPO", "/Users/enzo/projects/Home Lab/cubie-a7s-armbian")
)
DEFAULT_TIMEOUT = 30


def run(
    argv: list[str],
    cwd: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    ok_codes: tuple[int, ...] = (0,),
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": "timeout"}
    return {
        "ok": proc.returncode in ok_codes,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def git_status(repo: Path, remote: str) -> dict[str, Any]:
    status = run(["git", "status", "--short"], cwd=repo)
    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=repo)
    full_head = run(["git", "rev-parse", "HEAD"], cwd=repo)
    remote_head = run(["git", "ls-remote", remote, "refs/heads/main"], cwd=repo, timeout=20)
    remote_sha = ""
    if remote_head["ok"] and remote_head["stdout"]:
        remote_sha = remote_head["stdout"].split()[0]
    return {
        "path": str(repo),
        "clean": status["ok"] and not status["stdout"],
        "status_short": status["stdout"],
        "head_short": head["stdout"] if head["ok"] else "",
        "head": full_head["stdout"] if full_head["ok"] else "",
        "remote": remote,
        "remote_head": remote_sha,
        "remote_matches": bool(remote_sha and remote_sha == (full_head["stdout"] if full_head["ok"] else "")),
        "errors": [item["stderr"] for item in (status, head, full_head, remote_head) if item["stderr"]],
    }


def command_json(argv: list[str], timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    proc = run(argv, cwd=REPO_ROOT, timeout=timeout)
    if not proc["ok"]:
        return {"ok": False, "error": proc["stderr"] or proc["stdout"], "returncode": proc["returncode"]}
    try:
        return {"ok": True, "data": json.loads(proc["stdout"])}
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"json decode: {exc}", "stdout": proc["stdout"]}


def command_text(argv: list[str], timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    proc = run(argv, cwd=REPO_ROOT, timeout=timeout)
    return {
        "ok": proc["ok"],
        "returncode": proc["returncode"],
        "stdout": proc["stdout"],
        "stderr": proc["stderr"],
    }


def machine_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {"ok": False, "error": data.get("error", "machine readiness failed"), "hosts": []}
    hosts = []
    required_missing = 0
    for host in data["data"].get("hosts", []):
        required_missing += int(host.get("required_missing", 0))
        hosts.append(
            {
                "name": host.get("name"),
                "ip": host.get("ip") or "local",
                "status": host.get("status"),
                "sudo_status": host.get("sudo_status"),
                "required_missing": host.get("required_missing", 0),
                "optional_missing": host.get("optional_missing", 0),
            }
        )
    return {"ok": required_missing == 0, "required_missing": required_missing, "hosts": hosts}


def offload_summary(text: dict[str, Any]) -> dict[str, Any]:
    if not text["ok"]:
        return {"ok": False, "error": text["stderr"] or text["stdout"]}
    lines = text["stdout"].splitlines()
    targets = [line.strip() for line in lines if line.startswith(("amd-", "strix-"))]
    cortex = [line.strip() for line in lines if line.startswith("qdrant:")]
    failures = [line for line in targets + cortex if ": ok " not in line and not line.endswith(": ok")]
    return {"ok": not failures, "targets": targets, "cortex": cortex, "failures": failures}


def ledger_summary(text: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": text["ok"], "values": {}, "error": text["stderr"] if not text["ok"] else ""}
    for line in text["stdout"].splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result["values"][key] = value
    return result


def cubie_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {"ok": False, "status": "unknown", "next_action": data.get("error", "cubie gate failed")}
    gate = data["data"]
    return {
        "ok": gate.get("status") == "runtime-ready",
        "status": gate.get("status"),
        "reason": gate.get("reason"),
        "next_action": gate.get("next_action"),
    }


def build_status(args: argparse.Namespace) -> dict[str, Any]:
    machine = machine_summary(
        command_json([str(REPO_ROOT / "scripts" / "kernel-machine-readiness"), "--json"], timeout=args.timeout)
    )
    offload = offload_summary(
        command_text([str(REPO_ROOT / "scripts" / "kernel-token-offload"), "status"], timeout=args.timeout)
    )
    ledger = ledger_summary(
        command_text([str(REPO_ROOT / "scripts" / "kernel-idle-ledger"), "status"], timeout=args.timeout)
    )
    cubie = cubie_summary(
        command_json(
            [str(REPO_ROOT / "scripts" / "cubie-runtime-gate"), "--skip-network", "--json"],
            timeout=args.timeout,
        )
    )
    return {
        "homelab": git_status(REPO_ROOT, "origin"),
        "public_repo": git_status(PUBLIC_REPO, "public") if PUBLIC_REPO.exists() else {"clean": False, "error": "missing"},
        "public_mirror": git_status(PUBLIC_REPO, "origin") if PUBLIC_REPO.exists() else {"clean": False, "error": "missing"},
        "machine_readiness": machine,
        "local_offload": offload,
        "idle_ledger": ledger,
        "cubie_runtime_gate": cubie,
    }


def md_bool(value: object) -> str:
    return "yes" if value else "no"


def markdown(data: dict[str, Any]) -> str:
    public_repo = data["public_repo"]
    public_mirror = data["public_mirror"]
    homelab = data["homelab"]
    machine = data["machine_readiness"]
    offload = data["local_offload"]
    ledger = data["idle_ledger"]
    cubie = data["cubie_runtime_gate"]

    lines = [
        "# Kernel Workflow Status",
        "",
        "| area | state |",
        "| --- | --- |",
        f"| private workflow repo | clean={md_bool(homelab.get('clean'))}, backed_up={md_bool(homelab.get('remote_matches'))}, head=`{homelab.get('head_short', '')}` |",
        f"| public kernel repo | clean={md_bool(public_repo.get('clean'))}, github_backed_up={md_bool(public_repo.get('remote_matches'))}, head=`{public_repo.get('head_short', '')}` |",
        f"| thinkcentre public mirror | backed_up={md_bool(public_mirror.get('remote_matches'))} |",
        f"| machine readiness | required_missing={machine.get('required_missing', 'unknown')} |",
        f"| local offload | ok={md_bool(offload.get('ok'))} |",
        f"| idle review ledger | idle_candidates={ledger.get('values', {}).get('idle_review_candidates', 'unknown')}, unconsumed={ledger.get('values', {}).get('unconsumed_reviewed', 'unknown')} |",
        f"| Cubie runtime gate | `{cubie.get('status')}` |",
        "",
        "## Machine Readiness",
        "",
        "| host | ip | status | sudo | required missing | optional missing |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for host in machine.get("hosts", []):
        lines.append(
            f"| {host['name']} | `{host['ip']}` | `{host['status']}` | `{host['sudo_status']}` | "
            f"{host['required_missing']} | {host['optional_missing']} |"
        )
    lines.extend(["", "## Offload", ""])
    for line in offload.get("targets", []):
        lines.append(f"- {line}")
    for line in offload.get("cortex", []):
        lines.append(f"- {line}")
    if offload.get("failures"):
        lines.append(f"- failures: {', '.join(offload['failures'])}")
    lines.extend(["", "## Next Action", "", str(cubie.get("next_action") or "none")])
    return "\n".join(lines) + "\n"


def strict_failed(data: dict[str, Any]) -> bool:
    return any(
        [
            not data["homelab"].get("clean"),
            not data["homelab"].get("remote_matches"),
            not data["public_repo"].get("clean"),
            not data["public_repo"].get("remote_matches"),
            not data["public_mirror"].get("remote_matches"),
            data["machine_readiness"].get("required_missing", 1) != 0,
            not data["local_offload"].get("ok"),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    data = build_status(args)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data), end="")
    return 1 if args.strict and strict_failed(data) else 0


if __name__ == "__main__":
    raise SystemExit(main())
