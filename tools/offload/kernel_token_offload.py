#!/usr/bin/env python3
"""Local token-offload helpers for kernel work.

The tool turns large local inputs into small context cards by using local
search/model services first. It does not edit code, validate patches, add
trailers, promote branches, or send mail.
"""

from __future__ import annotations

import argparse
import concurrent.futures
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
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CARD_DIR = REPO_ROOT / "task-packets" / "kernel" / "context-cards"
DEFAULT_LEDGER = DEFAULT_CARD_DIR / "idle-review-ledger.json"
DEFAULT_IDLE_ROOTS = ["task-packets/kernel/reviews", "task-packets/kernel/research"]
DEFAULT_REVIEW_TARGETS = ["amd-fast", "amd-research", "strix-review"]

TARGETS: dict[str, dict[str, Any]] = {
    "amd-research": {
        "host": "192.168.50.252",
        "base_url": "http://127.0.0.1:8092/v1",
        "model": "qwen36-27b-7900xt-research",
        "chat_template_kwargs": {"enable_thinking": False},
        "role": "batch research and synthesis",
    },
    "amd-fast": {
        "host": "192.168.50.252",
        "base_url": "http://127.0.0.1:8001/v1",
        "model": "qwen3.6-27b-q4km-amd-rtx3090-vulkan",
        "chat_template_kwargs": {"enable_thinking": False},
        "role": "fast short-context triage if endpoint is running",
    },
    "strix-review": {
        "host": "192.168.50.11",
        "base_url": "http://127.0.0.1:8080/v1",
        "model": "qwen3.6-27b-rocmfp4-mtp",
        "role": "longer maintainer-style review on the Qwen3.6 27B ROCmFP4-MTP headQ6 trial endpoint",
    },
}

THINKCENTRE_HOST = "192.168.50.225"
THINKCENTRE_CORTEX_TOOL = "/srv/projects/kernel-services/cortex/tools/kernel_cortex.py"
QDRANT_URL = "http://127.0.0.1:6333"
EMBEDDING_API_BASE = "http://192.168.50.252:8091/v1"
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

SIGNAL_RE = re.compile(
    r"(" +
    r"\b(error|warning|failed|failure|fatal|traceback|undefined|unrecognized|"
    r"reject|invalid|missing|duplicate|conflict|oops|panic)\b" +
    r"|scripts/checkpatch\.pl|dt_binding_check|dtbs_check|CHECK_DTBS|"
    r"^\s*(ERROR|WARNING|CHECK):" +
    r")",
    re.IGNORECASE,
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9_.-]+", "-", value)
    return value.strip("-") or "context-card"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(
    command: list[str],
    *,
    input_text: str | None = None,
    cwd: str | None = None,
    check: bool = True,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        input=input_text,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    if check and proc.returncode != 0:
        raise SystemExit(
            f"command failed ({proc.returncode}): {shlex.join(command)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def ssh(host: str, remote_command: str, *, input_text: str | None = None, check: bool = True, timeout: int = 120) -> str:
    proc = run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, remote_command],
        input_text=input_text,
        check=check,
        timeout=timeout,
    )
    return proc.stdout


def truncate_middle(text: str, limit: int) -> tuple[str, bool]:
    if limit <= 0 or len(text) <= limit:
        return text, False
    keep = max(1000, limit // 2)
    head = text[:keep]
    tail = text[-keep:]
    omitted = len(text) - len(head) - len(tail)
    return f"{head}\n\n[... omitted {omitted} chars ...]\n\n{tail}", True


def read_text_source(path: str) -> tuple[str, dict[str, Any]]:
    if path == "-":
        text = sys.stdin.read()
        return text, {"source_type": "stdin", "source_path": "-"}
    source = Path(path)
    text = source.read_text(encoding="utf-8", errors="replace")
    return text, {
        "source_type": "file",
        "source_path": str(source),
        "source_sha256": sha256_text(text),
        "source_chars": len(text),
    }


def proof_json_to_text(path: str) -> tuple[str, dict[str, Any]]:
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    data = json.loads(raw)
    stdout = data.get("stdout", "")
    stderr = data.get("stderr", "")
    text = textwrap.dedent(
        f"""\
        proof_id: {data.get("proof_id")}
        task_id: {data.get("task_id")}
        check: {data.get("check")}
        result: {data.get("result")}
        exit_code: {data.get("exit_code")}
        command: {data.get("command_display")}
        result_reason: {data.get("result_reason")}

        stdout:
        {stdout}

        stderr:
        {stderr}
        """
    )
    return text, {
        "source_type": "proof_json",
        "source_path": path,
        "source_sha256": sha256_text(raw),
        "source_chars": len(raw),
        "proof_id": data.get("proof_id"),
        "proof_result": data.get("result"),
        "proof_check": data.get("check"),
        "proof_exit_code": data.get("exit_code"),
    }


def extract_signal_lines(text: str, limit: int = 80) -> list[str]:
    seen: set[str] = set()
    signals: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or not SIGNAL_RE.search(line):
            continue
        normalized = re.sub(r"\s+", " ", line.strip())
        if normalized in seen:
            continue
        seen.add(normalized)
        signals.append(line[:500])
        if len(signals) >= limit:
            break
    return signals


def remote_models(target_name: str) -> dict[str, Any]:
    target = TARGETS[target_name]
    request = {"base_url": target["base_url"]}
    code = r"""
import json
import sys
import urllib.request

req = json.load(sys.stdin)
url = req["base_url"].rstrip("/") + "/models"
with urllib.request.urlopen(url, timeout=20) as response:
    sys.stdout.write(response.read().decode("utf-8"))
"""
    return json.loads(ssh(target["host"], f"python3 -c {shlex.quote(code)}", input_text=json.dumps(request), timeout=40))


def choose_model(target_name: str) -> str:
    configured = TARGETS[target_name].get("model")
    if configured:
        return configured
    data = remote_models(target_name)
    models = [item.get("id") for item in data.get("data", []) if item.get("id")]
    if not models:
        raise SystemExit(f"target {target_name} has no advertised model")
    return models[0]


def chat_local_model(
    target_name: str,
    prompt: str,
    *,
    system: str = "",
    max_tokens: int = 800,
    temperature: float = 0.0,
) -> tuple[str, dict[str, Any]]:
    target = TARGETS[target_name]
    model = choose_model(target_name)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload: dict[str, Any] = {
        "base_url": target["base_url"],
        "request": {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    }
    if target.get("chat_template_kwargs"):
        payload["request"]["chat_template_kwargs"] = target["chat_template_kwargs"]

    code = r"""
import json
import sys
import urllib.request

outer = json.load(sys.stdin)
url = outer["base_url"].rstrip("/") + "/chat/completions"
body = json.dumps(outer["request"]).encode("utf-8")
request = urllib.request.Request(
    url,
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=900) as response:
    sys.stdout.write(response.read().decode("utf-8"))
"""
    raw = ssh(target["host"], f"python3 -c {shlex.quote(code)}", input_text=json.dumps(payload), timeout=960)
    data = json.loads(raw)
    text = data.get("choices", [{}])[0].get("message", {}).get("content") or ""
    meta = {
        "target": target_name,
        "host": target["host"],
        "base_url": target["base_url"],
        "model": model,
        "usage": data.get("usage", {}),
        "raw_response_sha256": sha256_text(raw),
    }
    return text.strip(), meta


def write_card(
    *,
    kind: str,
    title: str,
    source: dict[str, Any],
    deterministic_extract: str,
    local_summary: str,
    model_meta: dict[str, Any] | None,
    out_dir: str,
    extra: dict[str, Any] | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    created = utc_now()
    raw_chars = int(source.get("source_chars") or len(deterministic_extract))
    markdown = textwrap.dedent(
        f"""\
        # {title}

        Kind: `{kind}`
        Created: `{created}`

        ## Local Summary

        {local_summary.strip() or "(no model summary requested)"}

        ## Deterministic Extract

        ```text
        {deterministic_extract.strip() or "(empty)"}
        ```

        ## Source

        ```json
        {json.dumps(source, indent=2, sort_keys=True)}
        ```

        ## Model

        ```json
        {json.dumps(model_meta or {"target": "none"}, indent=2, sort_keys=True)}
        ```

        This context card is advisory. Validation proof logs, git diffs, and
        human approval remain authoritative.
        """
    )
    card_chars = len(markdown)
    card = {
        "schema_version": 1,
        "kind": kind,
        "title": title,
        "created_at": created,
        "source": source,
        "model": model_meta or {"target": "none"},
        "deterministic_extract": deterministic_extract,
        "local_summary": local_summary,
        "metrics": {
            "source_chars": raw_chars,
            "card_chars": card_chars,
            "approx_char_compression": round(raw_chars / max(card_chars, 1), 3),
        },
        "extra": extra or {},
        "human_gate": {
            "may_edit_code": False,
            "may_declare_validation_pass": False,
            "may_add_trailers": False,
            "may_send_mail": False,
        },
    }
    digest = sha256_text(json.dumps(card, sort_keys=True))[:12]
    stem = f"{slugify(kind)}-{slugify(title)}-{digest}"
    md_path = out / f"{stem}.md"
    json_path = out / f"{stem}.json"
    card["card_markdown"] = str(md_path)
    card["card_manifest"] = str(json_path)
    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return md_path, json_path, card


def print_card_result(md_path: Path, json_path: Path, card: dict[str, Any]) -> None:
    print(f"context_card={md_path}")
    print(f"context_manifest={json_path}")
    print(f"kind={card['kind']}")
    print(f"source_chars={card['metrics']['source_chars']}")
    print(f"card_chars={card['metrics']['card_chars']}")
    print(f"approx_char_compression={card['metrics']['approx_char_compression']}")
    summary = card.get("local_summary", "").strip().splitlines()
    if summary:
        print("summary_preview:")
        for line in summary[:8]:
            print(line[:240])


def build_model_prompt(task: str, context: str, instruction: str) -> str:
    return textwrap.dedent(
        f"""\
        Task: {task}

        Instructions:
        {instruction}

        Return a compact context card section. Use bullets. Do not invent facts.
        Include source IDs, paths, proof IDs, or commit IDs when present.
        Say "unknown" for anything not supported by the provided context.

        Context:
        {context}
        """
    )


def command_status(args: argparse.Namespace) -> int:
    targets = []
    cortex: dict[str, Any]
    ok = True
    for name in TARGETS:
        target = TARGETS[name]
        item: dict[str, Any] = {
            "name": name,
            "host": target["host"],
            "base_url": target["base_url"],
            "configured_model": target.get("model", ""),
            "ok": False,
            "models": [],
            "error": "",
        }
        try:
            data = remote_models(name)
            item["models"] = [model.get("id") for model in data.get("data", []) if model.get("id")]
            item["ok"] = True
        except (Exception, SystemExit) as exc:
            item["error"] = str(exc)
            ok = False
        targets.append(item)

    try:
        health = ssh(THINKCENTRE_HOST, "curl -fsS http://127.0.0.1:6333/healthz", timeout=20).strip()
        count = ssh(
            THINKCENTRE_HOST,
            "curl -fsS -X POST http://127.0.0.1:6333/collections/kernel_evidence/points/count "
            "-H 'Content-Type: application/json' -d '{}'",
            timeout=20,
        ).strip()
        cortex = {
            "name": "qdrant",
            "host": THINKCENTRE_HOST,
            "url": QDRANT_URL,
            "ok": True,
            "health": health,
            "count": count,
            "error": "",
        }
    except (Exception, SystemExit) as exc:
        cortex = {
            "name": "qdrant",
            "host": THINKCENTRE_HOST,
            "url": QDRANT_URL,
            "ok": False,
            "health": "",
            "count": "",
            "error": str(exc),
        }
        ok = False

    if args.json:
        print(json.dumps({"ok": ok, "targets": targets, "cortex": cortex}, indent=2, sort_keys=True))
        return 0 if ok else 1

    print("== local model targets ==")
    for item in targets:
        if item["ok"]:
            print(
                f"{item['name']}: ok host={item['host']} "
                f"base={item['base_url']} models={item['models']}"
            )
        else:
            print(
                f"{item['name']}: unavailable host={item['host']} "
                f"base={item['base_url']} error={item['error']}"
            )

    print("\n== cortex ==")
    if cortex["ok"]:
        print(f"qdrant: ok health={cortex['health']} count={cortex['count']}")
    else:
        print(f"qdrant: unavailable error={cortex['error']}")
    return 0 if ok else 1


def command_research_query(args: argparse.Namespace) -> int:
    query = args.query
    remote_cmd = (
        f"QDRANT_URL={shlex.quote(QDRANT_URL)} "
        f"EMBEDDING_API_BASE={shlex.quote(EMBEDDING_API_BASE)} "
        f"EMBEDDING_MODEL={shlex.quote(EMBEDDING_MODEL)} "
        f"python3 {shlex.quote(THINKCENTRE_CORTEX_TOOL)} search "
        f"{shlex.quote(query)} --limit {int(args.limit)}"
    )
    raw = ssh(THINKCENTRE_HOST, remote_cmd, timeout=180)
    data = json.loads(raw)
    hits = data.get("result", [])
    lines = [f"query: {query}", f"hits: {len(hits)}"]
    snippets = []
    for idx, hit in enumerate(hits, start=1):
        payload = hit.get("payload", {})
        text = (payload.get("text") or "").strip().replace("\r\n", "\n")
        snippet, _ = truncate_middle(text, args.snippet_chars)
        lines.append(
            f"{idx}. score={hit.get('score')} source={payload.get('source_uri')} "
            f"chunk={payload.get('chunk_index')} sha={payload.get('content_sha256')}"
        )
        snippets.append(f"[{idx}] {payload.get('source_uri')} chunk {payload.get('chunk_index')}\n{snippet}")
    deterministic = "\n".join(lines) + "\n\n" + "\n\n".join(snippets)
    source = {
        "source_type": "qdrant_search",
        "query": query,
        "thinkcentre_host": THINKCENTRE_HOST,
        "qdrant_url": QDRANT_URL,
        "collection": "kernel_evidence",
        "hit_count": len(hits),
        "source_chars": len(raw) + len(query),
        "raw_result_sha256": sha256_text(raw),
    }
    local_summary = ""
    model_meta = None
    if not args.no_model:
        context, _ = truncate_middle(deterministic, args.max_model_chars)
        prompt = build_model_prompt(
            "Summarize local kernel evidence search results",
            context,
            "Answer the query, list the strongest evidence, name unresolved risks, and state the next kernel workflow action.",
        )
        local_summary, model_meta = chat_local_model(args.target, prompt, max_tokens=args.max_tokens)
    md_path, json_path, card = write_card(
        kind="research-query",
        title=args.title or query,
        source=source,
        deterministic_extract=deterministic,
        local_summary=local_summary,
        model_meta=model_meta,
        out_dir=args.out_dir,
    )
    print_card_result(md_path, json_path, card)
    return 0


def command_log_triage(args: argparse.Namespace) -> int:
    if args.proof_json:
        text, source = proof_json_to_text(args.proof_json)
    else:
        text, source = read_text_source(args.file)
    signals = extract_signal_lines(text, args.signal_limit)
    excerpt, truncated = truncate_middle(text, args.max_input_chars)
    deterministic = textwrap.dedent(
        f"""\
        source: {source.get('source_path')}
        truncated_for_model: {truncated}
        signal_lines:
        {chr(10).join(signals) if signals else "(none found)"}

        excerpt:
        {excerpt}
        """
    )
    local_summary = ""
    model_meta = None
    if not args.no_model:
        prompt = build_model_prompt(
            "Triage a kernel validation/build/checkpatch log",
            deterministic,
            "Return: result, first actionable failures, likely root cause, exact next command, and what Codex should not need to read.",
        )
        local_summary, model_meta = chat_local_model(args.target, prompt, max_tokens=args.max_tokens)
    title = args.title or f"log triage {source.get('proof_id') or source.get('source_path')}"
    md_path, json_path, card = write_card(
        kind="log-triage",
        title=title,
        source=source,
        deterministic_extract="\n".join(signals) if signals else excerpt,
        local_summary=local_summary,
        model_meta=model_meta,
        out_dir=args.out_dir,
        extra={"input_truncated_for_model": truncated},
    )
    print_card_result(md_path, json_path, card)
    return 0


def git_diff_local(repo: str, *, max_diff_chars: int) -> tuple[str, dict[str, Any], str]:
    stat = run(["git", "diff", "--stat", "--"], cwd=repo, check=False).stdout.strip()
    names = run(["git", "diff", "--name-only", "--"], cwd=repo, check=False).stdout.strip()
    diff = run(["git", "diff", "--no-ext-diff", "--binary", "--"], cwd=repo, check=False, timeout=180).stdout
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"], cwd=repo, check=False).stdout.splitlines()
    untracked_diff = []
    for path in untracked[: args_untracked_limit()]:
        proc = run(["git", "diff", "--no-index", "--", "/dev/null", path], cwd=repo, check=False, timeout=60)
        untracked_diff.append(proc.stdout)
    full = diff + "\n".join(untracked_diff)
    shown, truncated = truncate_middle(full, max_diff_chars)
    meta = {
        "source_type": "git_diff",
        "repo": str(Path(repo).resolve()),
        "source_chars": len(full),
        "diff_truncated": truncated,
        "diff_sha256": sha256_text(full),
        "changed_files": [line for line in names.splitlines() if line],
        "untracked_files": untracked,
    }
    deterministic = f"diff_stat:\n{stat or '(empty)'}\n\nchanged_files:\n{names or '(none)'}\n\nuntracked_files:\n" + (
        "\n".join(untracked) if untracked else "(none)"
    ) + f"\n\ndiff_excerpt:\n{shown}"
    return deterministic, meta, full


def args_untracked_limit() -> int:
    return int(os.environ.get("KERNEL_OFFLOAD_UNTRACKED_DIFF_LIMIT", "20"))


def git_diff_remote(host: str, path: str, *, max_diff_chars: int) -> tuple[str, dict[str, Any], str]:
    script = r"""
set -e
printf -- '---STAT---\n'
git diff --stat --
printf -- '---NAMES---\n'
git diff --name-only --
printf -- '---UNTRACKED---\n'
git ls-files --others --exclude-standard
printf -- '---DIFF---\n'
git diff --no-ext-diff --binary --
git ls-files --others --exclude-standard | head -20 | while IFS= read -r path; do
  git diff --no-index -- /dev/null "$path" || true
done
"""
    raw = ssh(host, f"cd {shlex.quote(path)} && {script}", timeout=240)
    parts = re.split(r"^---([A-Z]+)---$", raw, flags=re.MULTILINE)
    buckets = {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}
    full = buckets.get("DIFF", "")
    shown, truncated = truncate_middle(full, max_diff_chars)
    names = [line for line in buckets.get("NAMES", "").splitlines() if line.strip()]
    untracked = [line for line in buckets.get("UNTRACKED", "").splitlines() if line.strip()]
    meta = {
        "source_type": "remote_git_diff",
        "host": host,
        "repo": path,
        "source_chars": len(full),
        "diff_truncated": truncated,
        "diff_sha256": sha256_text(full),
        "changed_files": names,
        "untracked_files": untracked,
    }
    deterministic = (
        f"diff_stat:\n{buckets.get('STAT', '').strip() or '(empty)'}\n\n"
        f"changed_files:\n{chr(10).join(names) if names else '(none)'}\n\n"
        f"untracked_files:\n{chr(10).join(untracked) if untracked else '(none)'}\n\n"
        f"diff_excerpt:\n{shown}"
    )
    return deterministic, meta, full


def diff_context(args: argparse.Namespace) -> tuple[str, dict[str, Any], str]:
    if args.remote_host or args.remote_path:
        if not args.remote_host or not args.remote_path:
            raise SystemExit("--remote-host and --remote-path must be used together")
        return git_diff_remote(args.remote_host, args.remote_path, max_diff_chars=args.max_diff_chars)
    return git_diff_local(args.repo, max_diff_chars=args.max_diff_chars)


def command_diff_brief(args: argparse.Namespace) -> int:
    deterministic, source, _ = diff_context(args)
    local_summary = ""
    model_meta = None
    if not args.no_model:
        context, _ = truncate_middle(deterministic, args.max_model_chars)
        prompt = build_model_prompt(
            "Brief a kernel git diff before Codex reads it",
            context,
            "Return: what changed, files touched, likely maintainer risks, validation required, and whether this looks too broad.",
        )
        local_summary, model_meta = chat_local_model(args.target, prompt, max_tokens=args.max_tokens)
    title = args.title or f"diff brief {source.get('repo')}"
    md_path, json_path, card = write_card(
        kind="diff-brief",
        title=title,
        source=source,
        deterministic_extract=deterministic,
        local_summary=local_summary,
        model_meta=model_meta,
        out_dir=args.out_dir,
    )
    print_card_result(md_path, json_path, card)
    return 0


def command_review_local(args: argparse.Namespace) -> int:
    if args.file:
        text, source = read_text_source(args.file)
        deterministic, truncated = truncate_middle(text, args.max_diff_chars)
        source["input_truncated"] = truncated
    else:
        deterministic, source, _ = diff_context(args)
    context, _ = truncate_middle(deterministic, args.max_model_chars)
    prompt = build_model_prompt(
        "Local maintainer-risk review",
        context,
        args.prompt
        or "Find three reasons a Linux kernel maintainer would reject this code. Tie each reason to evidence in the provided diff or payload.",
    )
    local_summary, model_meta = chat_local_model(args.target, prompt, max_tokens=args.max_tokens)
    title = args.title or f"local review {source.get('repo') or source.get('source_path')}"
    md_path, json_path, card = write_card(
        kind="local-review",
        title=title,
        source=source,
        deterministic_extract=deterministic,
        local_summary=local_summary,
        model_meta=model_meta,
        out_dir=args.out_dir,
    )
    print_card_result(md_path, json_path, card)
    print("halted_for_human_gate=1")
    return 0


def command_review_matrix(args: argparse.Namespace) -> int:
    md_path, json_path, card = create_review_matrix_card(args)
    print_card_result(md_path, json_path, card)
    print("halted_for_human_gate=1")
    return 0


def create_review_matrix_card(args: argparse.Namespace) -> tuple[Path, Path, dict[str, Any]]:
    if args.file:
        text, source = read_text_source(args.file)
        deterministic, truncated = truncate_middle(text, args.max_diff_chars)
        source["input_truncated"] = truncated
    else:
        deterministic, source, _ = diff_context(args)

    context, _ = truncate_middle(deterministic, args.max_model_chars)
    target_names = []
    for value in args.targets:
        target_names.extend([item.strip() for item in value.split(",") if item.strip()])
    target_names = list(dict.fromkeys(target_names))
    if not target_names:
        target_names = list(DEFAULT_REVIEW_TARGETS)

    lane_prompts = {
        "amd-fast": (
            "Fast 3090 triage: identify obvious correctness bugs, build/checkpatch "
            "risks, and the first concrete command Codex should run next."
        ),
        "amd-research": (
            "7900XT research review: identify overlap with prior kernel work, "
            "process risks, missing evidence, and what should be searched next."
        ),
        "strix-review": (
            "Strix maintainer review: find three reasons a Linux kernel maintainer "
            "would reject this code or plan, grounded only in the provided context."
        ),
    }

    def run_lane(target_name: str) -> tuple[str, dict[str, Any]]:
        prompt = build_model_prompt(
            f"Multi-lane local review via {target_name}",
            context,
            lane_prompts.get(target_name, args.prompt)
            or "Review this kernel artifact and return compact, evidence-grounded risks.",
        )
        summary, meta = chat_local_model(target_name, prompt, max_tokens=args.max_tokens)
        return summary, meta

    lane_results: dict[str, Any] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(target_names), 3)) as pool:
        future_map = {pool.submit(run_lane, target): target for target in target_names}
        for future in concurrent.futures.as_completed(future_map):
            target = future_map[future]
            try:
                summary, meta = future.result()
                lane_results[target] = {"summary": summary, "meta": meta, "ok": True}
            except BaseException as exc:
                if isinstance(exc, KeyboardInterrupt):
                    raise
                if not args.allow_unavailable:
                    raise
                lane_results[target] = {"summary": "", "meta": {"target": target}, "ok": False, "error": str(exc)}

    ordered_sections = []
    for target in target_names:
        result = lane_results.get(target, {})
        if result.get("ok"):
            ordered_sections.append(f"## {target}\n\n{result.get('summary', '').strip()}")
        else:
            ordered_sections.append(f"## {target}\n\nunavailable: {result.get('error', 'unknown error')}")
    local_summary = "\n\n".join(ordered_sections).strip()
    model_meta = {
        "matrix_targets": target_names,
        "lanes": {target: lane_results[target].get("meta", {}) for target in target_names if target in lane_results},
        "errors": {target: lane_results[target].get("error") for target in target_names if lane_results.get(target, {}).get("error")},
    }
    title = args.title or f"multi lane review {source.get('repo') or source.get('source_path')}"
    return write_card(
        kind="review-matrix",
        title=title,
        source=source,
        deterministic_extract=deterministic,
        local_summary=local_summary,
        model_meta=model_meta,
        out_dir=args.out_dir,
    )


def existing_matrix_source_hashes(out_dir: str) -> set[str]:
    hashes: set[str] = set()
    root = Path(out_dir)
    if not root.exists():
        return hashes
    for path in root.glob("review-matrix-*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        source_sha = data.get("source", {}).get("source_sha256")
        if source_sha:
            hashes.add(source_sha)
    return hashes


def iter_review_matrix_cards(out_dir: str) -> list[Path]:
    root = Path(out_dir)
    if not root.exists():
        return []
    return sorted(root.glob("review-matrix-*.json"))


def latest_matrix_file_records(out_dir: str) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    latest: dict[str, dict[str, Any]] = {}
    stats = {
        "matrix_cards": 0,
        "file_cards": 0,
        "skipped": 0,
    }
    for card_path in iter_review_matrix_cards(out_dir):
        stats["matrix_cards"] += 1
        key, record, reason = matrix_card_to_ledger_record(card_path)
        if not key or record is None:
            stats["skipped"] += 1
            continue
        stats["file_cards"] += 1
        marker = (record.get("reviewed_at") or "", str(card_path))
        existing = latest.get(key)
        if not existing or marker > existing["marker"]:
            latest[key] = {"record": record, "marker": marker}
    return latest, stats


def load_ledger(path: str) -> dict[str, Any]:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return {"schema_version": 1, "updated_at": "", "artifacts": {}}
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "updated_at": "", "artifacts": {}}
    data.setdefault("schema_version", 1)
    data.setdefault("artifacts", {})
    return data


def save_ledger(path: str, ledger: dict[str, Any]) -> None:
    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger["updated_at"] = utc_now()
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def matrix_card_to_ledger_record(path: Path) -> tuple[str | None, dict[str, Any] | None, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, None, f"unreadable:{exc}"

    if data.get("kind") != "review-matrix":
        return None, None, "not-review-matrix"

    source = data.get("source", {})
    source_path = source.get("source_path")
    source_sha = source.get("source_sha256")
    if source_path == "-":
        return None, None, "non-file-source"
    if not source_path or not source_sha:
        return None, None, "non-file-source"

    model = data.get("model", {})
    errors = model.get("errors", {}) or {}
    record = {
        "status": "failed" if errors else "reviewed",
        "source_sha256": source_sha,
        "source_chars": source.get("source_chars", 0),
        "reviewed_at": data.get("created_at") or "",
        "card_markdown": data.get("card_markdown") or "",
        "card_manifest": data.get("card_manifest") or str(path),
        "lanes": model.get("lanes", {}),
        "errors": errors,
        "backfilled_from": str(path),
    }
    return source_path, record, "ok"


def backfill_idle_ledger(ledger_path: str, out_dir: str) -> dict[str, int]:
    ledger = load_ledger(ledger_path)
    artifacts = ledger.setdefault("artifacts", {})
    stats = {
        "matrix_cards": 0,
        "file_cards": 0,
        "added": 0,
        "updated": 0,
        "unchanged": 0,
        "skipped": 0,
    }
    now = utc_now()
    latest, scan_stats = latest_matrix_file_records(out_dir)
    stats["matrix_cards"] = scan_stats["matrix_cards"]
    stats["file_cards"] = scan_stats["file_cards"]
    stats["skipped"] = scan_stats["skipped"]
    for key, item in latest.items():
        record = item["record"]
        existing = artifacts.get(key, {})
        preserve_fields = ("consumed_by_codex_at", "consumed_note", "started_at")
        preserved = {}
        if existing.get("source_sha256") == record.get("source_sha256"):
            preserved = {field: existing[field] for field in preserve_fields if existing.get(field)}
        merged = dict(existing)
        merged.update(record)
        merged.update(preserved)
        merged["backfilled_at"] = existing.get("backfilled_at") or now

        if not existing:
            stats["added"] += 1
        elif merged != existing:
            stats["updated"] += 1
        else:
            stats["unchanged"] += 1
        artifacts[key] = merged

    if stats["added"] or stats["updated"]:
        save_ledger(ledger_path, ledger)
    return stats


def ledger_status(ledger_path: str, out_dir: str, roots: list[str]) -> dict[str, Any]:
    ledger = load_ledger(ledger_path)
    artifacts = ledger.get("artifacts", {})
    by_status: dict[str, int] = {}
    consumed = 0
    consumed_reviewed = 0
    for record in artifacts.values():
        status = record.get("status") or "unknown"
        by_status[status] = by_status.get(status, 0) + 1
        if record.get("consumed_by_codex_at"):
            consumed += 1
            if status == "reviewed":
                consumed_reviewed += 1

    backfillable = 0
    matrix_cards = 0
    matrix_file_cards = 0
    skipped_non_file = 0
    latest, scan_stats = latest_matrix_file_records(out_dir)
    matrix_cards = scan_stats["matrix_cards"]
    matrix_file_cards = scan_stats["file_cards"]
    skipped_non_file = scan_stats["skipped"]
    for key, item in latest.items():
        record = item["record"]
        existing = artifacts.get(key, {})
        if existing.get("source_sha256") != record.get("source_sha256") or not existing.get("card_manifest"):
            backfillable += 1

    candidates = candidate_idle_items(roots, out_dir, ledger_path)
    reviewed = by_status.get("reviewed", 0)
    return {
        "ledger": str(Path(ledger_path)),
        "updated_at": ledger.get("updated_at", ""),
        "records": len(artifacts),
        "by_status": by_status,
        "consumed": consumed,
        "unconsumed_reviewed": max(reviewed - consumed_reviewed, 0),
        "matrix_cards": matrix_cards,
        "matrix_file_cards": matrix_file_cards,
        "skipped_non_file": skipped_non_file,
        "backfillable_missing_or_stale": backfillable,
        "idle_review_candidates": len(candidates),
        "next_candidate": candidates[0] if candidates else None,
    }


def print_ledger_status(status: dict[str, Any]) -> None:
    by_status = status.get("by_status", {})
    print(f"ledger={status['ledger']}")
    print(f"updated_at={status.get('updated_at') or '(never)'}")
    print(f"records={status['records']}")
    print(
        "statuses="
        + ",".join(f"{name}:{count}" for name, count in sorted(by_status.items()))
        if by_status
        else "statuses=(none)"
    )
    print(f"consumed={status['consumed']}")
    print(f"unconsumed_reviewed={status['unconsumed_reviewed']}")
    print(f"matrix_cards={status['matrix_cards']}")
    print(f"matrix_file_cards={status['matrix_file_cards']}")
    print(f"skipped_non_file={status['skipped_non_file']}")
    print(f"backfillable_missing_or_stale={status['backfillable_missing_or_stale']}")
    print(f"idle_review_candidates={status['idle_review_candidates']}")
    if status.get("next_candidate"):
        item = status["next_candidate"]
        print(f"next_candidate={item['path']} reason={item['reason']} chars={item['source_chars']}")


def unconsumed_reviewed_records(ledger: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    records: list[tuple[str, dict[str, Any]]] = []
    for key, record in ledger.get("artifacts", {}).items():
        if record.get("status") != "reviewed":
            continue
        if record.get("consumed_by_codex_at"):
            continue
        records.append((key, record))
    records.sort(key=lambda item: (item[1].get("reviewed_at") or "", item[0]))
    return records


def find_ledger_artifact_key(ledger: dict[str, Any], value: str) -> str | None:
    artifacts = ledger.get("artifacts", {})
    checks = [value]
    path = Path(value)
    if path.exists():
        checks.append(str(path.resolve()))

    if path.suffix == ".json" and path.exists():
        key, _, _ = matrix_card_to_ledger_record(path)
        if key:
            checks.append(key)

    for key, record in artifacts.items():
        if key in checks:
            return key
        if record.get("card_markdown") in checks or record.get("card_manifest") in checks:
            return key
    return None


def command_idle_ledger(args: argparse.Namespace) -> int:
    roots = args.root or DEFAULT_IDLE_ROOTS
    if args.action == "backfill":
        stats = backfill_idle_ledger(args.ledger, args.out_dir)
        for key in ("matrix_cards", "file_cards", "added", "updated", "unchanged", "skipped"):
            print(f"{key}={stats[key]}")
        print_ledger_status(ledger_status(args.ledger, args.out_dir, roots))
        return 0

    if args.action == "status":
        print_ledger_status(ledger_status(args.ledger, args.out_dir, roots))
        return 0

    if args.action == "next-unconsumed":
        ledger = load_ledger(args.ledger)
        records = unconsumed_reviewed_records(ledger)
        print(f"unconsumed_reviewed={len(records)}")
        if records:
            key, record = records[0]
            print(f"artifact={key}")
            print(f"source_sha256={record.get('source_sha256', '')}")
            print(f"reviewed_at={record.get('reviewed_at', '')}")
            print(f"card_markdown={record.get('card_markdown', '')}")
            print(f"card_manifest={record.get('card_manifest', '')}")
        return 0

    if args.action == "mark-consumed":
        if not args.artifact:
            raise SystemExit("mark-consumed requires an artifact path, card markdown path, or card manifest path")
        ledger = load_ledger(args.ledger)
        key = find_ledger_artifact_key(ledger, args.artifact)
        if not key:
            raise SystemExit(f"artifact not found in ledger: {args.artifact}")
        record = ledger.setdefault("artifacts", {}).setdefault(key, {})
        record["consumed_by_codex_at"] = utc_now()
        if args.note:
            record["consumed_note"] = args.note
        save_ledger(args.ledger, ledger)
        print(f"consumed_artifact={key}")
        print(f"card_markdown={record.get('card_markdown', '')}")
        return 0

    raise SystemExit(f"unknown idle-ledger action: {args.action}")


def artifact_identity(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    stat = path.stat()
    return {
        "path": str(path),
        "source_sha256": sha256_text(text),
        "source_chars": len(text),
        "mtime": stat.st_mtime,
        "mtime_utc": dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def candidate_idle_items(roots: list[str], out_dir: str, ledger_path: str) -> list[dict[str, Any]]:
    reviewed_hashes = existing_matrix_source_hashes(out_dir)
    ledger = load_ledger(ledger_path)
    records = ledger.get("artifacts", {})
    candidates: list[dict[str, Any]] = []
    for root_value in roots:
        root = Path(root_value)
        if not root.is_absolute():
            root = REPO_ROOT / root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
            if ".raw." in path.name or path.name.endswith(".raw.md"):
                continue
            try:
                identity = artifact_identity(path)
            except Exception:
                continue
            record = records.get(str(path), {})
            reviewed_by_card = identity["source_sha256"] in reviewed_hashes
            reviewed_by_ledger = (
                record.get("source_sha256") == identity["source_sha256"]
                and record.get("status") == "reviewed"
            )
            if reviewed_by_card or reviewed_by_ledger:
                continue
            identity["reason"] = "new" if not record else "changed-or-incomplete"
            candidates.append(identity)
    return candidates


def command_idle_sweep(args: argparse.Namespace) -> int:
    roots = args.root or DEFAULT_IDLE_ROOTS
    max_runs = args.max_runs if args.max_runs is not None else args.limit
    if args.next:
        max_runs = 1

    completed = 0
    while True:
        candidates = candidate_idle_items(roots, args.out_dir, args.ledger)
        selected = candidates[: (1 if args.next else args.limit)]
        if not selected:
            print("idle_review_candidates=0")
            break

        print(f"idle_review_candidates={len(candidates)}")
        for item in selected:
            print(f"candidate={item['path']} reason={item['reason']} chars={item['source_chars']}")

        if not args.run:
            print("dry_run=1")
            print("rerun with --run to create review-matrix cards")
            break

        for item in selected:
            path = Path(item["path"])
            ledger = load_ledger(args.ledger)
            ledger.setdefault("artifacts", {}).setdefault(str(path), {})
            ledger["artifacts"][str(path)].update(
                {
                    "status": "in_progress",
                    "source_sha256": item["source_sha256"],
                    "source_chars": item["source_chars"],
                    "started_at": utc_now(),
                }
            )
            save_ledger(args.ledger, ledger)

            ok = False
            error = ""
            md_path = None
            json_path = None
            card: dict[str, Any] | None = None
            try:
                matrix_args = argparse.Namespace(
                    file=str(path),
                    repo=os.getcwd(),
                    remote_host="",
                    remote_path="",
                    max_diff_chars=args.max_diff_chars,
                    title=f"idle review {path.name}",
                    targets=args.targets,
                    prompt="",
                    max_tokens=args.max_tokens,
                    max_model_chars=args.max_model_chars,
                    out_dir=args.out_dir,
                    allow_unavailable=args.allow_unavailable,
                )
                md_path, json_path, card = create_review_matrix_card(matrix_args)
                print_card_result(md_path, json_path, card)
                print("halted_for_human_gate=1")
                ok = not bool(card.get("model", {}).get("errors"))
            except Exception as exc:
                if not args.allow_unavailable:
                    raise
                error = str(exc)

            ledger = load_ledger(args.ledger)
            record = ledger.setdefault("artifacts", {}).setdefault(str(path), {})
            record.update(
                {
                    "status": "reviewed" if ok else "failed",
                    "source_sha256": item["source_sha256"],
                    "source_chars": item["source_chars"],
                    "reviewed_at": utc_now(),
                    "card_markdown": str(md_path) if md_path else "",
                    "card_manifest": str(json_path) if json_path else "",
                    "lanes": (card or {}).get("model", {}).get("lanes", {}),
                    "errors": (card or {}).get("model", {}).get("errors", {}) or ({"exception": error} if error else {}),
                }
            )
            save_ledger(args.ledger, ledger)
            completed += 1

            if completed >= max_runs:
                print(f"idle_review_completed={completed}")
                return 0

        if not args.loop:
            break

    print(f"idle_review_completed={completed}")
    return 0


def add_common_model_args(parser: argparse.ArgumentParser, default_target: str) -> None:
    parser.add_argument("--target", choices=sorted(TARGETS), default=default_target)
    parser.add_argument("--max-tokens", type=int, default=800)
    parser.add_argument("--max-model-chars", type=int, default=14000)
    parser.add_argument("--out-dir", default=str(DEFAULT_CARD_DIR))
    parser.add_argument("--no-model", action="store_true")


def add_diff_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=os.getcwd())
    parser.add_argument("--remote-host", default="")
    parser.add_argument("--remote-path", default="")
    parser.add_argument("--max-diff-chars", type=int, default=30000)
    parser.add_argument("--title", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local token-offload tools for kernel work.")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=command_status)

    research = sub.add_parser("research-query")
    research.add_argument("query")
    research.add_argument("--title", default="")
    research.add_argument("--limit", type=int, default=5)
    research.add_argument("--snippet-chars", type=int, default=1000)
    add_common_model_args(research, "amd-research")
    research.set_defaults(func=command_research_query)

    log = sub.add_parser("log-triage")
    src = log.add_mutually_exclusive_group(required=True)
    src.add_argument("--file")
    src.add_argument("--proof-json")
    log.add_argument("--title", default="")
    log.add_argument("--max-input-chars", type=int, default=14000)
    log.add_argument("--signal-limit", type=int, default=80)
    add_common_model_args(log, "amd-research")
    log.set_defaults(func=command_log_triage)

    diff = sub.add_parser("diff-brief")
    add_diff_args(diff)
    add_common_model_args(diff, "amd-research")
    diff.set_defaults(func=command_diff_brief)

    review = sub.add_parser("review-local")
    add_diff_args(review)
    review.add_argument("--file", default="")
    review.add_argument("--prompt", default="")
    add_common_model_args(review, "strix-review")
    review.set_defaults(func=command_review_local)

    matrix = sub.add_parser("review-matrix")
    add_diff_args(matrix)
    matrix.add_argument("--file", default="")
    matrix.add_argument(
        "--targets",
        action="append",
        default=[],
        help="Comma-separated or repeated target names. Default uses 3090, 7900XT, and Strix.",
    )
    matrix.add_argument("--prompt", default="")
    matrix.add_argument("--max-tokens", type=int, default=700)
    matrix.add_argument("--max-model-chars", type=int, default=14000)
    matrix.add_argument("--out-dir", default=str(DEFAULT_CARD_DIR))
    matrix.add_argument("--allow-unavailable", action="store_true")
    matrix.set_defaults(func=command_review_matrix)

    idle = sub.add_parser("idle-sweep")
    idle.add_argument("--root", action="append", default=[])
    idle.add_argument("--limit", type=int, default=3)
    idle.add_argument("--next", action="store_true", help="Select only the next due artifact.")
    idle.add_argument("--loop", action="store_true", help="Continue selecting due artifacts until max runs or queue empty.")
    idle.add_argument("--max-runs", type=int, default=None, help="Maximum artifacts to review during this invocation.")
    idle.add_argument("--run", action="store_true")
    idle.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    idle.add_argument(
        "--targets",
        action="append",
        default=[],
        help="Comma-separated or repeated target names.",
    )
    idle.add_argument("--max-tokens", type=int, default=600)
    idle.add_argument("--max-model-chars", type=int, default=14000)
    idle.add_argument("--max-diff-chars", type=int, default=30000)
    idle.add_argument("--out-dir", default=str(DEFAULT_CARD_DIR))
    idle.add_argument("--allow-unavailable", action="store_true")
    idle.set_defaults(func=command_idle_sweep)

    ledger = sub.add_parser("idle-ledger")
    ledger.add_argument("action", choices=["status", "backfill", "next-unconsumed", "mark-consumed"])
    ledger.add_argument("artifact", nargs="?", help="Artifact path, card Markdown path, or card manifest path for mark-consumed.")
    ledger.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ledger.add_argument("--out-dir", default=str(DEFAULT_CARD_DIR))
    ledger.add_argument("--root", action="append", default=[])
    ledger.add_argument("--note", default="")
    ledger.set_defaults(func=command_idle_ledger)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
