#!/usr/bin/env python3
"""Benchmark an OpenAI-compatible Strix runtime endpoint.

This script is intentionally dependency-free so it can be streamed over SSH and
run directly on Strix. It measures API behavior that matters for Codex/agent
use, not just raw token speed.
"""

import argparse
import hashlib
import json
import os
import platform
import re
import socket
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request


def now_ms():
    return int(time.time() * 1000)


def emit(record):
    print(json.dumps(record, sort_keys=True), flush=True)


def run_text(command, timeout=10):
    try:
        proc = subprocess.run(
            command,
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


def collect_environment():
    return {
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "env": {
            key: os.environ.get(key)
            for key in (
                "GGML_VK_VISIBLE_DEVICES",
                "VK_ICD_FILENAMES",
                "CUDA_VISIBLE_DEVICES",
                "HIP_VISIBLE_DEVICES",
                "ROCR_VISIBLE_DEVICES",
                "OMP_NUM_THREADS",
            )
            if os.environ.get(key) is not None
        },
        "commands": {
            "uname": run_text(["uname", "-a"]),
            "mem": run_text(["bash", "-lc", "free -h | sed -n '1,2p'"]),
            "render_devices": run_text(["bash", "-lc", "ls -l /dev/dri 2>/dev/null || true"]),
            "gpu_devices": run_text(
                ["bash", "-lc", "ls -1 /dev/dri/renderD* /dev/kfd /dev/nvidia* 2>/dev/null || true"]
            ),
            "vulkan": run_text(["bash", "-lc", "vulkaninfo --summary 2>/dev/null | sed -n '1,80p'"]),
            "docker": run_text(["bash", "-lc", "docker --version 2>/dev/null || true"]),
        },
    }


class OpenAIEndpoint:
    def __init__(self, base_url, timeout):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request_json(self, path, payload=None, timeout=None):
        url = f"{self.base_url}{path}"
        if payload is None:
            req = urllib.request.Request(url, method="GET")
        else:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        with urllib.request.urlopen(req, timeout=timeout or self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def chat(self, payload, timeout=None):
        start = time.perf_counter()
        data = self.request_json("/chat/completions", payload, timeout=timeout)
        elapsed = time.perf_counter() - start
        return data, elapsed

    def stream_chat(self, payload, timeout=None):
        url = f"{self.base_url}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        start = time.perf_counter()
        first_content = None
        chunks = 0
        content_parts = []

        with urllib.request.urlopen(req, timeout=timeout or self.timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                body = line[5:].strip()
                if body == "[DONE]":
                    break
                if not body:
                    continue
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    continue
                choices = data.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                text = delta.get("content") or ""
                if text:
                    chunks += 1
                    content_parts.append(text)
                    if first_content is None:
                        first_content = time.perf_counter()

        end = time.perf_counter()
        content = "".join(content_parts)
        return {
            "elapsed_sec": end - start,
            "ttft_sec": (first_content - start) if first_content is not None else None,
            "content_chars": len(content),
            "content_chunks": chunks,
            "chars_per_sec": len(content) / (end - start) if end > start else None,
            "content_preview": content[:160].replace("\n", " "),
        }


def message_content(data):
    try:
        content = data["choices"][0]["message"].get("content")
    except Exception:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)
    return ""


def usage_metrics(data, elapsed):
    usage = data.get("usage") or {}
    completion_tokens = usage.get("completion_tokens") or 0
    prompt_tokens = usage.get("prompt_tokens") or 0
    total_tokens = usage.get("total_tokens") or 0
    return {
        "elapsed_sec": elapsed,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "completion_tokens_per_sec": completion_tokens / elapsed if elapsed and completion_tokens else None,
    }


def parse_json_object(text):
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found")
    return json.loads(stripped[start : end + 1])


def base_payload(model, prompt, max_tokens, stream=False):
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": stream,
    }


def record_case(target, case, passed, metrics=None, error=None, extra=None):
    record = {
        "type": "case",
        "timestamp_ms": now_ms(),
        "target": target,
        "case": case,
        "passed": passed,
    }
    if metrics:
        record["metrics"] = metrics
    if error:
        record["error"] = error
    if extra:
        record.update(extra)
    emit(record)
    return record


def run_health(endpoint, target, explicit_model):
    try:
        data = endpoint.request_json("/models", timeout=10)
        models = [item.get("id") for item in data.get("data", []) if item.get("id")]
        selected = explicit_model or (models[0] if models else None)
        passed = bool(selected)
        return record_case(target, "health_models", passed, extra={"models": models, "selected_model": selected}), selected
    except Exception as exc:
        return record_case(target, "health_models", False, error=str(exc)), explicit_model


def run_short_chat(endpoint, target, model, max_tokens):
    prompt = (
        "In one sentence, explain why a Linux kernel patch benchmark should "
        "measure correctness gates as well as token speed."
    )
    try:
        data, elapsed = endpoint.chat(base_payload(model, prompt, max_tokens), timeout=120)
        content = message_content(data)
        metrics = usage_metrics(data, elapsed)
        passed = bool(content.strip())
        return record_case(
            target,
            "short_chat",
            passed,
            metrics=metrics,
            extra={"content_preview": content[:160].replace("\n", " ")},
        )
    except Exception as exc:
        return record_case(target, "short_chat", False, error=str(exc))


def run_stream_chat(endpoint, target, model, max_tokens):
    prompt = "Write three short bullet points about deterministic local model routing."
    try:
        payload = base_payload(model, prompt, max_tokens, stream=True)
        metrics = endpoint.stream_chat(payload, timeout=120)
        return record_case(target, "stream_chat", bool(metrics["content_chars"]), metrics=metrics)
    except Exception as exc:
        return record_case(target, "stream_chat", False, error=str(exc))


def run_json_instruction(endpoint, target, model, max_tokens):
    prompt = (
        "Return exactly one JSON object and no prose. "
        "It must be {\"runtime_ready\": true, \"risk\": \"measured\"}."
    )
    try:
        data, elapsed = endpoint.chat(base_payload(model, prompt, max_tokens), timeout=120)
        content = message_content(data)
        parsed = parse_json_object(content)
        passed = parsed.get("runtime_ready") is True and parsed.get("risk") == "measured"
        return record_case(
            target,
            "json_instruction",
            passed,
            metrics=usage_metrics(data, elapsed),
            extra={"parsed": parsed, "content_preview": content[:160].replace("\n", " ")},
        )
    except Exception as exc:
        return record_case(target, "json_instruction", False, error=str(exc))


def run_tool_call(endpoint, target, model, max_tokens):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Call record_runtime_observation exactly once with "
                    "target=\"%s\", verdict=\"ok\", reason=\"tool call smoke\". "
                    "Do not answer in prose."
                )
                % target,
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "record_runtime_observation",
                    "description": "Record one runtime benchmark observation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string"},
                            "verdict": {"type": "string", "enum": ["ok", "fail"]},
                            "reason": {"type": "string"},
                        },
                        "required": ["target", "verdict", "reason"],
                    },
                },
            }
        ],
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    try:
        data, elapsed = endpoint.chat(payload, timeout=120)
        message = data["choices"][0]["message"]
        tool_calls = message.get("tool_calls") or []
        parsed_args = []
        for call in tool_calls:
            function = call.get("function") or {}
            try:
                parsed_args.append(json.loads(function.get("arguments") or "{}"))
            except json.JSONDecodeError:
                parsed_args.append({"_invalid_json": function.get("arguments")})
        passed = bool(tool_calls) and any(
            args.get("target") == target and args.get("verdict") == "ok" for args in parsed_args
        )
        return record_case(
            target,
            "tool_call",
            passed,
            metrics=usage_metrics(data, elapsed),
            extra={
                "tool_call_count": len(tool_calls),
                "tool_names": [(call.get("function") or {}).get("name") for call in tool_calls],
                "tool_arguments": parsed_args,
                "content_preview": (message.get("content") or "")[:160].replace("\n", " "),
            },
        )
    except Exception as exc:
        return record_case(target, "tool_call", False, error=str(exc))


def run_long_context(endpoint, target, model, max_tokens, long_chars):
    marker = "STRIX_RUNTIME_BENCH_MARKER_20260605"
    seed = (
        "Linux kernel review requires exact evidence, narrow claims, proof logs, "
        "and human sign-off. "
    )
    repeat_count = (long_chars // len(seed)) + 1
    blob = (seed * repeat_count)[:long_chars]
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
    prompt = (
        f"Read the following context. The marker is {marker}. "
        f"The context digest prefix is {digest}. Reply with exactly the marker "
        "and the digest prefix, separated by one space.\n\n"
        f"{blob}"
    )
    try:
        data, elapsed = endpoint.chat(base_payload(model, prompt, max_tokens), timeout=300)
        content = message_content(data)
        passed = marker in content and digest in content
        return record_case(
            target,
            "long_context",
            passed,
            metrics=usage_metrics(data, elapsed),
            extra={
                "long_chars": long_chars,
                "digest_prefix": digest,
                "content_preview": content[:160].replace("\n", " "),
            },
        )
    except Exception as exc:
        return record_case(
            target,
            "long_context",
            False,
            error=str(exc),
            extra={"long_chars": long_chars},
        )


def summarize(target, records):
    cases = [record for record in records if record.get("type") == "case"]
    passed = [record for record in cases if record.get("passed")]
    short_tps = [
        record.get("metrics", {}).get("completion_tokens_per_sec")
        for record in cases
        if record.get("case") == "short_chat"
    ]
    ttft = [
        record.get("metrics", {}).get("ttft_sec")
        for record in cases
        if record.get("case") == "stream_chat"
    ]
    short_tps = [value for value in short_tps if value is not None]
    ttft = [value for value in ttft if value is not None]

    tool_passed = any(record.get("case") == "tool_call" and record.get("passed") for record in cases)
    chat_passed = any(record.get("case") == "short_chat" and record.get("passed") for record in cases)
    json_passed = any(record.get("case") == "json_instruction" and record.get("passed") for record in cases)
    long_passed = any(record.get("case") == "long_context" and record.get("passed") for record in cases)

    if not chat_passed:
        agent_grade = "blocked_no_chat"
    elif not tool_passed:
        agent_grade = "review_only_no_tool_calls"
    elif not json_passed:
        agent_grade = "agent_candidate_json_weak"
    elif not long_passed:
        agent_grade = "agent_candidate_long_context_weak"
    else:
        agent_grade = "agent_candidate"

    summary = {
        "type": "summary",
        "timestamp_ms": now_ms(),
        "target": target,
        "case_count": len(cases),
        "passed_count": len(passed),
        "failed_cases": [record.get("case") for record in cases if not record.get("passed")],
        "agent_grade": agent_grade,
        "short_completion_tps": statistics.mean(short_tps) if short_tps else None,
        "stream_ttft_sec": statistics.mean(ttft) if ttft else None,
    }
    emit(summary)
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Fair runtime benchmark for Strix OpenAI-compatible model servers."
    )
    parser.add_argument("--base-url", required=True, help="Example: http://127.0.0.1:8082/v1")
    parser.add_argument("--model", default=None, help="Model id. Defaults to first /models entry.")
    parser.add_argument("--target-name", default="strix-runtime", help="Human-readable runtime label.")
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--long-chars", type=int, default=65536)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--warmup", action="store_true", help="Run one unrecorded warmup request.")
    parser.add_argument(
        "--cases",
        default="health,short,stream,json,tool,long",
        help="Comma-separated cases: health,short,stream,json,tool,long.",
    )
    args = parser.parse_args()

    endpoint = OpenAIEndpoint(args.base_url, args.timeout)
    target = args.target_name
    selected_cases = {item.strip() for item in args.cases.split(",") if item.strip()}

    emit({
        "type": "run_start",
        "timestamp_ms": now_ms(),
        "target": target,
        "base_url": args.base_url,
        "requested_model": args.model,
        "max_tokens": args.max_tokens,
        "long_chars": args.long_chars,
        "cases": sorted(selected_cases),
        "environment": collect_environment(),
    })

    records = []
    health_record, model = run_health(endpoint, target, args.model)
    records.append(health_record)
    if "health" not in selected_cases:
        records = []

    if not model:
        summarize(target, records)
        return 2

    if args.warmup:
        try:
            endpoint.chat(base_payload(model, "Reply with: warmup", 8), timeout=60)
        except Exception:
            pass

    case_runners = [
        ("short", lambda: run_short_chat(endpoint, target, model, args.max_tokens)),
        ("stream", lambda: run_stream_chat(endpoint, target, model, args.max_tokens)),
        ("json", lambda: run_json_instruction(endpoint, target, model, args.max_tokens)),
        ("tool", lambda: run_tool_call(endpoint, target, model, args.max_tokens)),
        ("long", lambda: run_long_context(endpoint, target, model, args.max_tokens, args.long_chars)),
    ]

    for name, runner in case_runners:
        if name not in selected_cases:
            continue
        records.append(runner())

    summary = summarize(target, records)
    return 0 if summary["failed_cases"] == [] else 1


if __name__ == "__main__":
    raise SystemExit(main())
