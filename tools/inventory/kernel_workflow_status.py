#!/usr/bin/env python3
"""Summarize the current local kernel workflow state."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REPO = Path(
    os.environ.get("KERNEL_PUBLIC_REPO", "/Users/enzo/projects/Home Lab/cubie-a7s-armbian")
)
DEFAULT_TIMEOUT = 30
OPERATOR_BRIEF = "scripts/cubie-corrected-root-operator-brief"
PATCH_PREP_CHECKLIST = "scripts/a733-patch-prep-checklist"
BACKUP_APPROVAL_BRIEF = "scripts/kernel-backup-approval-brief"
REQUIRED_OFFLOAD_TARGETS = {"amd-fast", "amd-research", "strix-review"}


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
    remote_url = run(["git", "remote", "get-url", remote], cwd=repo)
    remote_head = run(["git", "ls-remote", remote, "refs/heads/main"], cwd=repo, timeout=20)
    remote_sha = ""
    if remote_head["ok"] and remote_head["stdout"]:
        remote_sha = remote_head["stdout"].split()[0]
    url = remote_url["stdout"] if remote_url["ok"] else ""
    return {
        "path": str(repo),
        "clean": status["ok"] and not status["stdout"],
        "status_short": status["stdout"],
        "head_short": head["stdout"] if head["ok"] else "",
        "head": full_head["stdout"] if full_head["ok"] else "",
        "remote": remote,
        "remote_url": url,
        "remote_is_github": "github.com" in url.lower(),
        "remote_head": remote_sha,
        "remote_matches": bool(remote_sha and remote_sha == (full_head["stdout"] if full_head["ok"] else "")),
        "errors": [item["stderr"] for item in (status, head, full_head, remote_url, remote_head) if item["stderr"]],
    }


def missing_git_status(repo: Path, remote: str) -> dict[str, Any]:
    return {
        "path": str(repo),
        "clean": False,
        "status_short": "",
        "head_short": "",
        "head": "",
        "remote": remote,
        "remote_url": "",
        "remote_is_github": False,
        "remote_head": "",
        "remote_matches": False,
        "errors": ["missing repository"],
    }


def command_json(
    argv: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    ok_codes: tuple[int, ...] = (0,),
) -> dict[str, Any]:
    proc = run(argv, cwd=REPO_ROOT, timeout=timeout, ok_codes=ok_codes)
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


def offload_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {"ok": False, "error": data.get("error", "offload status failed"), "targets": [], "cortex": []}
    status = data["data"]
    target_lines = []
    failures = []
    seen_targets = set()
    for target in status.get("targets", []):
        name = str(target.get("name") or "")
        if name:
            seen_targets.add(name)
        if target.get("ok"):
            target_lines.append(
                f"{target.get('name')}: ok host={target.get('host')} "
                f"base={target.get('base_url')} models={target.get('models', [])}"
            )
        else:
            line = (
                f"{target.get('name')}: unavailable host={target.get('host')} "
                f"base={target.get('base_url')} error={target.get('error')}"
            )
            target_lines.append(line)
            failures.append(line)
    missing_targets = sorted(REQUIRED_OFFLOAD_TARGETS.difference(seen_targets))
    for name in missing_targets:
        failures.append(f"{name}: missing required dispatcher offload target")
    cortex_data = status.get("cortex", {})
    if cortex_data.get("ok"):
        cortex_lines = [
            f"qdrant: ok health={cortex_data.get('health')} count={cortex_data.get('count')}"
        ]
    else:
        line = f"qdrant: unavailable error={cortex_data.get('error')}"
        cortex_lines = [line]
        failures.append(line)
    return {
        "ok": bool(status.get("ok")) and not failures,
        "targets": target_lines,
        "cortex": cortex_lines,
        "failures": failures,
        "required_targets": sorted(REQUIRED_OFFLOAD_TARGETS),
        "missing_targets": missing_targets,
    }


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
        return {
            "ok": False,
            "status": "unknown",
            "human_required": False,
            "human_gate": "",
            "evidence_gate": "",
            "next_action": data.get("error", "cubie gate failed"),
            "next_command": "",
            "next_shell": "",
            "next_reboot_command": "",
            "next_reboot_shell": "",
        }
    gate = data["data"]
    status = gate.get("status")
    next_command = ""
    next_reboot_command = ""
    human_required = False
    human_gate = ""
    evidence_gate = ""
    staging = gate.get("staging") if isinstance(gate.get("staging"), dict) else {}
    rows = staging.get("rows") if isinstance(staging.get("rows"), list) else []
    if status == "root-install-required":
        ready = [row for row in rows if row.get("ready_for_root_install")]
        if ready and ready[0].get("ip"):
            next_command = (
                "scripts/cubie-interactive-root-install-session "
                f"--confirm-target-ip {ready[0]['ip']}"
            )
            human_required = True
            human_gate = (
                "Cubie sudo password and live UART/operator control are required; "
                "do not install the extlinux label non-interactively."
            )
            evidence_gate = (
                "After install and boot capture, run "
                "`scripts/cubie-latest-corrected-root-proof --strict` before "
                "claiming v4 runtime proof."
            )
    elif status == "boot-selection-required":
        installed = [row for row in rows if row.get("root_install_complete")]
        labels = sorted({row.get("capture_label") for row in installed if row.get("capture_label")})
        stage = str(staging.get("stage") or "")
        capture_label = labels[0] if labels else f"{Path(stage).name}-boot" if stage else "cubie-manual-boot"
        next_command = f"scripts/cubie-uart-interactive-boot-session {shlex.quote(capture_label)}"
        if installed and installed[0].get("ip"):
            next_reboot_command = f"ssh radxa@{installed[0]['ip']} 'sudo reboot'"
        human_required = True
        human_gate = (
            "Live U-Boot intervention is required: set RAM-only `drm_debug=1`, "
            "run `bootcmd`, then select the corrected-root label."
        )
        evidence_gate = (
            "The UART capture must pass `scripts/cubie-corrected-root-proof-gate "
            "--strict` for the exact v4 Image and DTB."
        )
    elif status == "runtime-ready":
        evidence_gate = "Runtime proof is present; inspect the proof ID before patch prep."
    return {
        "ok": status == "runtime-ready",
        "status": status,
        "reason": gate.get("reason"),
        "human_required": human_required,
        "human_gate": human_gate,
        "evidence_gate": evidence_gate,
        "next_action": gate.get("next_action"),
        "next_command": next_command,
        "next_shell": f"cd {shlex.quote(str(REPO_ROOT))} && {next_command}" if next_command else "",
        "next_reboot_command": next_reboot_command,
        "next_reboot_shell": next_reboot_command,
    }


def a733_series_shape_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {
            "ok": False,
            "status": "unknown",
            "patch_count": 0,
            "finding_kinds": [],
            "next_action": data.get("error", "A733 series-shape gate failed"),
        }
    gate = data["data"]
    findings = gate.get("findings") if isinstance(gate.get("findings"), list) else []
    finding_kinds = [str(item.get("kind")) for item in findings if item.get("kind")]
    if gate.get("status") == "PASS":
        next_action = (
            "series shape is maintainer-aligned; require corrected-root runtime "
            "proof and normal kernel validation before patch prep"
        )
    else:
        next_action = (
            "do not send the current public patch export; reshape to the narrow "
            "DTS/board series after corrected-root runtime proof"
        )
    return {
        "ok": gate.get("status") == "PASS",
        "status": gate.get("status", "unknown"),
        "patch_count": gate.get("patch_count", 0),
        "finding_kinds": finding_kinds,
        "next_action": next_action,
    }


def public_hygiene_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {
            "ok": False,
            "status": "unknown",
            "match_count": 0,
            "kinds": [],
            "next_action": data.get("error", "public hygiene gate failed"),
        }
    gate = data["data"]
    matches = gate.get("matches") if isinstance(gate.get("matches"), list) else []
    kinds = sorted({str(item.get("kind")) for item in matches if item.get("kind")})
    if gate.get("status") == "PASS":
        next_action = "public kernel-facing repo has no private lab or AI metadata hygiene matches"
    else:
        next_action = "remove private lab or AI metadata from the public kernel-facing repo before backup or submission"
    return {
        "ok": gate.get("status") == "PASS",
        "status": gate.get("status", "unknown"),
        "match_count": gate.get("match_count", 0),
        "kinds": kinds,
        "next_action": next_action,
    }


def maintainer_ready_summary(data: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    blockers.extend(strict_blockers(data))
    if data["cubie_runtime_gate"].get("status") != "runtime-ready":
        blockers.append(f"cubie runtime proof is {data['cubie_runtime_gate'].get('status')}")
    if not data["a733_series_shape"].get("ok"):
        blockers.append(
            "A733 export shape is not maintainer-ready: "
            + ", ".join(data["a733_series_shape"].get("finding_kinds", []) or ["unknown"])
        )
    if not data["public_repo"].get("remote_is_github"):
        blockers.append("public kernel repo public remote is not GitHub")

    cubie_next = data["cubie_runtime_gate"].get("next_shell") or data["cubie_runtime_gate"].get("next_command")
    if data["cubie_runtime_gate"].get("status") != "runtime-ready" and cubie_next:
        next_action = str(cubie_next)
    elif not data["a733_series_shape"].get("ok"):
        next_action = (
            "after corrected-root runtime proof, reshape the public export to "
            "the narrow A733 DTS/board series before patch-prep validation"
        )
    elif not data["public_hygiene"].get("ok"):
        next_action = "remove public hygiene matches before public backup or patch prep"
    elif not data["public_repo"].get("clean") or not data["public_repo"].get("remote_matches"):
        next_action = "clean and push the public kernel repo before patch prep"
    elif not data["public_mirror"].get("remote_matches"):
        next_action = "push the public kernel repo to the ThinkCentre mirror before patch prep"
    elif blockers:
        next_action = "do not prepare or send maintainer-facing patches; clear the listed blockers first"
    else:
        next_action = "maintainer-ready gates pass; proceed to patch-prep validation and human review"
    return {
        "ok": not blockers,
        "blockers": blockers,
        "next_action": next_action,
        "operator_brief_shell": f"cd {shlex.quote(str(REPO_ROOT))} && {OPERATOR_BRIEF}",
    }


def workflow_backup_summary(data: dict[str, Any]) -> dict[str, Any]:
    homelab = data["homelab"]
    public_repo = data["public_repo"]
    public_mirror = data["public_mirror"]
    private_github_backed = bool(homelab.get("remote_matches") and homelab.get("remote_is_github"))
    next_action = "backup posture is current"
    if not homelab.get("remote_matches"):
        next_action = f"push private workflow repo to configured origin `{homelab.get('remote')}`"
    elif not private_github_backed:
        next_action = (
            "private workflow repo is backed up to its configured origin, but not GitHub; "
            "human approval is required before adding a private GitHub remote"
        )
    elif not (public_repo.get("remote_matches") and public_repo.get("remote_is_github")):
        next_action = "push public kernel repo to its GitHub remote"
    elif not public_mirror.get("remote_matches"):
        next_action = "push public kernel repo to the ThinkCentre mirror"
    return {
        "ok": bool(
            homelab.get("remote_matches")
            and public_repo.get("remote_matches")
            and public_repo.get("remote_is_github")
            and public_mirror.get("remote_matches")
        ),
        "private_origin_backed": bool(homelab.get("remote_matches")),
        "private_github_backed": private_github_backed,
        "private_remote_url": homelab.get("remote_url") or "",
        "public_github_backed": bool(public_repo.get("remote_matches") and public_repo.get("remote_is_github")),
        "public_remote_url": public_repo.get("remote_url") or "",
        "public_mirror_backed": bool(public_mirror.get("remote_matches")),
        "next_action": next_action,
        "note": (
            "private workflow repo is backed up only to its configured origin; "
            "no GitHub remote is configured"
            if homelab.get("remote_matches") and not homelab.get("remote_is_github")
            else ""
        ),
    }


def dispatcher_waiting_actions(data: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    cubie = data["cubie_runtime_gate"]
    ledger_values = data.get("idle_ledger", {}).get("values", {})
    idle_candidates = ledger_values.get("idle_review_candidates", "unknown")
    if cubie.get("human_required"):
        actions.append(f"read operator brief: cd {shlex.quote(str(REPO_ROOT))} && {OPERATOR_BRIEF}")
        actions.append(
            "keep hardware gate explicit: "
            + str(cubie.get("human_gate") or "human interaction required before runtime proof")
        )
        actions.append(
            "do not reshape or send patches until evidence gate passes: "
            + str(cubie.get("evidence_gate") or "runtime proof required")
        )
        actions.append(
            "after proof passes, use the read-only patch-prep checklist: "
            f"cd {shlex.quote(str(REPO_ROOT))} && {PATCH_PREP_CHECKLIST} --run"
        )
        actions.append(
            "while waiting, run non-hardware patch-prep preflight: "
            f"cd {shlex.quote(str(REPO_ROOT))} && {PATCH_PREP_CHECKLIST} --preflight"
        )
    actions.append(
        f"check backup posture: cd {shlex.quote(str(REPO_ROOT))} && "
        "scripts/kernel-workflow-status --workflow-backup-status"
    )
    backup_next = data.get("workflow_backup", {}).get("next_action")
    if backup_next and backup_next != "backup posture is current":
        actions.append(f"backup next action: {backup_next}")
        actions.append(
            "read backup approval brief before changing remotes: "
            f"cd {shlex.quote(str(REPO_ROOT))} && {BACKUP_APPROVAL_BRIEF}"
        )
    if data["local_offload"].get("ok") and idle_candidates not in ("0", 0):
        actions.append(
            "optional advisory review only: "
            "scripts/kernel-idle-review-sweep --limit 1 --run --allow-unavailable"
        )
    elif data["local_offload"].get("ok"):
        actions.append("advisory idle review queue is empty; do not run a no-op sweep")
    if not data["a733_series_shape"].get("ok"):
        actions.append(
            "preserve series guardrail: current export is scaffolding; "
            "do not create maintainer-facing patches before corrected-root proof"
        )
    return actions


def goal_completion_audit(data: dict[str, Any]) -> dict[str, Any]:
    checks = [
        {
            "requirement": "Codex Desktop dispatcher/offload documentation exists",
            "status": "pass" if data["local_offload"].get("ok") else "fail",
            "evidence": (
                "local offload lanes are healthy and dispatcher runbook/status surfaces exist: "
                + ", ".join(data["local_offload"].get("required_targets", []))
                if data["local_offload"].get("ok")
                else "local offload lanes are not all healthy"
            ),
        },
        {
            "requirement": "maintainer guardrails are enforced before patch prep",
            "status": "pass" if not data["a733_series_shape"].get("ok") else "review",
            "evidence": (
                "current 9-patch scaffolding export is blocked from maintainer use"
                if not data["a733_series_shape"].get("ok")
                else "series-shape gate passes; verify this is backed by runtime proof"
            ),
        },
        {
            "requirement": "exact v4 Cubie runtime proof is captured",
            "status": "fail" if data["cubie_runtime_gate"].get("status") != "runtime-ready" else "pass",
            "evidence": f"cubie runtime gate is {data['cubie_runtime_gate'].get('status')}",
        },
        {
            "requirement": "maintainer-facing A733 patch shape is ready",
            "status": "fail" if not data["a733_series_shape"].get("ok") else "pass",
            "evidence": data["a733_series_shape"].get("next_action") or "",
        },
        {
            "requirement": "public kernel material is hygienic and GitHub/mirror backed",
            "status": "pass"
            if data["public_hygiene"].get("ok")
            and data["public_repo"].get("remote_matches")
            and data["public_repo"].get("remote_is_github")
            and data["public_mirror"].get("remote_matches")
            else "fail",
            "evidence": (
                "public repo hygiene passes and public GitHub plus ThinkCentre mirror match"
                if data["public_hygiene"].get("ok")
                and data["public_repo"].get("remote_matches")
                and data["public_repo"].get("remote_is_github")
                and data["public_mirror"].get("remote_matches")
                else "public hygiene or backup checks are incomplete"
            ),
        },
        {
            "requirement": "private workflow work is backed up at stopping points",
            "status": "pass" if data["workflow_backup"].get("private_origin_backed") else "fail",
            "evidence": data["workflow_backup"].get("note") or "private workflow origin matches HEAD",
        },
    ]
    incomplete = [item for item in checks if item["status"] != "pass"]
    return {
        "complete": not incomplete,
        "checks": checks,
        "incomplete": incomplete,
        "next_action": data["maintainer_ready"].get("next_action") or "none",
    }


def build_status(args: argparse.Namespace) -> dict[str, Any]:
    machine = machine_summary(
        command_json([str(REPO_ROOT / "scripts" / "kernel-machine-readiness"), "--json"], timeout=args.timeout)
    )
    offload = offload_summary(
        command_json(
            [str(REPO_ROOT / "scripts" / "kernel-token-offload"), "status", "--json"],
            timeout=args.timeout,
            ok_codes=(0, 1),
        )
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
    a733_series_shape = a733_series_shape_summary(
        command_json(
            [
                str(REPO_ROOT / "scripts" / "a733-series-shape-gate"),
                str(PUBLIC_REPO / "patches"),
                "--json",
            ],
            timeout=args.timeout,
            ok_codes=(0, 1),
        )
    )
    public_hygiene = public_hygiene_summary(
        command_json(
            [
                str(REPO_ROOT / "scripts" / "kernel-public-hygiene-gate"),
                str(PUBLIC_REPO),
                "--json",
            ],
            timeout=args.timeout,
            ok_codes=(0, 1),
        )
    )
    data = {
        "homelab": git_status(REPO_ROOT, "origin"),
        "public_repo": git_status(PUBLIC_REPO, "public")
        if PUBLIC_REPO.exists()
        else missing_git_status(PUBLIC_REPO, "public"),
        "public_mirror": git_status(PUBLIC_REPO, "origin")
        if PUBLIC_REPO.exists()
        else missing_git_status(PUBLIC_REPO, "origin"),
        "machine_readiness": machine,
        "local_offload": offload,
        "idle_ledger": ledger,
        "cubie_runtime_gate": cubie,
        "a733_series_shape": a733_series_shape,
        "public_hygiene": public_hygiene,
    }
    data["workflow_backup"] = workflow_backup_summary(data)
    data["maintainer_ready"] = maintainer_ready_summary(data)
    data["dispatcher_waiting_actions"] = dispatcher_waiting_actions(data)
    data["goal_completion_audit"] = goal_completion_audit(data)
    return data


def md_bool(value: object) -> str:
    return "yes" if value else "no"


def dirty_count(repo_status: dict[str, Any]) -> int:
    status = str(repo_status.get("status_short") or "")
    return len([line for line in status.splitlines() if line.strip()])


def markdown(data: dict[str, Any]) -> str:
    public_repo = data["public_repo"]
    public_mirror = data["public_mirror"]
    homelab = data["homelab"]
    machine = data["machine_readiness"]
    offload = data["local_offload"]
    ledger = data["idle_ledger"]
    cubie = data["cubie_runtime_gate"]
    a733_shape = data["a733_series_shape"]
    public_hygiene = data["public_hygiene"]
    maintainer_ready = data["maintainer_ready"]
    workflow_backup = data["workflow_backup"]
    waiting_actions = data["dispatcher_waiting_actions"]
    goal_audit = data["goal_completion_audit"]

    lines = [
        "# Kernel Workflow Status",
        "",
        "| area | state |",
        "| --- | --- |",
        f"| private workflow repo | clean={md_bool(homelab.get('clean'))}, backed_up={md_bool(homelab.get('remote_matches'))}, head=`{homelab.get('head_short', '')}` |",
        f"| private workflow remote | `{homelab.get('remote_url', '') or 'none'}`; github={md_bool(homelab.get('remote_is_github'))} |",
        f"| workflow backup posture | private_github={md_bool(workflow_backup.get('private_github_backed'))}, public_github={md_bool(workflow_backup.get('public_github_backed'))}, public_mirror={md_bool(workflow_backup.get('public_mirror_backed'))} |",
        f"| public kernel repo | clean={md_bool(public_repo.get('clean'))}, github_backed_up={md_bool(public_repo.get('remote_matches') and public_repo.get('remote_is_github'))}, head=`{public_repo.get('head_short', '')}` |",
        f"| public kernel GitHub remote | `{public_repo.get('remote_url', '') or 'none'}` |",
        f"| thinkcentre public mirror | backed_up={md_bool(public_mirror.get('remote_matches'))} |",
        f"| machine readiness | required_missing={machine.get('required_missing', 'unknown')} |",
        f"| local offload | ok={md_bool(offload.get('ok'))} |",
        f"| idle review ledger | idle_candidates={ledger.get('values', {}).get('idle_review_candidates', 'unknown')}, unconsumed={ledger.get('values', {}).get('unconsumed_reviewed', 'unknown')} |",
        f"| Cubie runtime gate | `{cubie.get('status')}` |",
        f"| human gate | required={md_bool(cubie.get('human_required'))}; {cubie.get('human_gate') or 'none'} |",
        f"| evidence gate | {cubie.get('evidence_gate') or 'none'} |",
        f"| A733 series shape | `{a733_shape.get('status')}`, patches={a733_shape.get('patch_count')}, sendable={md_bool(a733_shape.get('ok'))} |",
        f"| public hygiene | `{public_hygiene.get('status')}`, matches={public_hygiene.get('match_count')}, clean={md_bool(public_hygiene.get('ok'))} |",
        f"| maintainer ready | {md_bool(maintainer_ready.get('ok'))}; blockers={len(maintainer_ready.get('blockers', []))} |",
        f"| goal complete | {md_bool(goal_audit.get('complete'))}; incomplete={len(goal_audit.get('incomplete', []))} |",
        f"| next command | `{cubie.get('next_shell') or cubie.get('next_command') or 'none'}` |",
        f"| next reboot command | `{cubie.get('next_reboot_shell') or cubie.get('next_reboot_command') or 'none'}` |",
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
    if cubie.get("human_gate"):
        lines.extend(["", "## Human Gate", "", str(cubie["human_gate"])])
    if cubie.get("evidence_gate"):
        lines.extend(["", "## Evidence Gate", "", str(cubie["evidence_gate"])])
    lines.extend(["", "## A733 Series Shape", "", str(a733_shape.get("next_action") or "none")])
    if a733_shape.get("finding_kinds"):
        lines.append("")
        lines.append("Findings: " + ", ".join(a733_shape["finding_kinds"]))
    lines.extend(["", "## Public Hygiene", "", str(public_hygiene.get("next_action") or "none")])
    if public_hygiene.get("kinds"):
        lines.append("")
        lines.append("Findings: " + ", ".join(public_hygiene["kinds"]))
    lines.extend(["", "## Maintainer Ready", "", str(maintainer_ready.get("next_action") or "none")])
    for blocker in maintainer_ready.get("blockers", []):
        lines.append(f"- {blocker}")
    lines.extend(["", "## Dispatcher Waiting Actions", ""])
    for action in waiting_actions:
        lines.append(f"- {action}")
    lines.extend(["", "## Goal Completion Audit", ""])
    for item in goal_audit.get("checks", []):
        lines.append(f"- {item['status']}: {item['requirement']} - {item['evidence']}")
    if workflow_backup.get("note"):
        lines.extend(["", "## Workflow Backup Note", "", str(workflow_backup["note"])])
    if workflow_backup.get("next_action"):
        lines.extend(["", "## Workflow Backup Next Action", "", str(workflow_backup["next_action"])])
    return "\n".join(lines) + "\n"


def strict_failed(data: dict[str, Any]) -> bool:
    return bool(strict_blockers(data))


def strict_blockers(data: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not data["homelab"].get("clean"):
        blockers.append("private workflow repo is dirty")
    if not data["homelab"].get("remote_matches"):
        blockers.append("private workflow repo is not backed up to its origin")
    if not data["public_repo"].get("clean"):
        blockers.append("public kernel repo is dirty")
    if not data["public_repo"].get("remote_matches"):
        blockers.append("public kernel repo is not backed up to its public remote")
    if not data["public_mirror"].get("remote_matches"):
        blockers.append("ThinkCentre public mirror is not backed up")
    if data["machine_readiness"].get("required_missing", 1) != 0:
        blockers.append(
            f"machine readiness has {data['machine_readiness'].get('required_missing')} required missing checks"
        )
    if not data["local_offload"].get("ok"):
        blockers.append("local offload lanes are not all healthy")
    if not data["public_hygiene"].get("ok"):
        blockers.append("public hygiene gate is not clean")
    return blockers


def runtime_strict_failed(data: dict[str, Any]) -> bool:
    return strict_failed(data) or data["cubie_runtime_gate"].get("status") != "runtime-ready"


def maintainer_ready_failed(data: dict[str, Any]) -> bool:
    return any(
        [
            runtime_strict_failed(data),
            not data["a733_series_shape"].get("ok"),
            not data["public_hygiene"].get("ok"),
            not data["public_repo"].get("clean"),
            not data["public_repo"].get("remote_matches"),
            not data["public_repo"].get("remote_is_github"),
            not data["public_mirror"].get("remote_matches"),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--next-action",
        action="store_true",
        help="Print only the current deterministic next action.",
    )
    parser.add_argument(
        "--next-command",
        action="store_true",
        help="Print only the current runnable next command when one is known.",
    )
    parser.add_argument(
        "--next-shell",
        action="store_true",
        help="Print a copy-pasteable shell line for the current next command.",
    )
    parser.add_argument(
        "--next-reboot-shell",
        action="store_true",
        help="Print a copy-pasteable shell line for the paired board reboot when one is known.",
    )
    parser.add_argument(
        "--maintainer-ready-blockers",
        action="store_true",
        help="Print one maintainer-readiness blocker per line.",
    )
    parser.add_argument(
        "--maintainer-next-action",
        action="store_true",
        help="Print the ordered next action for maintainer-readiness.",
    )
    parser.add_argument(
        "--maintainer-operator-brief-shell",
        action="store_true",
        help="Print a copy-pasteable read-only operator brief command.",
    )
    parser.add_argument(
        "--workflow-backup-status",
        action="store_true",
        help="Print compact private/public backup posture for dispatcher stopping points.",
    )
    parser.add_argument(
        "--workflow-backup-next-action",
        action="store_true",
        help="Print the next safe backup action without inventing remotes.",
    )
    parser.add_argument(
        "--workflow-dirty-status",
        action="store_true",
        help="Print compact private/public git cleanliness for dispatcher preflight.",
    )
    parser.add_argument(
        "--dispatcher-waiting-actions",
        action="store_true",
        help="Print safe dispatcher actions while a human/hardware gate is pending.",
    )
    parser.add_argument(
        "--goal-completion-audit",
        action="store_true",
        help="Print requirement-level audit for the persistent kernel-maintainer goal.",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--runtime-strict",
        action="store_true",
        help="Exit non-zero unless workflow health and Cubie runtime proof are both ready.",
    )
    parser.add_argument(
        "--maintainer-ready-strict",
        action="store_true",
        help=(
            "Exit non-zero unless the public A733 path is ready for maintainer "
            "preparation: workflow health, runtime proof, series shape, hygiene, "
            "and public backups must all pass."
        ),
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    data = build_status(args)
    if args.next_shell:
        print(data["cubie_runtime_gate"].get("next_shell") or "none")
    elif args.next_reboot_shell:
        print(data["cubie_runtime_gate"].get("next_reboot_shell") or "none")
    elif args.next_command:
        print(data["cubie_runtime_gate"].get("next_command") or "none")
    elif args.next_action:
        print(data["cubie_runtime_gate"].get("next_action") or "none")
    elif args.maintainer_ready_blockers:
        blockers = data["maintainer_ready"].get("blockers") or []
        print("\n".join(blockers) if blockers else "none")
    elif args.maintainer_next_action:
        print(data["maintainer_ready"].get("next_action") or "none")
    elif args.maintainer_operator_brief_shell:
        print(data["maintainer_ready"].get("operator_brief_shell") or "none")
    elif args.workflow_backup_status:
        backup = data["workflow_backup"]
        print(f"private_origin_backed={md_bool(backup.get('private_origin_backed'))}")
        print(f"private_github_backed={md_bool(backup.get('private_github_backed'))}")
        print(f"private_remote_url={backup.get('private_remote_url') or 'none'}")
        print(f"public_github_backed={md_bool(backup.get('public_github_backed'))}")
        print(f"public_mirror_backed={md_bool(backup.get('public_mirror_backed'))}")
        print(f"next_action={backup.get('next_action') or 'none'}")
        if backup.get("note"):
            print(f"note={backup['note']}")
    elif args.workflow_backup_next_action:
        print(data["workflow_backup"].get("next_action") or "none")
    elif args.workflow_dirty_status:
        print(f"private_clean={md_bool(data['homelab'].get('clean'))}")
        print(f"private_dirty_count={dirty_count(data['homelab'])}")
        print(f"public_clean={md_bool(data['public_repo'].get('clean'))}")
        print(f"public_dirty_count={dirty_count(data['public_repo'])}")
    elif args.dispatcher_waiting_actions:
        print("\n".join(data["dispatcher_waiting_actions"]) or "none")
    elif args.goal_completion_audit:
        audit = data["goal_completion_audit"]
        print(f"complete={md_bool(audit.get('complete'))}")
        for item in audit.get("checks", []):
            print(f"{item['status']}: {item['requirement']} - {item['evidence']}")
        print(f"next_action={audit.get('next_action') or 'none'}")
    elif args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data), end="")
    if args.maintainer_ready_strict:
        return 1 if maintainer_ready_failed(data) else 0
    if args.runtime_strict:
        return 1 if runtime_strict_failed(data) else 0
    return 1 if args.strict and strict_failed(data) else 0


if __name__ == "__main__":
    raise SystemExit(main())
