#!/usr/bin/env python3
"""Resolve host-aware paths for the A733 kernel workflow."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import socket
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "inventory" / "kernel-workflow-paths.json"


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    if not path.exists():
        return {"schema": 0, "hosts": {}, "missing": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def current_host() -> str:
    return os.environ.get("KERNEL_WORKFLOW_HOST") or socket.gethostname().split(".")[0]


def host_config(registry: dict[str, Any], host: str | None = None) -> tuple[str, dict[str, Any]]:
    wanted = host or current_host()
    hosts = registry.get("hosts", {})
    if wanted in hosts:
        return wanted, hosts[wanted]
    for name, config in hosts.items():
        aliases = {str(item) for item in config.get("aliases", [])}
        aliases.add(name)
        if wanted in aliases:
            return name, config
    return wanted, {}


def clean_candidates(values: list[str | None]) -> list[str]:
    out: list[str] = []
    for value in values:
        if not value:
            continue
        if value not in out:
            out.append(value)
    return out


def select_path(candidates: list[str]) -> dict[str, Any]:
    cleaned = clean_candidates(candidates)
    for item in cleaned:
        if Path(item).exists():
            return {"selected": item, "exists": True, "candidates": cleaned}
    selected = cleaned[0] if cleaned else ""
    return {"selected": selected, "exists": False, "candidates": cleaned}


def build_env(host: str | None = None, registry_path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    registry = load_registry(registry_path)
    resolved_host, config = host_config(registry, host)

    public_repo = select_path(
        [
            os.environ.get("KERNEL_PUBLIC_REPO"),
            config.get("public_repo"),
            *config.get("public_repo_candidates", []),
            "/srv/projects/cubie-a7s-armbian-public",
            "/home/enzo/projects/radxa_cubie_a7s_allwinner_a733",
            "/Users/enzo/projects/Home Lab/cubie-a7s-armbian",
        ]
    )
    kernel_tree = select_path(
        [
            os.environ.get("KERNEL_TREE_PATH"),
            config.get("kernel_tree"),
            *config.get("kernel_tree_candidates", []),
            "/srv/projects/a733-prereq-stack-current",
            "/srv/projects/cubie-a7s-armbian/sources/mainline-linux",
            "/srv/projects/kernel-work/scratch/strix-mainline-linux",
            "/Users/enzo/projects/linux-a733",
        ]
    )
    patch_export = select_path(
        [
            os.environ.get("KERNEL_PATCH_EXPORT"),
            config.get("patch_export"),
            str(Path(public_repo["selected"]) / "patches") if public_repo["selected"] else None,
        ]
    )
    rfc_recheck_dir = select_path(
        [
            os.environ.get("A733_RFC_RECHECK_DIR"),
            config.get("rfc_recheck_dir"),
            str(REPO_ROOT / "task-packets" / "kernel" / "research"),
        ]
    )
    hermes_work_dir = select_path(
        [
            os.environ.get("HERMES_KERNEL_WORK_DIR"),
            config.get("hermes_work_dir"),
            str(REPO_ROOT / "task-packets" / "kernel" / "hermes-work"),
        ]
    )
    runtime_approval_dir = select_path(
        [
            os.environ.get("CUBIE_RUNTIME_APPROVAL_DIR"),
            config.get("runtime_approval_dir"),
            str(REPO_ROOT / "task-packets" / "kernel" / "approvals"),
        ]
    )

    return {
        "host": resolved_host,
        "detected_host": current_host(),
        "registry": str(registry_path),
        "config_found": bool(config),
        "paths": {
            "homelab_repo": select_path([config.get("homelab_repo"), str(REPO_ROOT)]),
            "public_repo": public_repo,
            "patch_export": patch_export,
            "kernel_tree": kernel_tree,
            "rfc_recheck_dir": rfc_recheck_dir,
            "hermes_work_dir": hermes_work_dir,
            "runtime_approval_dir": runtime_approval_dir,
        },
        "remote": {
            "kernel_tree_remote": config.get("kernel_tree_remote", ""),
        },
        "resource_policy": registry.get("resource_policy", {}),
        "generated_state_policy": registry.get("generated_state_policy", {}),
        "notes": config.get("notes", []),
    }


def shell_exports(env: dict[str, Any]) -> str:
    paths = env["paths"]
    exports = {
        "KERNEL_WORKFLOW_HOST": env["host"],
        "KERNEL_PUBLIC_REPO": paths["public_repo"]["selected"],
        "KERNEL_PATCH_EXPORT": paths["patch_export"]["selected"],
        "KERNEL_TREE_PATH": paths["kernel_tree"]["selected"],
        "A733_RFC_RECHECK_DIR": paths["rfc_recheck_dir"]["selected"],
        "HERMES_KERNEL_WORK_DIR": paths["hermes_work_dir"]["selected"],
        "CUBIE_RUNTIME_APPROVAL_DIR": paths["runtime_approval_dir"]["selected"],
    }
    return "\n".join(f"export {key}={shlex.quote(str(value))}" for key, value in exports.items() if value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", help="Resolve paths for this registry host instead of auto-detecting")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--shell", action="store_true")
    args = parser.parse_args()

    env = build_env(args.host, Path(args.registry))
    if args.shell:
        print(shell_exports(env))
    elif args.json:
        print(json.dumps(env, indent=2, sort_keys=True))
    else:
        print(f"host={env['host']}")
        for name, value in env["paths"].items():
            print(f"{name}={value['selected']} exists={str(value['exists']).lower()}")
        if env["remote"].get("kernel_tree_remote"):
            print(f"kernel_tree_remote={env['remote']['kernel_tree_remote']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
