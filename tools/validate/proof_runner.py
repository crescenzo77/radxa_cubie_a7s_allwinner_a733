#!/usr/bin/env python3
"""Run one validation command and write a hashed proof log.

The runner is intentionally small and boring. It is the authority for terminal
results: models may summarize proof IDs, but they do not get to invent PASS.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shlex
import socket
import subprocess
import sys
import time
import uuid


BUILTIN_COMMANDS = {
    "dummy-pass": ["bash", "-lc", "printf 'dummy proof pass\\n'"],
    "dummy-fail": ["bash", "-lc", "printf 'dummy proof failure\\n' >&2; exit 7"],
    "version-report": [
        "bash",
        "-lc",
        (
            "git --version; "
            "make --version | sed -n '1p'; "
            "aarch64-linux-gnu-gcc --version | sed -n '1p'; "
            "dtc --version; "
            "yamllint --version; "
            "dt-validate --version 2>/dev/null || true; "
            "sparse --version 2>/dev/null || true; "
            "python3 --version"
        ),
    ],
    "checkpatch-current-diff-strict": [
        "bash",
        "-lc",
        r"""
set -euo pipefail
patch_file="$(mktemp)"
trap 'rm -f "$patch_file"' EXIT
git diff --no-ext-diff --binary -- > "$patch_file"
git ls-files --others --exclude-standard | while IFS= read -r path; do
  git diff --no-index -- /dev/null "$path" >> "$patch_file" || true
done
if [ ! -s "$patch_file" ]; then
  printf 'no current diff\n'
  exit 0
fi
perl scripts/checkpatch.pl --strict "$patch_file"
""",
    ],
    "checkpatch-warning-gate": [
        "bash",
        "-lc",
        r"""
set -euo pipefail
shopt -s nullglob
patches=(export-patches/000*.patch)
if [ "${#patches[@]}" -eq 0 ]; then
  printf 'no exported patches found under export-patches/000*.patch\n' >&2
  exit 2
fi
checkpatch-warning-gate --checkpatch-tree . --maintainers MAINTAINERS "${patches[@]}"
""",
    ],
    "trailer-gate": [
        "bash",
        "-lc",
        r"""
set -euo pipefail
shopt -s nullglob
patches=(export-patches/000*.patch)
if [ "${#patches[@]}" -eq 0 ]; then
  printf 'no exported patches found under export-patches/000*.patch\n' >&2
  exit 2
fi
trailer-gate "${patches[@]}"
""",
    ],
    "public-hygiene-gate": [
        "bash",
        "-lc",
        r"""
set -euo pipefail
public-hygiene-gate .
""",
    ],
    "cubie-a7s-dtbs-check": [
        "bash",
        "-lc",
        r"""
set -euo pipefail
rm -f arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dtb
rm -f arch/arm64/boot/dts/allwinner/.sun60i-a733-cubie-a7s.dtb.*
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig >/dev/null
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig >/dev/null
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CHECK_DTBS=y allwinner/sun60i-a733-cubie-a7s.dtb
""",
    ],
}

ALLOWED_PREFIXES = {
    "git-diff-check": [["git", "diff", "--check"]],
    "checkpatch-strict": [["perl", "scripts/checkpatch.pl", "--strict"], ["scripts/checkpatch.pl", "--strict"]],
    "checkpatch-warning-gate": [["checkpatch-warning-gate"]],
    "trailer-gate": [["trailer-gate"]],
    "public-hygiene-gate": [["public-hygiene-gate"]],
}

VERSION_COMMANDS = {
    "git": ["git", "--version"],
    "make": ["bash", "-lc", "make --version | sed -n '1p'"],
    "aarch64_gcc": ["bash", "-lc", "aarch64-linux-gnu-gcc --version | sed -n '1p'"],
    "dtc": ["dtc", "--version"],
    "yamllint": ["yamllint", "--version"],
    "dtschema": ["bash", "-lc", "dt-validate --version 2>/dev/null || python3 -m pip show dtschema | sed -n 's/^Version: //p'"],
    "sparse": ["bash", "-lc", "sparse --version 2>/dev/null || true"],
    "perl": ["bash", "-lc", "perl -e 'printf \"%vd\\n\", $^V'"],
    "python": ["python3", "--version"],
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def run_text(command, cwd=None, env=None, timeout=20):
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except Exception as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
        }


def collect_versions(cwd, env):
    return {name: run_text(command, cwd=cwd, env=env) for name, command in VERSION_COMMANDS.items()}


def parse_env(items):
    env = os.environ.copy()
    recorded = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid --env value, expected KEY=VALUE: {item}")
        key, value = item.split("=", 1)
        env[key] = value
        recorded[key] = value
    return env, recorded


def command_allowed(check, command):
    if check in BUILTIN_COMMANDS:
        return True
    prefixes = ALLOWED_PREFIXES.get(check, [])
    for prefix in prefixes:
        if command[: len(prefix)] == prefix:
            return True
    if check == "dt-binding-check":
        return command[:1] == ["make"] and "dt_binding_check" in command
    if check == "dtbs-check":
        return command[:1] == ["make"] and (
            "dtbs_check" in command or any(arg == "CHECK_DTBS=y" for arg in command)
        )
    if check == "arm64-build":
        return command[:1] == ["make"] and any(arg == "ARCH=arm64" for arg in command)
    if check == "object-build":
        return command[:1] == ["make"]
    if check == "sparse":
        return command[:1] == ["sparse"] or (
            command[:1] == ["make"] and any(arg in {"C=1", "C=2"} for arg in command)
        )
    return False


def command_from_args(check, raw_command):
    if raw_command:
        return raw_command
    if check in BUILTIN_COMMANDS:
        return BUILTIN_COMMANDS[check]
    raise SystemExit(f"check '{check}' requires an explicit command after --")


def excerpt(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n[truncated {len(text) - limit} chars]"


def effective_result(check, returncode, stdout, stderr):
    if returncode != 0:
        return "FAIL", returncode, "command returned nonzero"
    if check in {"dt-binding-check", "dtbs-check", "cubie-a7s-dtbs-check"} and stderr.strip():
        return "FAIL", 1, "devicetree validation wrote stderr"
    return "PASS", 0, "command returned zero"


def main():
    parser = argparse.ArgumentParser(description="Run one kernel validation proof command.")
    parser.add_argument("--proof-dir", default="/proof-logs")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--check", required=True)
    parser.add_argument("--workdir", default="/workspace")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("--stdout-excerpt-chars", type=int, default=4000)
    parser.add_argument("--stderr-excerpt-chars", type=int, default=4000)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    raw_command = args.command
    if raw_command and raw_command[0] == "--":
        raw_command = raw_command[1:]
    command = command_from_args(args.check, raw_command)

    if not command_allowed(args.check, command):
        allowed = ALLOWED_PREFIXES.get(args.check, [])
        raise SystemExit(
            f"refusing command for check '{args.check}': {shlex.join(command)}; "
            f"allowed prefixes: {allowed}"
        )

    env, recorded_env = parse_env(args.env)
    os.makedirs(args.proof_dir, exist_ok=True)

    started = utc_now()
    start_perf = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=args.workdir,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout,
        check=False,
    )
    ended = utc_now()
    duration = time.perf_counter() - start_perf

    result, effective_exit_code, result_reason = effective_result(
        args.check, proc.returncode, proc.stdout, proc.stderr
    )
    proof_id = f"{args.task_id}-{args.check}-{uuid.uuid4().hex[:12]}"

    record = {
        "schema_version": 1,
        "proof_id": proof_id,
        "task_id": args.task_id,
        "check": args.check,
        "result": result,
        "exit_code": effective_exit_code,
        "command_exit_code": proc.returncode,
        "result_reason": result_reason,
        "command": command,
        "command_display": shlex.join(command),
        "workdir": args.workdir,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "started_at": started,
        "ended_at": ended,
        "duration_seconds": duration,
        "recorded_env": recorded_env,
        "tool_versions": collect_versions(args.workdir, env),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    record_hash = hashlib.sha256(canonical).hexdigest()
    record["record_sha256"] = record_hash

    proof_path = os.path.join(args.proof_dir, f"{proof_id}.json")
    with open(proof_path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    summary = {
        "proof_id": proof_id,
        "proof_path": proof_path,
        "record_sha256": record_hash,
        "task_id": args.task_id,
        "check": args.check,
        "result": result,
        "exit_code": effective_exit_code,
        "command_exit_code": proc.returncode,
        "result_reason": result_reason,
        "duration_seconds": duration,
        "stdout_excerpt": excerpt(proc.stdout, args.stdout_excerpt_chars),
        "stderr_excerpt": excerpt(proc.stderr, args.stderr_excerpt_chars),
    }
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return effective_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
