#!/usr/bin/env python3
import argparse
import json
import statistics
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

def http_json(url, payload=None, timeout=300):
    if payload is None:
        req = urllib.request.Request(url, method="GET")
    else:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def get_model(base_url):
    data = http_json(f"{base_url.rstrip('/')}/models", timeout=10)
    return data["data"][0]["id"]

def one_request(base_url, model, prompt, max_tokens):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": False,
    }

    start = time.perf_counter()
    data = http_json(f"{base_url.rstrip('/')}/chat/completions", payload=payload)
    end = time.perf_counter()

    elapsed = end - start
    usage = data.get("usage") or {}
    completion_tokens = usage.get("completion_tokens") or 0
    total_tokens = usage.get("total_tokens") or 0
    content = data["choices"][0]["message"]["content"]

    return {
        "elapsed_sec": elapsed,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "tokens_per_sec_completion": completion_tokens / elapsed if elapsed else None,
        "content_preview": content[:120].replace("\n", " "),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True, help="Example: http://127.0.0.1:8010/v1")
    ap.add_argument("--model", default=None)
    ap.add_argument("--requests", type=int, default=5)
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--max-tokens", type=int, default=128)
    ap.add_argument(
        "--prompt",
        default="Write a concise explanation of why local LLM benchmarking should control for model size, context length, and concurrency.",
    )
    args = ap.parse_args()

    base_url = args.base_url.rstrip("/")
    model = args.model or get_model(base_url)

    print(f"base_url={base_url}")
    print(f"model={model}")
    print(f"requests={args.requests}")
    print(f"concurrency={args.concurrency}")
    print(f"max_tokens={args.max_tokens}")

    results = []
    bench_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = [
            ex.submit(one_request, base_url, model, args.prompt, args.max_tokens)
            for _ in range(args.requests)
        ]
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            print(json.dumps(r, indent=2))

    bench_end = time.perf_counter()
    elapsed = bench_end - bench_start

    latencies = [r["elapsed_sec"] for r in results]
    completion_tps = [
        r["tokens_per_sec_completion"]
        for r in results
        if r["tokens_per_sec_completion"] is not None
    ]
    total_completion_tokens = sum(r["completion_tokens"] for r in results)

    summary = {
        "base_url": base_url,
        "model": model,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "max_tokens": args.max_tokens,
        "wall_time_sec": elapsed,
        "latency_avg_sec": statistics.mean(latencies),
        "latency_median_sec": statistics.median(latencies),
        "latency_min_sec": min(latencies),
        "latency_max_sec": max(latencies),
        "per_request_completion_tps_avg": statistics.mean(completion_tps) if completion_tps else None,
        "aggregate_completion_tps": total_completion_tokens / elapsed if elapsed > 0 else None,
        "total_completion_tokens": total_completion_tokens,
    }

    print("\n== SUMMARY ==")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
