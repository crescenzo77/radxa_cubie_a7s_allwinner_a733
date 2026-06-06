#!/usr/bin/env python3
"""Build a maintainer-review payload and optionally ask the Strix reviewer.

This tool is deliberately evidence-only. It does not apply patches, create
branches, add trailers, or send mail.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import textwrap
from pathlib import Path


REVIEW_PROMPT = "Find three reasons a Linux kernel maintainer would reject this code."


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9_.-]+", "-", value)
    return value.strip("-") or "kernel-review"


def run(command: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise SystemExit(
            f"command failed ({proc.returncode}): {shlex.join(command)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc


def ssh(host: str, remote_command: str, *, check: bool = True) -> str:
    proc = run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, remote_command],
        check=check,
    )
    return proc.stdout


def remote_tree_command(tree_path: str, command: str) -> str:
    return f"cd {shlex.quote(tree_path)} && {command}"


def truncate(text: str, limit: int) -> tuple[str, bool]:
    if limit <= 0 or len(text) <= limit:
        return text, False
    marker = f"\n[truncated {len(text) - limit} chars]\n"
    return text[:limit] + marker, True


def remote_changed_files(host: str, tree_path: str) -> list[str]:
    command = remote_tree_command(
        tree_path,
        "\n".join(
            [
                "git diff --name-only --diff-filter=ACMRTUXB",
                "git ls-files --others --exclude-standard",
            ]
        ),
    )
    files = [line.strip() for line in ssh(host, command).splitlines() if line.strip()]
    return sorted(dict.fromkeys(files))


def remote_untracked_files(host: str, tree_path: str) -> list[str]:
    command = remote_tree_command(tree_path, "git ls-files --others --exclude-standard")
    files = [line.strip() for line in ssh(host, command).splitlines() if line.strip()]
    return sorted(dict.fromkeys(files))


def remote_diff(host: str, tree_path: str, max_chars: int) -> tuple[str, bool]:
    script = r"""
set -e
git diff --no-ext-diff --binary --
git ls-files --others --exclude-standard | while IFS= read -r path; do
  git diff --no-index -- /dev/null "$path" || true
done
"""
    text = ssh(host, remote_tree_command(tree_path, script))
    return truncate(text, max_chars)


def remote_stat(host: str, tree_path: str) -> str:
    script = r"""
set -e
git diff --stat --
git ls-files --others --exclude-standard | while IFS= read -r path; do
  printf 'untracked: %s\n' "$path"
done
"""
    return ssh(host, remote_tree_command(tree_path, script))


def remote_status(host: str, tree_path: str) -> dict[str, str]:
    values = {}
    commands = {
        "head": "git rev-parse HEAD",
        "branch": "git branch --show-current",
        "short_status": "git status --short",
    }
    for key, command in commands.items():
        values[key] = ssh(host, remote_tree_command(tree_path, command)).strip()
    return values


def remote_maintainers(host: str, tree_path: str, files: list[str]) -> str:
    if not files:
        return ""
    quoted = " ".join(shlex.quote(path) for path in files)
    command = remote_tree_command(
        tree_path,
        f"perl scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats -f {quoted} 2>&1",
    )
    return ssh(host, command, check=False).strip()


def proof_summary(host: str, proof_dir: str, proof_id: str) -> dict[str, object]:
    safe = shlex.quote(f"{proof_dir.rstrip('/')}/{proof_id}.json")
    text = ssh(host, f"cat {safe}")
    record = json.loads(text)
    if record.get("proof_id") != proof_id:
        raise SystemExit(f"proof ID mismatch for {proof_id}")
    return {
        "proof_id": proof_id,
        "result": record.get("result"),
        "exit_code": record.get("exit_code"),
        "check": record.get("check"),
        "command_display": record.get("command_display"),
        "record_sha256": record.get("record_sha256"),
        "started_at": record.get("started_at"),
        "ended_at": record.get("ended_at"),
        "stdout_sha256": hashlib.sha256(record.get("stdout", "").encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(record.get("stderr", "").encode()).hexdigest(),
    }


def write_payload(args: argparse.Namespace) -> tuple[Path, Path, dict[str, object], str]:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = remote_changed_files(args.tree_host, args.tree_path)
    untracked = remote_untracked_files(args.tree_host, args.tree_path)
    diff_text, diff_truncated = remote_diff(args.tree_host, args.tree_path, args.max_diff_chars)
    stat_text = remote_stat(args.tree_host, args.tree_path).strip()
    status = remote_status(args.tree_host, args.tree_path)
    maintainers = remote_maintainers(args.tree_host, args.tree_path, files)
    proofs = [proof_summary(args.proof_host, args.proof_dir, proof_id) for proof_id in args.proof_id]

    payload = {
        "schema_version": 1,
        "task_id": args.task_id,
        "created_at": utc_now(),
        "review_prompt": REVIEW_PROMPT,
        "human_gate": {
            "apply_patch_allowed": False,
            "candidate_branch_promotion_allowed": False,
            "signed_off_by_allowed": False,
            "send_email_allowed": False,
        },
        "tree": {
            "host": args.tree_host,
            "path": args.tree_path,
            **status,
        },
        "changed_files": files,
        "untracked_files": untracked,
        "maintainers": maintainers,
        "proofs": proofs,
        "diff_truncated": diff_truncated,
    }

    markdown = textwrap.dedent(
        f"""\
        # Kernel Maintainer Review Payload

        Task ID: `{args.task_id}`
        Created: `{payload["created_at"]}`
        Tree: `{args.tree_host}:{args.tree_path}`
        Base commit: `{status["head"]}`
        Branch: `{status["branch"] or "(detached)"}`

        ## Human Gate

        Do not apply this patch, create a candidate branch, add trailers, or send mail.
        This payload is for maintainer-risk review only.

        ## Required Reviewer Prompt

        {REVIEW_PROMPT}

        ## Changed Files

        ```text
        {chr(10).join(files) if files else "(none)"}
        ```

        ## Diff Stat

        ```text
        {stat_text or "(empty)"}
        ```

        ## Git Status

        ```text
        {status["short_status"] or "(clean)"}
        ```

        ## Maintainer Routing

        ```text
        {maintainers or "(no maintainer output)"}
        ```

        ## Proof Logs

        ```json
        {json.dumps(proofs, indent=2, sort_keys=True)}
        ```

        ## Diff

        ```diff
        {diff_text or "(empty diff)"}
        ```
        """
    )

    digest = hashlib.sha256(markdown.encode()).hexdigest()[:16]
    stem = f"{slugify(args.task_id)}-{digest}"
    md_path = out_dir / f"{stem}.md"
    json_path = out_dir / f"{stem}.json"

    payload["payload_sha256"] = hashlib.sha256(markdown.encode()).hexdigest()
    payload["payload_markdown"] = str(md_path)
    payload["payload_manifest"] = str(json_path)

    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return md_path, json_path, payload, markdown


def ask_strix(args: argparse.Namespace, markdown: str, payload: dict[str, object]) -> tuple[Path, Path]:
    message = f"{REVIEW_PROMPT}\n\n{markdown}"
    request = {
        "model": args.review_model,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0,
        "max_tokens": args.max_review_tokens,
    }
    remote_code = r"""
import json
import sys
import urllib.request

body = json.dumps(json.load(sys.stdin)).encode("utf-8")
request = urllib.request.Request(
    "http://127.0.0.1:8082/v1/chat/completions",
    data=body,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(request, timeout=900) as response:
    sys.stdout.write(response.read().decode("utf-8"))
"""
    proc = run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            args.review_host,
            f"python3 -c {shlex.quote(remote_code)}",
        ],
        input_text=json.dumps(request),
    )

    out_dir = Path(args.out_dir)
    stem = Path(payload["payload_markdown"]).stem
    raw_path = out_dir / f"{stem}.strix-review.raw.json"
    txt_path = out_dir / f"{stem}.strix-review.txt"
    raw_path.write_text(proc.stdout, encoding="utf-8")

    try:
        data = json.loads(proc.stdout)
        text = data["choices"][0]["message"]["content"]
    except Exception:
        text = proc.stdout
    txt_path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return raw_path, txt_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or submit a maintainer review payload.")
    parser.add_argument("action", choices=["payload", "review"])
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--proof-id", action="append", default=[])
    parser.add_argument("--tree-host", default=os.environ.get("KERNEL_TREE_HOST", "192.168.50.252"))
    parser.add_argument(
        "--tree-path",
        default=os.environ.get("KERNEL_TREE_PATH", "/srv/projects/kernel-work/scratch/strix-mainline-linux"),
    )
    parser.add_argument("--proof-host", default=os.environ.get("PROOF_HOST", "192.168.50.252"))
    parser.add_argument("--proof-dir", default=os.environ.get("PROOF_DIR", "/srv/projects/kernel-proof/proof-logs"))
    parser.add_argument("--review-host", default=os.environ.get("REVIEW_HOST", "192.168.50.11"))
    parser.add_argument("--review-model", default=os.environ.get("REVIEW_MODEL", "qwen3.6-27b-q4km-native-vulkan"))
    parser.add_argument("--out-dir", default="task-packets/kernel/reviews")
    parser.add_argument("--max-diff-chars", type=int, default=180000)
    parser.add_argument("--max-review-tokens", type=int, default=2048)
    args = parser.parse_args()

    md_path, json_path, payload, markdown = write_payload(args)
    print(f"payload_markdown={md_path}")
    print(f"payload_manifest={json_path}")
    print(f"payload_sha256={payload['payload_sha256']}")

    if args.action == "review":
        raw_path, txt_path = ask_strix(args, markdown, payload)
        print(f"strix_review_raw={raw_path}")
        print(f"strix_review_text={txt_path}")
        print("halted_for_human_gate=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
