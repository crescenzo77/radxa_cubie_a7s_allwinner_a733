#!/usr/bin/env python3
"""LAN UI for changing Hermes Agent model priority on ThinkCentre.

The app intentionally edits only the user Hermes config. It discovers models
from the Open WebUI/model-dispatch hub and exposes only Hermes-eligible models:
free OpenRouter models and online local chat models with enough context.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - runtime guard
    raise SystemExit("PyYAML is required. Run with Hermes' venv Python.") from exc


HOST = os.environ.get("HERMES_MODEL_PRIORITY_HOST", "0.0.0.0")
PORT = int(os.environ.get("HERMES_MODEL_PRIORITY_PORT", "9130"))
CONFIG_PATH = Path(os.environ.get("HERMES_CONFIG", "~/.hermes/config.yaml")).expanduser()
HUB_BASE_URL = os.environ.get("HERMES_MODEL_HUB_URL", "http://192.168.50.225:4011/v1").rstrip("/")
PROVIDER = os.environ.get("HERMES_MODEL_PROVIDER", "openwebui-hub")
MIN_CONTEXT = int(os.environ.get("HERMES_MIN_CONTEXT", "64000"))
ALLOW_3090 = os.environ.get("HERMES_ALLOW_3090", "").lower() in {"1", "true", "yes", "on"}
RESTART_GATEWAY = os.environ.get("HERMES_RESTART_GATEWAY", "1").lower() not in {"0", "false", "no"}
GATEWAY_SERVICE = os.environ.get("HERMES_GATEWAY_SERVICE", "hermes-gateway.service")


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hermes Model Priority</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #101418;
      --panel: #171d23;
      --panel2: #202833;
      --text: #e7edf3;
      --muted: #9caab8;
      --line: #34404d;
      --accent: #51a2ff;
      --good: #43c478;
      --warn: #f0b84f;
      --bad: #f26d6d;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.4 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      padding: 18px 22px;
      border-bottom: 1px solid var(--line);
      display: flex;
      gap: 16px;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    h1 { font-size: 20px; margin: 0; font-weight: 650; }
    main {
      display: grid;
      grid-template-columns: minmax(320px, 1fr) minmax(320px, 1fr);
      gap: 14px;
      padding: 14px;
      max-width: 1500px;
      margin: 0 auto;
    }
    section {
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      min-height: 200px;
      overflow: hidden;
    }
    section h2 {
      margin: 0;
      font-size: 15px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel2);
    }
    .toolbar { display: flex; flex-wrap: wrap; gap: 8px; }
    button, select, input {
      color: var(--text);
      background: var(--panel2);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
    }
    button { cursor: pointer; }
    button:hover { border-color: var(--accent); }
    button.primary { background: #174a7c; border-color: #2f82d0; }
    button.good { background: #1d5b3b; border-color: #358a5b; }
    button.warn { background: #5f4416; border-color: #99732a; }
    .status {
      white-space: pre-wrap;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: var(--muted);
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      background: #0d1116;
    }
    .list { display: flex; flex-direction: column; gap: 8px; padding: 10px; }
    .model {
      border: 1px solid var(--line);
      background: #111820;
      border-radius: 7px;
      padding: 10px;
      display: grid;
      gap: 8px;
    }
    .model-title { font-weight: 650; overflow-wrap: anywhere; }
    .meta { display: flex; flex-wrap: wrap; gap: 6px; color: var(--muted); font-size: 12px; }
    .tag {
      border: 1px solid var(--line);
      background: #0e141a;
      border-radius: 999px;
      padding: 2px 7px;
    }
    .tag.good { color: var(--good); border-color: #285b3d; }
    .tag.warn { color: var(--warn); border-color: #5f4b1b; }
    .tag.bad { color: var(--bad); border-color: #6a3434; }
    .actions { display: flex; gap: 6px; flex-wrap: wrap; }
    .hidden { display: none; }
    .wide { grid-column: 1 / -1; }
    details { padding: 0 10px 10px; }
    summary { cursor: pointer; color: var(--muted); }
    @media (max-width: 850px) {
      main { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Hermes Model Priority</h1>
      <div id="subtitle" class="meta"></div>
    </div>
    <div class="toolbar">
      <button onclick="loadState()">Refresh</button>
      <button onclick="presetFreeFirst()">Free first</button>
      <button onclick="presetLocalFirst()">Local first</button>
      <button class="primary" onclick="applyOrder()">Apply order</button>
    </div>
  </header>
  <div id="status" class="status">Loading...</div>
  <main>
    <section>
      <h2>Active Priority Order</h2>
      <div id="active" class="list"></div>
    </section>
    <section>
      <h2>Available Eligible Models</h2>
      <div id="available" class="list"></div>
    </section>
    <section class="wide">
      <h2>Excluded By Safety / Viability Rules</h2>
      <details>
        <summary>Show excluded models</summary>
        <div id="excluded" class="list"></div>
      </details>
    </section>
  </main>
  <script>
    let state = null;
    let activeOrder = [];

    function fmtContext(n) {
      if (!n) return "context unknown";
      if (n >= 1000000) return Math.round(n / 1000) + "k ctx";
      return Math.round(n / 1000) + "k ctx";
    }

    function tags(model) {
      const out = [];
      out.push(`<span class="tag ${model.source === "local" ? "good" : "warn"}">${model.source}</span>`);
      if (model.free_only) out.push(`<span class="tag good">free only</span>`);
      if (model.router) out.push(`<span class="tag warn">router</span>`);
      if (model.online === true) out.push(`<span class="tag good">online</span>`);
      out.push(`<span class="tag">${fmtContext(model.context)}</span>`);
      return out.join("");
    }

    function renderModel(model, mode, idx) {
      const title = escapeHtml(model.id);
      const buttons = [];
      if (mode === "active") {
        buttons.push(`<button onclick="moveActive(${idx}, -1)">Up</button>`);
        buttons.push(`<button onclick="moveActive(${idx}, 1)">Down</button>`);
        buttons.push(`<button onclick="removeActive(${idx})">Remove</button>`);
      } else if (!activeOrder.includes(model.id)) {
        buttons.push(`<button class="good" onclick="addActive('${encodeURIComponent(model.id)}')">Add</button>`);
      } else {
        buttons.push(`<button disabled>Added</button>`);
      }
      return `<div class="model">
        <div class="model-title">${title}</div>
        <div class="meta">${tags(model)}</div>
        ${model.reason ? `<div class="meta"><span class="tag bad">${escapeHtml(model.reason)}</span></div>` : ""}
        <div class="actions">${buttons.join("")}</div>
      </div>`;
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }[c]));
    }

    function modelById(id) {
      return state.eligible.find(m => m.id === id) || state.current.find(m => m.id === id) || {id, source: "unknown"};
    }

    function render() {
      document.getElementById("subtitle").innerHTML =
        `<span class="tag">provider ${escapeHtml(state.provider)}</span>` +
        `<span class="tag">min ${fmtContext(state.min_context)}</span>` +
        `<span class="tag">hub ${escapeHtml(state.hub_base_url)}</span>`;
      document.getElementById("active").innerHTML =
        activeOrder.length ? activeOrder.map((id, i) => renderModel(modelById(id), "active", i)).join("") :
        `<div class="model"><div class="model-title">No active order selected</div></div>`;
      document.getElementById("available").innerHTML =
        state.eligible.map(m => renderModel(m, "available")).join("");
      document.getElementById("excluded").innerHTML =
        state.excluded.length ? state.excluded.map(m => renderModel(m, "excluded")).join("") :
        `<div class="model"><div class="model-title">No excluded models reported</div></div>`;
    }

    async function loadState() {
      document.getElementById("status").textContent = "Loading...";
      const res = await fetch("/api/state");
      state = await res.json();
      if (!res.ok) {
        document.getElementById("status").textContent = JSON.stringify(state, null, 2);
        return;
      }
      activeOrder = state.current.map(m => m.id).filter(id => state.eligible.some(m => m.id === id));
      document.getElementById("status").textContent = state.message;
      render();
    }

    function addActive(encoded) {
      const id = decodeURIComponent(encoded);
      if (!activeOrder.includes(id)) activeOrder.push(id);
      render();
    }
    function removeActive(idx) {
      activeOrder.splice(idx, 1);
      render();
    }
    function moveActive(idx, delta) {
      const next = idx + delta;
      if (next < 0 || next >= activeOrder.length) return;
      [activeOrder[idx], activeOrder[next]] = [activeOrder[next], activeOrder[idx]];
      render();
    }
    function presetFreeFirst() {
      activeOrder = state.eligible
        .filter(m => m.source === "openrouter-free")
        .map(m => m.id)
        .concat(state.eligible.filter(m => m.source === "local").map(m => m.id));
      render();
    }
    function presetLocalFirst() {
      activeOrder = state.eligible
        .filter(m => m.source === "local")
        .map(m => m.id)
        .concat(state.eligible.filter(m => m.source === "openrouter-free").map(m => m.id));
      render();
    }
    async function applyOrder() {
      if (!activeOrder.length) {
        document.getElementById("status").textContent = "Refusing to apply an empty model order.";
        return;
      }
      document.getElementById("status").textContent = "Applying...";
      const res = await fetch("/api/apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({order: activeOrder})
      });
      const body = await res.json();
      await loadState();
      document.getElementById("status").textContent = JSON.stringify(body, null, 2);
    }
    loadState().catch(err => {
      document.getElementById("status").textContent = String(err.stack || err);
    });
  </script>
</body>
</html>
"""


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{CONFIG_PATH} did not parse as a YAML mapping")
    return data


def fetch_hub_models() -> list[dict[str, Any]]:
    url = f"{HUB_BASE_URL}/models"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    data = body.get("data", [])
    if not isinstance(data, list):
        raise ValueError(f"{url} returned unexpected model payload")
    return [item for item in data if isinstance(item, dict)]


def provider_models(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    provider = ((config.get("providers") or {}).get(PROVIDER) or {})
    models = provider.get("models") or {}
    return models if isinstance(models, dict) else {}


def current_order(config: dict[str, Any]) -> list[str]:
    order: list[str] = []
    primary = ((config.get("providers") or {}).get(PROVIDER) or {}).get("model")
    if not primary:
        primary = ((config.get("providers") or {}).get(PROVIDER) or {}).get("default_model")
    if not primary:
        primary = (config.get("model") or {}).get("default")
    if isinstance(primary, str) and primary:
        order.append(primary)
    for item in config.get("fallback_providers") or []:
        if not isinstance(item, dict):
            continue
        if item.get("provider") == PROVIDER and isinstance(item.get("model"), str):
            order.append(item["model"])
    return dedupe(order)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def classify(raw: dict[str, Any], config_models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    model_id = str(raw.get("id") or "")
    meta = raw.get("meta") if isinstance(raw.get("meta"), dict) else {}
    cfg = config_models.get(model_id) or {}
    context = as_int(meta.get("context")) or as_int(cfg.get("context_length"))
    owned_by = str(raw.get("owned_by") or "")
    kind = str(meta.get("kind") or "chat")
    is_openrouter = owned_by == "openrouter-free" or model_id.startswith("openrouter-free /")
    is_local = owned_by == "homelab-local"
    free_only = bool(meta.get("free_only") or cfg.get("free_only"))
    router = bool(meta.get("router") or cfg.get("router"))
    online = meta.get("online")
    if router and not context:
        context = as_int(cfg.get("context_length")) or 200000

    model = {
        "id": model_id,
        "owned_by": owned_by,
        "source": "openrouter-free" if is_openrouter else "local" if is_local else "other",
        "context": context,
        "free_only": free_only,
        "router": router,
        "online": online,
        "kind": kind,
        "eligible": False,
        "reason": "",
    }

    lower_id = model_id.lower()
    if not model_id:
        model["reason"] = "missing model id"
    elif "3090" in lower_id and not ALLOW_3090:
        model["reason"] = "RTX 3090 disabled by policy while ComfyUI may own it"
    elif "embedding" in lower_id or kind == "embedding":
        model["reason"] = "embedding model, not Hermes chat model"
    elif is_openrouter:
        if not free_only:
            model["reason"] = "OpenRouter model is not marked free_only"
        elif not context or context < MIN_CONTEXT:
            model["reason"] = f"context below {MIN_CONTEXT}"
        else:
            model["eligible"] = True
    elif is_local:
        if kind != "chat":
            model["reason"] = f"local model kind is {kind}, not chat"
        elif online is not True:
            model["reason"] = "local model is not reported online"
        elif not context or context < MIN_CONTEXT:
            model["reason"] = f"context below {MIN_CONTEXT}"
        else:
            model["eligible"] = True
    else:
        model["reason"] = "not a supported Hermes provider model"
    return model


def collect_state() -> dict[str, Any]:
    config = load_config()
    config_models = provider_models(config)
    errors: list[str] = []
    raw_models: list[dict[str, Any]] = []
    try:
        raw_models = fetch_hub_models()
    except Exception as exc:
        errors.append(f"hub fetch failed: {exc}")
        for model_id, cfg in config_models.items():
            raw_models.append({"id": model_id, "owned_by": "openrouter-free" if cfg.get("free_only") else "homelab-local", "meta": cfg})

    by_id: dict[str, dict[str, Any]] = {}
    for raw in raw_models:
        model = classify(raw, config_models)
        by_id[model["id"]] = model

    eligible = sorted(
        [m for m in by_id.values() if m["eligible"]],
        key=lambda m: (0 if m["source"] == "local" else 1, 0 if m["router"] else 1, m["id"].lower()),
    )
    excluded = sorted(
        [m for m in by_id.values() if not m["eligible"]],
        key=lambda m: (m["source"], m["reason"], m["id"].lower()),
    )
    order_ids = current_order(config)
    current = [by_id.get(model_id) or {"id": model_id, "source": "missing", "reason": "not in hub response"} for model_id in order_ids]
    primary = order_ids[0] if order_ids else ""
    return {
        "provider": PROVIDER,
        "hub_base_url": HUB_BASE_URL,
        "config_path": str(CONFIG_PATH),
        "min_context": MIN_CONTEXT,
        "allow_3090": ALLOW_3090,
        "restart_gateway": RESTART_GATEWAY,
        "gateway_service": GATEWAY_SERVICE,
        "primary": primary,
        "current": current,
        "eligible": eligible,
        "excluded": excluded,
        "errors": errors,
        "message": "\n".join(errors) if errors else f"Loaded {len(eligible)} eligible models. Primary: {primary}",
    }


def write_config_order(order: list[str], state: dict[str, Any]) -> dict[str, Any]:
    eligible = {m["id"]: m for m in state["eligible"]}
    clean_order = dedupe([str(item) for item in order if isinstance(item, str) and item])
    if not clean_order:
        raise ValueError("empty model order")
    unknown = [item for item in clean_order if item not in eligible]
    if unknown:
        raise ValueError(f"order contains ineligible/unknown models: {unknown}")

    config = load_config()
    backup_path = CONFIG_PATH.with_name(
        f"{CONFIG_PATH.name}.bak.model-priority-ui.{dt.datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    shutil.copy2(CONFIG_PATH, backup_path)

    model_cfg = config.setdefault("model", {})
    if not isinstance(model_cfg, dict):
        model_cfg = {}
        config["model"] = model_cfg
    model_cfg["provider"] = PROVIDER
    model_cfg["default"] = clean_order[0]

    providers = config.setdefault("providers", {})
    if not isinstance(providers, dict):
        providers = {}
        config["providers"] = providers
    provider_cfg = providers.setdefault(PROVIDER, {})
    if not isinstance(provider_cfg, dict):
        provider_cfg = {}
        providers[PROVIDER] = provider_cfg
    provider_cfg["model"] = clean_order[0]
    provider_cfg["default_model"] = clean_order[0]
    models_cfg = provider_cfg.setdefault("models", {})
    if not isinstance(models_cfg, dict):
        models_cfg = {}
        provider_cfg["models"] = models_cfg
    for model_id in clean_order:
        details = eligible[model_id]
        item = models_cfg.setdefault(model_id, {})
        if details.get("context"):
            item["context_length"] = int(details["context"])
        if details.get("source") == "openrouter-free":
            item["free_only"] = True

    config["fallback_providers"] = [{"provider": PROVIDER, "model": model_id} for model_id in clean_order[1:]]

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(CONFIG_PATH.parent), delete=False) as fh:
        yaml.safe_dump(config, fh, sort_keys=False, allow_unicode=True)
        tmp_path = Path(fh.name)
    os.chmod(tmp_path, 0o600)
    os.replace(tmp_path, CONFIG_PATH)

    restart_result = None
    if RESTART_GATEWAY:
        proc = subprocess.run(
            ["systemctl", "--user", "restart", GATEWAY_SERVICE],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        restart_result = {
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    return {
        "ok": True,
        "primary": clean_order[0],
        "fallback_count": max(len(clean_order) - 1, 0),
        "backup": str(backup_path),
        "gateway_restart": restart_result,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "HermesModelPriorityUI/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_HEAD(self) -> None:
        if self.path in {"/", "/index.html", "/api/state", "/api/health"}:
            self.send_response(HTTPStatus.OK)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self.respond_text(HTML, "text/html; charset=utf-8")
            return
        if self.path == "/api/state":
            self.respond_json(collect_state())
            return
        if self.path == "/api/health":
            self.respond_json({"ok": True, "config": str(CONFIG_PATH), "hub": HUB_BASE_URL})
            return
        self.respond_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/apply":
            self.respond_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(body, dict):
                raise ValueError("JSON body must be an object")
            order = body.get("order")
            if not isinstance(order, list):
                raise ValueError("order must be a list")
            result = write_config_order(order, collect_state())
            self.respond_json(result)
        except Exception as exc:
            self.respond_json(
                {"ok": False, "error": str(exc), "trace": traceback.format_exc()},
                HTTPStatus.BAD_REQUEST,
            )

    def respond_text(self, body: str, content_type: str) -> None:
        data = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def respond_json(self, body: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Hermes model priority UI listening on http://{HOST}:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
