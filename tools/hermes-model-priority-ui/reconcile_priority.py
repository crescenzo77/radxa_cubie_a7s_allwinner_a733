#!/usr/bin/env python3
"""Reconcile Hermes model priority after the OpenRouter free cache refreshes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import app


AUTO_FREE_MODEL = "openrouter-free / Auto Free Router random available free model"
STATE_PATH = Path(os.environ.get("HERMES_PRIORITY_STATE", "~/.hermes/model-priority-ui/reconcile_state.json")).expanduser()
OPENROUTER_DEGRADED_MODE = os.environ.get("HERMES_OPENROUTER_DEGRADED_MODE", "1").lower() not in {
    "0",
    "false",
    "no",
    "off",
}
OPENROUTER_PROBE_TIMEOUT = float(os.environ.get("HERMES_OPENROUTER_PROBE_TIMEOUT", "25"))


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def read_state() -> dict[str, Any]:
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def write_state(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_name(f".{STATE_PATH.name}.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.chmod(0o600)
    tmp.replace(STATE_PATH)


def openrouter_probe(model_id: str = AUTO_FREE_MODEL) -> dict[str, Any]:
    if not OPENROUTER_DEGRADED_MODE:
        return {"enabled": False, "ok": True, "reason": "disabled"}

    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Reply with OK."}],
        "max_tokens": 8,
        "temperature": 0,
        "stream": False,
    }
    url = f"{app.HUB_BASE_URL}/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=OPENROUTER_PROBE_TIMEOUT) as response:
            body = json.loads(response.read().decode("utf-8"))
        choices = body.get("choices") if isinstance(body, dict) else None
        ok = isinstance(choices, list) and bool(choices)
        return {
            "enabled": True,
            "model": model_id,
            "ok": ok,
            "status": getattr(response, "status", None),
            "reason": "" if ok else "empty choices",
        }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        return {"enabled": True, "model": model_id, "ok": False, "status": exc.code, "reason": detail or str(exc)}
    except Exception as exc:
        return {"enabled": True, "model": model_id, "ok": False, "reason": str(exc)}


def baseline_ids(eligible: list[dict[str, Any]]) -> list[str]:
    eligible_ids = {model["id"] for model in eligible}
    requested = [
        item.strip()
        for item in os.environ.get("HERMES_PRIORITY_BASELINE", "").splitlines()
        if item.strip()
    ]
    if not requested:
        requested = [AUTO_FREE_MODEL]
        requested.extend(
            model["id"]
            for model in eligible
            if model.get("source") == "local" and str(model.get("id", "")).startswith("Strix ")
        )
    return [model_id for model_id in requested if model_id in eligible_ids]


def reconcile_order(state: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    eligible = state["eligible"]
    eligible_ids = {model["id"] for model in eligible}
    current_ids = [model["id"] for model in state["current"] if isinstance(model.get("id"), str)]

    kept: list[str] = []
    pruned: list[str] = []
    for model_id in current_ids:
        if model_id in eligible_ids:
            if model_id not in kept:
                kept.append(model_id)
        else:
            pruned.append(model_id)

    added: list[str] = []
    for model_id in baseline_ids(eligible):
        if model_id not in kept:
            kept.append(model_id)
            added.append(model_id)

    if not kept and eligible:
        kept.append(eligible[0]["id"])
        added.append(eligible[0]["id"])

    return kept, pruned, added


def local_first_order(order: list[str], eligible: list[dict[str, Any]]) -> list[str]:
    local_ids = [model["id"] for model in eligible if model.get("source") == "local"]
    local_ids = [model_id for model_id in local_ids if model_id in order]
    rest = [model_id for model_id in order if model_id not in local_ids]
    return local_ids + rest


def restore_preferred_order(preferred: list[str], eligible: list[dict[str, Any]]) -> list[str]:
    eligible_ids = {model["id"] for model in eligible}
    restored = [model_id for model_id in preferred if model_id in eligible_ids]
    for model_id in baseline_ids(eligible):
        if model_id not in restored:
            restored.append(model_id)
    return restored


def first_openrouter_model(order: list[str]) -> str:
    for model_id in order:
        if model_id.startswith("openrouter-free / "):
            return model_id
    return AUTO_FREE_MODEL


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="show the reconciled order without writing config")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args()

    state = app.collect_state()
    if state.get("errors"):
        result = {
            "ok": False,
            "changed": False,
            "dry_run": args.dry_run,
            "errors": state["errors"],
            "message": "refusing to reconcile while model discovery has errors",
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("hermes-priority-reconcile: refusing to reconcile while model discovery has errors", file=sys.stderr)
            for error in state["errors"]:
                print(f"error: {error}", file=sys.stderr)
        return 2

    old_order = [model["id"] for model in state["current"] if isinstance(model.get("id"), str)]
    new_order, pruned, added = reconcile_order(state)
    persisted = read_state()
    probe = openrouter_probe(first_openrouter_model(new_order))
    mode = "normal"

    if OPENROUTER_DEGRADED_MODE and not probe.get("ok"):
        mode = "openrouter_degraded"
        if persisted.get("mode") != "openrouter_degraded":
            persisted["preferred_order_before_degraded"] = old_order
        persisted["mode"] = "openrouter_degraded"
        persisted["openrouter_last_failure"] = {"at": now_iso(), "probe": probe}
        new_order = local_first_order(new_order, state["eligible"])
    elif persisted.get("mode") == "openrouter_degraded":
        mode = "openrouter_recovered"
        preferred = persisted.get("preferred_order_before_degraded")
        if isinstance(preferred, list):
            new_order = restore_preferred_order([str(item) for item in preferred], state["eligible"])
        persisted["mode"] = "normal"
        persisted["openrouter_recovered_at"] = now_iso()
    else:
        persisted["mode"] = "normal"
        persisted["preferred_order_before_degraded"] = new_order

    changed = old_order != new_order

    result: dict[str, Any] = {
        "ok": True,
        "changed": changed,
        "dry_run": args.dry_run,
        "mode": mode,
        "openrouter_probe": probe,
        "old_order": old_order,
        "new_order": new_order,
        "pruned": pruned,
        "added_baseline": added,
        "eligible_count": len(state["eligible"]),
        "excluded_count": len(state["excluded"]),
    }

    if changed and not args.dry_run:
        result["apply"] = app.write_config_order(new_order, state)
    if not args.dry_run:
        write_state(persisted)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if changed:
            action = "would update" if args.dry_run else "updated"
            print(f"hermes-priority-reconcile: {action} order")
        else:
            print("hermes-priority-reconcile: no changes")
        if mode != "normal":
            print(f"mode={mode}")
        if probe.get("enabled") and not probe.get("ok"):
            print(f"openrouter-probe-failed: {probe.get('reason')}")
        print(f"eligible={result['eligible_count']} excluded={result['excluded_count']}")
        for model_id in pruned:
            print(f"pruned: {model_id}")
        for model_id in added:
            print(f"added-baseline: {model_id}")
        print("order:")
        for idx, model_id in enumerate(new_order, 1):
            print(f"{idx}. {model_id}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"hermes-priority-reconcile: ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
