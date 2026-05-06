# Agent Status

## Current status

Slice 10 is paused.

Slice 11 has been started to prepare Codex SSH readiness from `strix` to `amd` and `thinkcentre`.

## Current slice

Slice 11: prepare Codex SSH readiness.

## What changed

Updated repo state docs only:

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`

The new slice documents the SSH readiness checks needed before resuming Slice 10.

## What did not change

No remote hosts were modified.

Not changed:

- SSH config
- SSH keys
- remote files
- LiteLLM
- OpenCode config
- Open WebUI config
- Docker Compose services
- systemd services or timers

No `sudo` was run.

## Relevant finding

During the paused Slice 10 attempt, SSH from `strix` failed before reaching remote hosts because the local SSH client reported:

```text
Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
```

Using `ssh -F /dev/null` bypassed that config file, but hostname resolution then failed for `amd` and `thinkcentre` in the sandboxed command environment. Direct LAN IP SSH attempts were blocked by sandbox network restrictions before user approval completed.

## Safety state

Agents may inspect remote hosts read-only by SSH when the current slice allows it.

Agents must stop for explicit approval before any remote mutation, including:

- editing SSH config
- generating or installing SSH keys
- editing remote `authorized_keys`
- changing live service config
- restarting services
- altering LiteLLM, OpenCode, or Open WebUI

Agents must not print secrets, capture passwords, or ask the user to paste private keys into chat.

## Checks run

Documentation reads:

- `AGENTS.md`
- `CODEX_CONTEXT.md`
- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `PROJECT_PLAN.md`
- `DECISIONS.md`

No SSH diagnostics for Slice 11 were run yet.

## Results of checks

The repo docs support a narrow readiness slice because `strix` is the canonical project host, while `amd` owns OpenCode execution and `thinkcentre` owns Open WebUI/LiteLLM services.

Reliable read-only SSH inspection from `strix` to `amd` and `thinkcentre` is useful for reducing copy/paste, but any mutation still requires explicit operator approval.

## Known risks or blockers

- The local SSH client config problem may require a later approved `sudo` fix.
- Hostname resolution for `amd` and `thinkcentre` may require local hosts, DNS, Tailscale, or SSH config inspection.
- Passwordless SSH may not be set up yet.
- Key generation or remote `authorized_keys` changes are out of scope until explicitly approved.

## User approval needed

No approval is needed for the repo-doc update already made.

Approval will be needed before:

- running commands that require sandbox network escalation
- running `sudo`
- editing SSH config
- generating SSH keys
- installing public keys on remote hosts
- mutating any remote host or live service

## Recommended next action

Review the Slice 11 diff. If accepted, commit it, then run only the read-only diagnostic command block from `CURRENT_SLICE.md`.

## Slice 11 diagnostic result

Read-only SSH diagnostics were run manually from `strix`.

Results:

- `ssh amd 'hostname'` works using the user SSH alias.
- `ssh thinkcentre 'hostname'` works using the user SSH alias.
- Passwordless SSH works for both `amd` and `thinkcentre`.
- LAN SSH aliases in `~/.ssh/config` are the correct agent path.
- `ssh -F /dev/null` should not be used for normal agent inspection because it bypasses `~/.ssh/config`.
- The earlier system SSH config permission error was not reproducible in the normal shell.

Recommended agent rule:

- Codex may use normal read-only SSH commands through configured aliases such as `ssh amd '...'` and `ssh thinkcentre '...'`.
- Codex must not use `ssh -F /dev/null` unless explicitly troubleshooting SSH config behavior.
- Codex must still stop for approval before any remote mutation.

Recommended next action:

Resume Slice 10 OpenCode config verification using normal SSH aliases.
