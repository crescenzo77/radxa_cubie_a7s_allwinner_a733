#!/usr/bin/env python3
"""Minimal Qdrant/OpenAI-compatible embedding helper for kernel evidence."""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid


TEXT_SUFFIXES = {
    ".c",
    ".dts",
    ".dtsi",
    ".h",
    ".log",
    ".md",
    ".patch",
    ".rst",
    ".txt",
    ".yaml",
    ".yml",
}


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_request(method, url, payload=None, timeout=120):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {body}") from exc


def chunk_text(text, max_chars, overlap):
    clean = text.replace("\r\n", "\n")
    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + max_chars, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def embed_openai(base_url, model, texts):
    payload = {"model": model, "input": texts}
    result = json_request("POST", f"{base_url.rstrip('/')}/embeddings", payload)
    data = result.get("data", [])
    if len(data) != len(texts):
        raise RuntimeError(f"embedding count mismatch: got {len(data)}, expected {len(texts)}")
    return [item["embedding"] for item in sorted(data, key=lambda item: item.get("index", 0))]


def ensure_collection(qdrant_url, collection, vector_size):
    base = qdrant_url.rstrip("/")
    try:
        json_request("GET", f"{base}/collections/{collection}", timeout=20)
        return
    except RuntimeError as exc:
        if "HTTP 404" not in str(exc):
            raise
    payload = {"vectors": {"size": vector_size, "distance": "Cosine"}}
    json_request("PUT", f"{base}/collections/{collection}", payload, timeout=60)


def upsert_points(qdrant_url, collection, points):
    if not points:
        return
    payload = {"points": points}
    json_request(
        "PUT",
        f"{qdrant_url.rstrip('/')}/collections/{collection}/points?wait=true",
        payload,
        timeout=180,
    )


def iter_files(path):
    if os.path.isfile(path):
        yield path
        return
    for root, dirs, files in os.walk(path):
        dirs[:] = [item for item in dirs if item not in {".git", "__pycache__"}]
        for name in sorted(files):
            full = os.path.join(root, name)
            if os.path.splitext(name)[1].lower() in TEXT_SUFFIXES:
                yield full


def source_uri_for(path, root):
    rel = os.path.relpath(path, root) if root and os.path.isdir(root) else path
    return rel.replace(os.sep, "/")


def upsert_path(args):
    qdrant_url = args.qdrant_url
    collection = args.collection
    ensure_collection(qdrant_url, collection, args.vector_size)

    batch_texts = []
    batch_meta = []
    root = args.path if os.path.isdir(args.path) else os.path.dirname(args.path)
    indexed_chunks = 0

    for path in iter_files(args.path):
        text = read_text(path)
        source_sha = sha256_text(text)
        source_uri = args.source_prefix + source_uri_for(path, root)
        chunks = chunk_text(text, args.max_chars, args.overlap)
        for index, chunk in enumerate(chunks):
            batch_texts.append(chunk)
            batch_meta.append((path, source_uri, source_sha, index, chunk))
            if len(batch_texts) >= args.batch_size:
                indexed_chunks += flush_batch(args, batch_texts, batch_meta)
                batch_texts.clear()
                batch_meta.clear()

    indexed_chunks += flush_batch(args, batch_texts, batch_meta)
    print(json.dumps({"collection": collection, "indexed_chunks": indexed_chunks}, sort_keys=True))


def flush_batch(args, texts, meta):
    if not texts:
        return 0
    vectors = embed_openai(args.embedding_base_url, args.embedding_model, texts)
    points = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for vector, (path, source_uri, source_sha, index, chunk) in zip(vectors, meta):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_uri}:{index}:{sha256_text(chunk)}"))
        points.append(
            {
                "id": point_id,
                "vector": vector,
                "payload": {
                    "chunk_index": index,
                    "content_sha256": sha256_text(chunk),
                    "indexed_at": now,
                    "source_path": path,
                    "source_sha256": source_sha,
                    "source_uri": source_uri,
                    "text": chunk,
                },
            }
        )
    upsert_points(args.qdrant_url, args.collection, points)
    return len(points)


def search(args):
    vector = embed_openai(args.embedding_base_url, args.embedding_model, [args.query])[0]
    payload = {"vector": vector, "limit": args.limit, "with_payload": True}
    result = json_request(
        "POST",
        f"{args.qdrant_url.rstrip('/')}/collections/{args.collection}/points/search",
        payload,
        timeout=60,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def env_default(name, fallback):
    return os.environ.get(name, fallback)


def add_common(parser):
    parser.add_argument("--qdrant-url", default=env_default("QDRANT_URL", "http://127.0.0.1:6333"))
    parser.add_argument("--collection", default=env_default("CORTEX_COLLECTION", "kernel_evidence"))
    parser.add_argument("--embedding-base-url", default=env_default("EMBEDDING_API_BASE", "http://192.168.50.252:8091/v1"))
    parser.add_argument("--embedding-model", default=env_default("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5"))
    parser.add_argument("--vector-size", type=int, default=int(env_default("VECTOR_SIZE", "1024")))


def main():
    parser = argparse.ArgumentParser(description="Index/search kernel evidence with Qdrant.")
    sub = parser.add_subparsers(dest="command", required=True)

    upsert_file = sub.add_parser("upsert-file")
    add_common(upsert_file)
    upsert_file.add_argument("path")
    upsert_file.add_argument("--source-prefix", default="")
    upsert_file.add_argument("--max-chars", type=int, default=int(env_default("CORTEX_MAX_CHARS", "700")))
    upsert_file.add_argument("--overlap", type=int, default=int(env_default("CORTEX_OVERLAP", "70")))
    upsert_file.add_argument("--batch-size", type=int, default=int(env_default("CORTEX_BATCH_SIZE", "16")))
    upsert_file.set_defaults(func=upsert_path)

    upsert_dir = sub.add_parser("upsert-dir")
    add_common(upsert_dir)
    upsert_dir.add_argument("path")
    upsert_dir.add_argument("--source-prefix", default="")
    upsert_dir.add_argument("--max-chars", type=int, default=int(env_default("CORTEX_MAX_CHARS", "700")))
    upsert_dir.add_argument("--overlap", type=int, default=int(env_default("CORTEX_OVERLAP", "70")))
    upsert_dir.add_argument("--batch-size", type=int, default=int(env_default("CORTEX_BATCH_SIZE", "16")))
    upsert_dir.set_defaults(func=upsert_path)

    search_cmd = sub.add_parser("search")
    add_common(search_cmd)
    search_cmd.add_argument("query")
    search_cmd.add_argument("--limit", type=int, default=8)
    search_cmd.set_defaults(func=search)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(f"kernel_cortex: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
