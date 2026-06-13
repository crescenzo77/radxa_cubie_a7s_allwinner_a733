#!/usr/bin/env python3
"""Summarize the current local kernel workflow state."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

import kernel_workflow_env

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ENV = kernel_workflow_env.build_env()
PUBLIC_REPO = Path(WORKFLOW_ENV["paths"]["public_repo"]["selected"])
PATCH_EXPORT = Path(WORKFLOW_ENV["paths"]["patch_export"]["selected"])
LINUX_TREE = Path(WORKFLOW_ENV["paths"]["kernel_tree"]["selected"])
DEFAULT_TIMEOUT = 30
STRIX_HOST = os.environ.get("KERNEL_STRIX_HOST", "192.168.50.11")
STRIX_SSH_TARGET = os.environ.get("KERNEL_STRIX_SSH_TARGET", f"enzo@{STRIX_HOST}")
STRIX_REPO = os.environ.get("KERNEL_STRIX_REPO", "/srv/projects/homelab")
STRIX_REMOTE = os.environ.get("KERNEL_STRIX_REMOTE", "mac-mini")
CUBIE_SSH_USER = os.environ.get("CUBIE_SSH_USER", "codex")
PRIVATE_ORIGIN_REMOTES = [
    item.strip()
    for item in os.environ.get("KERNEL_PRIVATE_ORIGIN_REMOTES", "origin,mac-mini").split(",")
    if item.strip()
]
PRIVATE_GITHUB_REMOTE_SPECS_RAW = os.environ.get(
    "KERNEL_PRIVATE_GITHUB_REMOTE_SPECS",
    "github:main,github-backup:homelab-backup-main",
)
PRIVATE_GITHUB_REMOTE = os.environ.get("KERNEL_PRIVATE_GITHUB_REMOTE", "github")
OPERATOR_BRIEF = "scripts/cubie-corrected-root-operator-brief"
PATCH_PREP_CHECKLIST = "scripts/a733-patch-prep-checklist"
BACKUP_APPROVAL_BRIEF = "scripts/kernel-backup-approval-brief"
PROOF_GATE_SELFTEST = "scripts/cubie-corrected-root-proof-gate-selftest"
RFC_RECHECK_GLOB = "a733-rfc-recheck-*.md"
RFC_RECHECK_DIR = Path(WORKFLOW_ENV["paths"]["rfc_recheck_dir"]["selected"])


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


def parse_remote_specs(raw: str, default_branch: str = "main") -> list[tuple[str, str]]:
    specs: list[tuple[str, str]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            remote, branch = item.split(":", 1)
            specs.append((remote.strip(), branch.strip() or default_branch))
        else:
            specs.append((item, default_branch))
    return specs


PRIVATE_GITHUB_REMOTE_SPECS = parse_remote_specs(PRIVATE_GITHUB_REMOTE_SPECS_RAW)


def git_status(repo: Path, remote: str, branch: str = "main") -> dict[str, Any]:
    status = run(["git", "status", "--short"], cwd=repo)
    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=repo)
    full_head = run(["git", "rev-parse", "HEAD"], cwd=repo)
    remote_url = run(["git", "remote", "get-url", remote], cwd=repo)
    remote_ref = f"refs/heads/{branch}"
    remote_head = run(["git", "ls-remote", remote, remote_ref], cwd=repo, timeout=20)
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
        "remote_branch": branch,
        "remote_ref": remote_ref,
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
        "remote_branch": "main",
        "remote_ref": "refs/heads/main",
        "remote_url": "",
        "remote_is_github": False,
        "remote_head": "",
        "remote_matches": False,
        "errors": ["missing repository"],
    }


def git_status_any(repo: Path, remotes: list[str]) -> dict[str, Any]:
    fallback: dict[str, Any] | None = None
    for remote in remotes:
        status = git_status(repo, remote)
        if fallback is None:
            fallback = status
        if status.get("remote_url"):
            return status
    return fallback or missing_git_status(repo, ",".join(remotes) or "origin")


def git_status_any_spec(repo: Path, specs: list[tuple[str, str]]) -> dict[str, Any]:
    fallback: dict[str, Any] | None = None
    for remote, branch in specs:
        status = git_status(repo, remote, branch)
        if fallback is None:
            fallback = status
        if status.get("remote_matches") and status.get("remote_is_github"):
            return status
        if status.get("remote_url") and fallback is not None and not fallback.get("remote_url"):
            fallback = status
    return fallback or missing_git_status(
        repo,
        ",".join(f"{remote}:{branch}" for remote, branch in specs) or "github:main",
    )


def command_json(
    argv: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    ok_codes: tuple[int, ...] = (0,),
) -> dict[str, Any]:
    proc = run(argv, cwd=REPO_ROOT, timeout=timeout, ok_codes=ok_codes)
    try:
        data = json.loads(proc["stdout"])
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"json decode: {exc}", "stdout": proc["stdout"]}
    if not proc["ok"]:
        return {
            "ok": False,
            "data": data,
            "error": proc["stderr"] or proc["stdout"],
            "returncode": proc["returncode"],
        }
    return {"ok": True, "data": data}


def command_text(argv: list[str], timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    proc = run(argv, cwd=REPO_ROOT, timeout=timeout)
    return {
        "ok": proc["ok"],
        "returncode": proc["returncode"],
        "stdout": proc["stdout"],
        "stderr": proc["stderr"],
    }


def strix_dispatch_shell(command: str, *, tty: bool = False) -> str:
    remote = (
        f"cd {shlex.quote(STRIX_REPO)} && "
        f"git pull --ff-only {shlex.quote(STRIX_REMOTE)} main && "
        f"{command}"
    )
    argv = ["ssh"]
    if tty:
        argv.append("-tt")
    argv.extend([STRIX_SSH_TARGET, remote])
    return shlex.join(argv)


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
    if not data.get("ok") and "data" not in data:
        return {"ok": False, "error": data.get("error", "offload status failed"), "targets": [], "cortex": []}
    status = data["data"]
    target_lines = []
    failures = []
    optional_unavailable = []
    seen_targets = set()
    required_targets = set()
    for target in status.get("targets", []):
        name = str(target.get("name") or "")
        if name:
            seen_targets.add(name)
        required = bool(target.get("required", True))
        if required and name:
            required_targets.add(name)
        note = f" note={target.get('note')}" if target.get("note") else ""
        if target.get("ok"):
            target_lines.append(
                f"{target.get('name')}: ok host={target.get('host')} "
                f"base={target.get('base_url')} models={target.get('models', [])}{note}"
            )
        else:
            line = (
                f"{target.get('name')}: unavailable host={target.get('host')} "
                f"base={target.get('base_url')} required={required} error={target.get('error')}{note}"
            )
            target_lines.append(line)
            if required:
                failures.append(line)
            else:
                optional_unavailable.append(line)
    missing_targets = sorted(required_targets.difference(seen_targets))
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
        "optional_unavailable": optional_unavailable,
        "required_targets": sorted(required_targets),
        "missing_targets": missing_targets,
        "mode": "ready" if not failures else "blocked",
    }


def ledger_summary(text: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": text["ok"], "values": {}, "error": text["stderr"] if not text["ok"] else ""}
    for line in text["stdout"].splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result["values"][key] = value
    return result


def proof_gate_selftest_summary(text: dict[str, Any]) -> dict[str, Any]:
    stdout = text.get("stdout") or ""
    ok = bool(text.get("ok")) and "cubie-corrected-root-proof-gate-selftest=pass" in stdout
    return {
        "ok": ok,
        "returncode": text.get("returncode"),
        "stdout": stdout,
        "stderr": text.get("stderr") or "",
        "next_action": (
            "corrected-root proof gate selftest passes"
            if ok
            else "fix scripts/cubie-corrected-root-proof-gate-selftest before trusting Cubie runtime proof logs"
        ),
    }


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
    if status == "boot-artifact-staging-required":
        next_command = "scripts/cubie-stage-boot-artifacts 192.168.50.85"
        human_required = True
        human_gate = (
            "Board artifact staging changes Cubie2 state. Generate or review "
            "`scripts/cubie-runtime-proof-approval-packet --board cubie2` and get "
            "operator approval before staging."
        )
        evidence_gate = (
            "After staging, rerun `scripts/cubie-runtime-gate --json`; do not write "
            "`/boot`, reboot, or claim proof until the later gates are approved."
        )
    elif status == "root-install-required":
        ready = [row for row in rows if row.get("ready_for_root_install")]
        if ready and ready[0].get("ip"):
            next_command = (
                "scripts/cubie-interactive-root-install-session "
                f"--confirm-target-ip {ready[0]['ip']}"
            )
            human_required = True
            human_gate = (
                "Live UART/operator control is required on Strix; "
                "Codex Desktop should dispatch the Strix command, not run UART locally on the Mac."
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
            next_reboot_command = f"ssh {CUBIE_SSH_USER}@{installed[0]['ip']} 'sudo -n reboot'"
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
        "next_shell": strix_dispatch_shell(next_command, tty=human_required) if next_command else "",
        "next_reboot_command": next_reboot_command,
        "next_reboot_shell": strix_dispatch_shell(next_reboot_command) if next_reboot_command else "",
        "staging": staging,
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
            "series shape is maintainer-aligned for review; require regeneration "
            "from the exact prerequisite branch, normal kernel validation, and "
            "final human review before mailing"
        )
    else:
        next_action = (
            "do not send the current public patch export; reshape to the narrow "
            "board-binding/optional-MMC-binding/SoC-DTSI/board-DTS series after "
            "corrected-root runtime proof"
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


def a733_prereq_api_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {
            "ok": False,
            "status": "unknown",
            "finding_kinds": [],
            "next_action": data.get("error", "A733 prerequisite API audit failed"),
        }
    gate = data["data"]
    findings = gate.get("findings") if isinstance(gate.get("findings"), list) else []
    finding_kinds = [str(item.get("kind")) for item in findings if item.get("kind")]
    if gate.get("status") == "PASS":
        next_action = "A733 DTS references match the checked prerequisite API assumptions"
    else:
        next_action = (
            "reconcile the A733 DTS with prerequisite RFC APIs before regenerating "
            "or mailing patches"
        )
    return {
        "ok": gate.get("status") == "PASS",
        "status": gate.get("status", "unknown"),
        "finding_kinds": finding_kinds,
        "next_action": next_action,
    }


def a733_prereq_stack_summary(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("ok"):
        return {
            "ok": False,
            "status": "unknown",
            "root": str(LINUX_TREE),
            "git_head": "",
            "git_branch": "",
            "git_dirty": False,
            "finding_kinds": [],
            "next_action": data.get("error", "A733 prerequisite stack audit failed"),
        }
    gate = data["data"]
    findings = gate.get("findings") if isinstance(gate.get("findings"), list) else []
    finding_kinds = [str(item.get("kind")) for item in findings if item.get("kind")]
    git = gate.get("git") if isinstance(gate.get("git"), dict) else {}
    if gate.get("status") == "PASS":
        next_action = "chosen A733 prerequisite stack satisfies the checked RTC/CCU/pinctrl/MMC API surface"
    else:
        next_action = (
            "choose or build a clean A733 prerequisite stack before regenerating "
            "the candidate DTS export"
        )
    return {
        "ok": gate.get("status") == "PASS",
        "status": gate.get("status", "unknown"),
        "root": gate.get("root", str(LINUX_TREE)),
        "git_head": git.get("head_short", ""),
        "git_branch": git.get("branch", ""),
        "git_dirty": bool(git.get("dirty")),
        "finding_kinds": finding_kinds,
        "next_action": next_action,
    }


def latest_rfc_recheck_path() -> Path:
    candidates = sorted(RFC_RECHECK_DIR.glob(RFC_RECHECK_GLOB))
    return candidates[-1] if candidates else RFC_RECHECK_DIR / "a733-rfc-recheck-missing.md"


def rfc_recheck_summary(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = latest_rfc_recheck_path()
    if not path.exists():
        return {
            "ok": False,
            "path": str(path),
            "date": "",
            "days_old": None,
            "fresh_today": False,
            "next_action": "run a fresh A733 CCU/pinctrl RFC overlap recheck before patch prep",
            "error": "missing RFC recheck packet",
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^(?:Date|Generated):\s*(\d{4}-\d{2}-\d{2})\b", text, re.MULTILINE)
    checked_date = match.group(1) if match else ""
    days_old = None
    fresh_today = False
    if checked_date:
        try:
            parsed = dt.date.fromisoformat(checked_date)
            today = dt.date.today()
            days_old = (today - parsed).days
            fresh_today = parsed == today
        except ValueError:
            pass
    next_action = (
        "A733 CCU/pinctrl RFC overlap recheck is fresh for today"
        if fresh_today
        else "run a fresh A733 CCU/pinctrl RFC overlap recheck before patch prep"
    )
    return {
        "ok": fresh_today,
        "path": str(path),
        "date": checked_date,
        "days_old": days_old,
        "fresh_today": fresh_today,
        "next_action": next_action,
        "error": "" if checked_date else "could not parse RFC recheck date",
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
    if not data["a733_prereq_api"].get("ok"):
        blockers.append(
            "A733 prerequisite API audit is not clean: "
            + ", ".join(data["a733_prereq_api"].get("finding_kinds", []) or ["unknown"])
        )
    if not data["a733_prereq_stack"].get("ok"):
        blockers.append(
            "A733 prerequisite stack audit is not clean: "
            + ", ".join(data["a733_prereq_stack"].get("finding_kinds", []) or ["unknown"])
        )
    if not data["public_repo"].get("remote_is_github"):
        blockers.append("public kernel repo public remote is not GitHub")
    if not data["a733_rfc_recheck"].get("ok"):
        blockers.append(
            "A733 CCU/pinctrl RFC overlap recheck is stale or missing: "
            + str(data["a733_rfc_recheck"].get("date") or data["a733_rfc_recheck"].get("error") or "unknown")
        )
    if not data["proof_gate_selftest"].get("ok"):
        blockers.append("corrected-root proof gate selftest is failing")

    cubie_next = data["cubie_runtime_gate"].get("next_shell") or data["cubie_runtime_gate"].get("next_command")
    if data["cubie_runtime_gate"].get("status") != "runtime-ready" and cubie_next:
        next_action = str(cubie_next)
    elif data["cubie_runtime_gate"].get("status") != "runtime-ready":
        next_action = str(
            data["cubie_runtime_gate"].get("next_action")
            or "capture and gate the exact v4 corrected-root Cubie runtime proof before patch prep"
        )
    elif not data["a733_series_shape"].get("ok"):
        next_action = (
            "after corrected-root runtime proof, reshape the public export to "
            "the narrow A733 board-binding/optional-MMC-binding/SoC-DTSI/board-DTS "
            "series before patch-prep validation"
        )
    elif not data["a733_prereq_stack"].get("ok"):
        next_action = (
            "choose or build a clean A733 prerequisite stack before regenerating "
            "the candidate DTS export"
        )
    elif not data["a733_prereq_api"].get("ok"):
        next_action = (
            "resolve the A733 prerequisite API audit findings before regenerating "
            "a clean candidate branch"
        )
    elif not data["public_hygiene"].get("ok"):
        next_action = "remove public hygiene matches before public backup or patch prep"
    elif not data["public_repo"].get("clean") or not data["public_repo"].get("remote_matches"):
        next_action = "clean and push the public kernel repo before patch prep"
    elif not data["public_mirror"].get("remote_matches"):
        next_action = "push the public kernel repo to the ThinkCentre mirror before patch prep"
    elif not data["a733_rfc_recheck"].get("ok"):
        next_action = "run a fresh A733 CCU/pinctrl RFC overlap recheck before patch prep"
    elif not data["proof_gate_selftest"].get("ok"):
        next_action = "fix the corrected-root proof gate selftest before patch prep"
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
    homelab_github = data["homelab_github"]
    public_repo = data["public_repo"]
    public_mirror = data["public_mirror"]
    private_github_backed = bool(
        (homelab.get("remote_matches") and homelab.get("remote_is_github"))
        or (homelab_github.get("remote_matches") and homelab_github.get("remote_is_github"))
    )
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
            and private_github_backed
            and public_repo.get("remote_matches")
            and public_repo.get("remote_is_github")
            and public_mirror.get("remote_matches")
        ),
        "private_origin_backed": bool(homelab.get("remote_matches")),
        "private_github_backed": private_github_backed,
        "private_remote_url": homelab.get("remote_url") or "",
        "private_github_remote": homelab_github.get("remote") or PRIVATE_GITHUB_REMOTE,
        "private_github_branch": homelab_github.get("remote_branch") or "main",
        "private_github_remote_url": homelab_github.get("remote_url") or "",
        "public_github_backed": bool(public_repo.get("remote_matches") and public_repo.get("remote_is_github")),
        "public_remote_url": public_repo.get("remote_url") or "",
        "public_mirror_backed": bool(public_mirror.get("remote_matches")),
        "next_action": next_action,
        "note": (
            "private workflow repo is backed up only to its configured origin; "
            "no GitHub remote is configured"
            if homelab.get("remote_matches") and not private_github_backed
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
            "preserve series guardrail: current export is not maintainer-aligned; "
            "do not create or send maintainer-facing patches before reshaping it"
        )
    if not data["a733_prereq_api"].get("ok"):
        actions.append(
            "resolve prerequisite API audit before candidate regeneration: "
            + str(data["a733_prereq_api"].get("next_action"))
        )
    if not data["a733_prereq_stack"].get("ok"):
        actions.append(
            "choose or build clean A733 prerequisite stack: "
            + str(data["a733_prereq_stack"].get("next_action"))
        )
    if not data["a733_rfc_recheck"].get("ok"):
        actions.append(
            "refresh external overlap evidence before patch prep: "
            + str(data["a733_rfc_recheck"].get("next_action"))
        )
    if not data["proof_gate_selftest"].get("ok"):
        actions.append(
            "fix proof classifier before live proof use: "
            + str(data["proof_gate_selftest"].get("next_action"))
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
            "status": "pass" if data["a733_series_shape"].get("ok") else "fail",
            "evidence": (
                "series-shape gate passes for the narrow review export"
                if data["a733_series_shape"].get("ok")
                else "series-shape gate blocks the current export from maintainer use"
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
            "requirement": "A733 DTS matches prerequisite API assumptions",
            "status": "pass" if data["a733_prereq_api"].get("ok") else "fail",
            "evidence": data["a733_prereq_api"].get("next_action") or "",
        },
        {
            "requirement": "chosen A733 prerequisite stack is cleanly audited",
            "status": "pass" if data["a733_prereq_stack"].get("ok") else "fail",
            "evidence": (
                data["a733_prereq_stack"].get("next_action")
                + " on "
                + str(data["a733_prereq_stack"].get("root") or "unknown tree")
            ),
        },
        {
            "requirement": "A733 CCU/pinctrl RFC overlap state is freshly rechecked",
            "status": "pass" if data["a733_rfc_recheck"].get("ok") else "fail",
            "evidence": (
                "RFC overlap recheck is fresh for today"
                if data["a733_rfc_recheck"].get("ok")
                else (
                    f"latest local RFC recheck is {data['a733_rfc_recheck'].get('date') or 'missing'}; "
                    "refresh before patch prep"
                )
            ),
        },
        {
            "requirement": "corrected-root proof classifier selftest passes",
            "status": "pass" if data["proof_gate_selftest"].get("ok") else "fail",
            "evidence": data["proof_gate_selftest"].get("next_action") or "",
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
            "requirement": "private workflow work is backed up locally and to GitHub at stopping points",
            "status": "pass"
            if data["workflow_backup"].get("private_origin_backed")
            and data["workflow_backup"].get("private_github_backed")
            else "fail",
            "evidence": (
                "private workflow origin and GitHub remote both match HEAD"
                if data["workflow_backup"].get("private_origin_backed")
                and data["workflow_backup"].get("private_github_backed")
                else data["workflow_backup"].get("note")
                or "private workflow local origin or GitHub backup is incomplete"
            ),
        },
    ]
    incomplete = [item for item in checks if item["status"] != "pass"]
    return {
        "complete": not incomplete,
        "checks": checks,
        "incomplete": incomplete,
        "next_action": data["maintainer_ready"].get("next_action") or "none",
    }


def stopping_point_audit(data: dict[str, Any]) -> dict[str, Any]:
    """Summarize what Codex should do before pausing at a kernel-work stop."""
    workflow_backup = data["workflow_backup"]
    public_repo = data["public_repo"]
    public_mirror = data["public_mirror"]
    homelab = data["homelab"]
    cubie = data["cubie_runtime_gate"]
    checks = [
        {
            "name": "private workflow commit",
            "status": "attention" if homelab.get("status_short") else "ok",
            "detail": (
                f"{dirty_count(homelab)} private workflow paths are dirty; commit only scoped work"
                if homelab.get("status_short")
                else f"private workflow tree clean at {homelab.get('head_short', '')}"
            ),
        },
        {
            "name": "private workflow origin backup",
            "status": "ok" if workflow_backup.get("private_origin_backed") else "fail",
            "detail": (
                f"origin `{workflow_backup.get('private_remote_url')}` matches HEAD"
                if workflow_backup.get("private_origin_backed")
                else "push private workflow repo to its configured origin"
            ),
        },
        {
            "name": "private workflow GitHub backup",
            "status": "human-approval-required"
            if workflow_backup.get("private_origin_backed") and not workflow_backup.get("private_github_backed")
            else ("ok" if workflow_backup.get("private_github_backed") else "fail"),
            "detail": (
                "no matching GitHub remote is configured; do not invent or add one without explicit human approval"
                if not workflow_backup.get("private_github_backed")
                else "private workflow GitHub remote matches HEAD"
            ),
        },
        {
            "name": "public kernel GitHub backup",
            "status": "ok" if workflow_backup.get("public_github_backed") else "fail",
            "detail": (
                f"public remote `{public_repo.get('remote_url')}` matches HEAD"
                if workflow_backup.get("public_github_backed")
                else "push public kernel repo to its GitHub remote before public handoff"
            ),
        },
        {
            "name": "public kernel mirror backup",
            "status": "ok" if workflow_backup.get("public_mirror_backed") else "fail",
            "detail": (
                f"mirror `{public_mirror.get('remote_url')}` matches HEAD"
                if workflow_backup.get("public_mirror_backed")
                else "push public kernel repo to the ThinkCentre mirror"
            ),
        },
        {
            "name": "maintainer guardrail",
            "status": "ok" if data["a733_series_shape"].get("ok") else "attention",
            "detail": (
                "series shape passes for the narrow review export; do not mail before final branch regeneration and validation"
                if data["a733_series_shape"].get("ok")
                else "current public export is not maintainer-aligned; do not send it"
            ),
        },
        {
            "name": "A733 prerequisite API audit",
            "status": "ok" if data["a733_prereq_api"].get("ok") else "attention",
            "detail": (
                data["a733_prereq_api"].get("next_action")
                or "audit A733 DTS references against CCU/pinctrl/MMC prerequisite APIs"
            ),
        },
        {
            "name": "A733 RFC overlap freshness",
            "status": "ok" if data["a733_rfc_recheck"].get("ok") else "attention",
            "detail": (
                "fresh for today"
                if data["a733_rfc_recheck"].get("ok")
                else (
                    f"latest local recheck is {data['a733_rfc_recheck'].get('date') or 'missing'}; "
                    "refresh before patch prep"
                )
            ),
        },
        {
            "name": "corrected-root proof gate selftest",
            "status": "ok" if data["proof_gate_selftest"].get("ok") else "fail",
            "detail": data["proof_gate_selftest"].get("next_action") or "unknown",
        },
        {
            "name": "next safe action",
            "status": "human-required" if cubie.get("human_required") else "ok",
            "detail": data["maintainer_ready"].get("next_action") or "none",
        },
    ]
    return {"checks": checks, "next_action": data["maintainer_ready"].get("next_action") or "none"}


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
                str(PATCH_EXPORT),
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
    a733_prereq_api = a733_prereq_api_summary(
        command_json(
            [
                str(REPO_ROOT / "scripts" / "a733-prereq-api-audit"),
                str(PATCH_EXPORT),
                "--json",
            ],
            timeout=args.timeout,
            ok_codes=(0, 1),
        )
    )
    a733_prereq_stack = a733_prereq_stack_summary(
        command_json(
            [
                str(REPO_ROOT / "scripts" / "a733-prereq-stack-audit"),
                str(LINUX_TREE),
                "--json",
            ],
            timeout=args.timeout,
            ok_codes=(0, 1),
        )
    )
    proof_gate_selftest = proof_gate_selftest_summary(
        command_text([str(REPO_ROOT / "scripts" / "cubie-corrected-root-proof-gate-selftest")], timeout=args.timeout)
    )
    data = {
        "homelab": git_status_any(REPO_ROOT, PRIVATE_ORIGIN_REMOTES),
        "homelab_github": git_status_any_spec(REPO_ROOT, PRIVATE_GITHUB_REMOTE_SPECS),
        "path_registry": WORKFLOW_ENV,
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
        "a733_prereq_api": a733_prereq_api,
        "a733_prereq_stack": a733_prereq_stack,
        "a733_rfc_recheck": rfc_recheck_summary(),
        "proof_gate_selftest": proof_gate_selftest,
    }
    data["workflow_backup"] = workflow_backup_summary(data)
    data["maintainer_ready"] = maintainer_ready_summary(data)
    data["dispatcher_waiting_actions"] = dispatcher_waiting_actions(data)
    data["goal_completion_audit"] = goal_completion_audit(data)
    data["stopping_point_audit"] = stopping_point_audit(data)
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
    a733_prereq_api = data["a733_prereq_api"]
    a733_prereq_stack = data["a733_prereq_stack"]
    a733_rfc_recheck = data["a733_rfc_recheck"]
    proof_gate_selftest = data["proof_gate_selftest"]
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
        f"| private workflow origin | `{homelab.get('remote_url', '') or 'none'}` |",
        (
            f"| private workflow GitHub remote | `{workflow_backup.get('private_github_remote')}` -> "
            f"`{workflow_backup.get('private_github_remote_url') or 'none'}`; "
            f"backed_up={md_bool(workflow_backup.get('private_github_backed'))} |"
        ),
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
        f"| A733 series shape | `{a733_shape.get('status')}`, patches={a733_shape.get('patch_count')}, shape_ok={md_bool(a733_shape.get('ok'))} |",
        f"| A733 prerequisite API audit | `{a733_prereq_api.get('status')}`, clean={md_bool(a733_prereq_api.get('ok'))} |",
        f"| A733 prerequisite stack | `{a733_prereq_stack.get('status')}`, clean={md_bool(a733_prereq_stack.get('ok'))}, tree=`{a733_prereq_stack.get('root')}` |",
        f"| A733 RFC overlap recheck | fresh_today={md_bool(a733_rfc_recheck.get('ok'))}, date=`{a733_rfc_recheck.get('date') or 'missing'}` |",
        f"| corrected-root proof gate selftest | ok={md_bool(proof_gate_selftest.get('ok'))} |",
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
    lines.extend(["", "## A733 Prerequisite API Audit", "", str(a733_prereq_api.get("next_action") or "none")])
    if a733_prereq_api.get("finding_kinds"):
        lines.append("")
        lines.append("Findings: " + ", ".join(a733_prereq_api["finding_kinds"]))
    lines.extend(["", "## A733 Prerequisite Stack Audit", "", str(a733_prereq_stack.get("next_action") or "none")])
    lines.append(
        f"Tree: `{a733_prereq_stack.get('root')}`; "
        f"branch=`{a733_prereq_stack.get('git_branch') or 'unknown'}`; "
        f"head=`{a733_prereq_stack.get('git_head') or 'unknown'}`; "
        f"dirty={md_bool(a733_prereq_stack.get('git_dirty'))}"
    )
    if a733_prereq_stack.get("finding_kinds"):
        lines.append("")
        lines.append("Findings: " + ", ".join(a733_prereq_stack["finding_kinds"]))
    lines.extend(["", "## A733 RFC Overlap Freshness", "", str(a733_rfc_recheck.get("next_action") or "none")])
    if a733_rfc_recheck.get("path"):
        lines.append(f"Evidence packet: `{a733_rfc_recheck.get('path')}`")
    if a733_rfc_recheck.get("days_old") is not None:
        lines.append(f"Days old: {a733_rfc_recheck.get('days_old')}")
    lines.extend(["", "## Corrected-Root Proof Gate Selftest", "", str(proof_gate_selftest.get("next_action") or "none")])
    if proof_gate_selftest.get("stderr"):
        lines.append(f"stderr: `{proof_gate_selftest.get('stderr')}`")
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
    lines.extend(["", "## Stopping Point Audit", ""])
    for item in data["stopping_point_audit"].get("checks", []):
        lines.append(f"- {item['status']}: {item['name']} - {item['detail']}")
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
    if not data["proof_gate_selftest"].get("ok"):
        blockers.append("corrected-root proof gate selftest is failing")
    return blockers


def runtime_strict_failed(data: dict[str, Any]) -> bool:
    return strict_failed(data) or data["cubie_runtime_gate"].get("status") != "runtime-ready"


def maintainer_ready_failed(data: dict[str, Any]) -> bool:
    return any(
        [
            runtime_strict_failed(data),
            not data["a733_series_shape"].get("ok"),
            not data["a733_prereq_api"].get("ok"),
            not data["a733_prereq_stack"].get("ok"),
            not data["public_hygiene"].get("ok"),
            not data["public_repo"].get("clean"),
            not data["public_repo"].get("remote_matches"),
            not data["public_repo"].get("remote_is_github"),
            not data["public_mirror"].get("remote_matches"),
            not data["a733_rfc_recheck"].get("ok"),
            not data["proof_gate_selftest"].get("ok"),
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
        "--a733-rfc-recheck-status",
        action="store_true",
        help="Print freshness of the local A733 CCU/pinctrl RFC overlap recheck.",
    )
    parser.add_argument(
        "--a733-prereq-stack-status",
        action="store_true",
        help="Print compact status for the chosen A733 prerequisite Linux tree.",
    )
    parser.add_argument(
        "--proof-gate-selftest-status",
        action="store_true",
        help="Print corrected-root proof gate selftest status.",
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
    parser.add_argument(
        "--stopping-point-audit",
        action="store_true",
        help="Print dispatcher stop/pause checks: scoped commits, backups, guardrails, and next action.",
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
            "prerequisite stack/API, and public backups must all pass."
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
        print(f"private_github_remote={backup.get('private_github_remote') or 'none'}")
        print(f"private_github_remote_url={backup.get('private_github_remote_url') or 'none'}")
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
    elif args.a733_rfc_recheck_status:
        recheck = data["a733_rfc_recheck"]
        print(f"fresh_today={md_bool(recheck.get('ok'))}")
        print(f"date={recheck.get('date') or 'missing'}")
        print(f"days_old={recheck.get('days_old') if recheck.get('days_old') is not None else 'unknown'}")
        print(f"path={recheck.get('path') or 'none'}")
        print(f"next_action={recheck.get('next_action') or 'none'}")
        if recheck.get("error"):
            print(f"error={recheck['error']}")
    elif args.a733_prereq_stack_status:
        stack = data["a733_prereq_stack"]
        print(f"status={stack.get('status') or 'unknown'}")
        print(f"clean={md_bool(stack.get('ok'))}")
        print(f"tree={stack.get('root') or 'unknown'}")
        print(f"branch={stack.get('git_branch') or 'unknown'}")
        print(f"head={stack.get('git_head') or 'unknown'}")
        print(f"dirty={md_bool(stack.get('git_dirty'))}")
        print("findings=" + ",".join(stack.get("finding_kinds") or []))
        print(f"next_action={stack.get('next_action') or 'none'}")
    elif args.proof_gate_selftest_status:
        selftest = data["proof_gate_selftest"]
        print(f"ok={md_bool(selftest.get('ok'))}")
        print(f"returncode={selftest.get('returncode')}")
        print(f"next_action={selftest.get('next_action') or 'none'}")
        if selftest.get("stdout"):
            print(f"stdout={selftest['stdout']}")
        if selftest.get("stderr"):
            print(f"stderr={selftest['stderr']}")
    elif args.dispatcher_waiting_actions:
        print("\n".join(data["dispatcher_waiting_actions"]) or "none")
    elif args.goal_completion_audit:
        audit = data["goal_completion_audit"]
        print(f"complete={md_bool(audit.get('complete'))}")
        for item in audit.get("checks", []):
            print(f"{item['status']}: {item['requirement']} - {item['evidence']}")
        print(f"next_action={audit.get('next_action') or 'none'}")
    elif args.stopping_point_audit:
        audit = data["stopping_point_audit"]
        for item in audit.get("checks", []):
            print(f"{item['status']}: {item['name']} - {item['detail']}")
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
