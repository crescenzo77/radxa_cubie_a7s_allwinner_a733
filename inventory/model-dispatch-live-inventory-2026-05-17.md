# model-dispatch Live Inventory — 2026-05-17

## Purpose and Boundaries

This document records the approved read-only inventory of
`thinkcentre:/srv/model-dispatch` for Slice 1 include/exclude planning.

The goal is to understand the live file shape before deciding what belongs in a
first-class source repo.

Boundaries:

- Read names and metadata only.
- Do not print file contents.
- Do not read `.env`, key, token, secret, database, sqlite, log, cache, or
  generated runtime file contents.
- Do not copy `/srv/model-dispatch`.
- Do not create `strix:/srv/projects/model-dispatch`.
- Do not create `thinkcentre:/srv/git/model-dispatch.git`.
- Do not restart services.
- Do not edit live config.
- Do not run `sudo`.

## Commands Run

Initial SSH attempts using hostname failed before inventory due to local SSH/DNS
issues:

```bash
ssh thinkcentre 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'
ssh -F /dev/null thinkcentre 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'
```

Successful read-only inventory commands used the LAN IP and ignored the local
SSH config:

```bash
ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'
ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -maxdepth 4 \( -name ".env" -o -iname "*secret*" -o -iname "*token*" -o -iname "*key*" -o -iname "*.log" -o -iname "*.db" -o -iname "*.sqlite" -o -iname "*.sqlite3" -o -name "__pycache__" -o -name ".venv" -o -name "venv" -o -name "node_modules" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" \) -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'
ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -path /srv/model-dispatch/.git -prune -o -maxdepth 2 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'
ssh -F /dev/null 192.168.50.225 'git -C /srv/model-dispatch status --short && git -C /srv/model-dispatch branch --show-current && git -C /srv/model-dispatch log --oneline -5'
ssh -F /dev/null 192.168.50.225 'git -C /srv/model-dispatch remote -v'
ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -path /srv/model-dispatch/.git -prune -o -type f -printf "%f\n" | awk "{n=split(\$0,a,\".\"); if (n==1) print \"[no extension]\"; else print a[n]}" | sort | uniq -c'
```

No file contents were printed.

## Directory and File Inventory Summary

Top-level live directory:

```text
d 4096 2026-05-16 12:10 /srv/model-dispatch
```

Top-level non-`.git` files:

| Type | Size | Timestamp | Path |
|---|---:|---|---|
| file | 152 | 2026-05-16 12:08 | `/srv/model-dispatch/.cgcignore` |
| file | 116 | 2026-05-16 12:10 | `/srv/model-dispatch/.gitignore` |
| file | 9346 | 2026-05-13 09:39 | `/srv/model-dispatch/app.py` |
| file | 5214 | 2026-05-11 11:36 | `/srv/model-dispatch/app.py.20260511-113634.bak` |
| file | 8420 | 2026-05-11 11:41 | `/srv/model-dispatch/app.py.20260511-114112.bak` |
| file | 8890 | 2026-05-13 09:32 | `/srv/model-dispatch/app.py.20260513-093223.bak` |
| file | 9282 | 2026-05-13 09:37 | `/srv/model-dispatch/app.py.20260513-093708.bak` |
| file | 2526 | 2026-05-11 11:33 | `/srv/model-dispatch/config.json` |
| file | 2285 | 2026-05-11 11:33 | `/srv/model-dispatch/config.json.20260511-113332.bak` |
| file | 2526 | 2026-05-11 11:36 | `/srv/model-dispatch/config.json.20260511-113634.bak` |
| file | 77829 | 2026-05-17 11:08 | `/srv/model-dispatch/dispatch.log` |

File extension summary outside `.git`:

| Extension | Count |
|---|---:|
| `bak` | 6 |
| `cgcignore` | 1 |
| `gitignore` | 1 |
| `json` | 1 |
| `log` | 1 |
| `py` | 1 |

## Git Metadata Summary

`/srv/model-dispatch` already contains a `.git` directory.

Observed Git metadata:

- Branch: `main`
- Recent commit: `ef65a5c initialize model dispatch service repo`
- `git status --short`: no output, so the live working tree appeared clean at
  inventory time.
- `git remote -v`: no output, so no remote was configured or visible from the
  read-only check.

Important note:
This means the live service directory already has local Git metadata, but it is
not yet documented as the canonical source repo. The target remains
`strix:/srv/projects/model-dispatch`, with ThinkCentre live runtime kept
separate from source ownership.

## Candidate Source Files to Include Later

Candidate source files from the live tree:

- `app.py`
- `config.json`
- `.gitignore`
- `.cgcignore`

These should be reviewed before copy. `config.json` may contain route
definitions or endpoint URLs; it must be checked for secrets before being added
to a public or shared repo.

## config.json Safety Review

A safe, non-secret-dumping review of
`thinkcentre:/srv/model-dispatch/config.json` was completed before creating any
Strix source repo candidate.

Review boundaries:

- Full config values were not printed.
- JSON shape only was printed.
- A redacted value preview was printed where strings were shown only as
  lengths.
- No live files were edited.
- No files were copied.

Observed root keys:

- `listen_host`
- `listen_port`
- `models`
- `routes`
- `reserved_output_tokens`
- `token_estimate_divisor`

Observed structure:

- `models` is a list of 8 entries.
- Model entries have these keys:
  - `id`
  - `display`
  - `role`
  - `endpoint`
  - `served_model`
  - `context`
- `routes` has these keys:
  - `auto-local`
  - `auto-coding-local`
  - `auto-reasoning-local`
  - `auto-small-local`

The suspicious-key scan only returned:

- `reserved_output_tokens`
- `token_estimate_divisor`

Those are token-budget/routing settings, not credential fields.

No API key, password, secret, bearer, auth, credential, or token credential
field was shown. Based on the safe review, `config.json` appears to be
route/model registry configuration.

Remaining risk:
Endpoint strings and served model names are internal operational details.
`config.json` is acceptable for a private homelab source candidate, but should
not be published publicly without sanitization.

## Candidate Docs, Config, and Tests to Add Later

The live tree does not currently show first-class docs or tests in the
metadata-only inventory.

Recommended additions for the future source repo:

- `README.md`
- `ROUTING.md`
- `SERVICE.md`
- `DEPLOYMENT.md`
- `DECISIONS.md`
- `tests/`
- A dependency manifest if not already embedded elsewhere:
  - `requirements.txt`, `pyproject.toml`, or equivalent.
- Example sanitized config if `config.json` cannot be safely committed as-is.

## Candidate Excludes

Exclude from a later source-repo copy by default:

- `.git/`
- `dispatch.log`
- `*.log`
- `*.bak`
- `.env`
- `*.env`
- Files or directories matching `*secret*`, `*token*`, or `*key*`.
- Runtime databases:
  - `*.db`
  - `*.sqlite`
  - `*.sqlite3`
- Caches:
  - `__pycache__/`
  - `.pytest_cache/`
  - `.mypy_cache/`
  - `.ruff_cache/`
- Virtual environments:
  - `.venv/`
  - `venv/`
- Dependency/vendor directories:
  - `node_modules/`
- Generated runtime files and request logs.

Observed candidate exclude in this inventory:

- `/srv/model-dispatch/dispatch.log`
- Backup snapshots:
  - `/srv/model-dispatch/app.py.20260511-113634.bak`
  - `/srv/model-dispatch/app.py.20260511-114112.bak`
  - `/srv/model-dispatch/app.py.20260513-093223.bak`
  - `/srv/model-dispatch/app.py.20260513-093708.bak`
  - `/srv/model-dispatch/config.json.20260511-113332.bak`
  - `/srv/model-dispatch/config.json.20260511-113634.bak`

The likely-secret/log/cache name scan only matched:

- `/srv/model-dispatch/dispatch.log`

No `.env`, obvious secret, token, key, database, sqlite, cache, virtualenv, or
`__pycache__` path was reported by name in the max-depth-4 scan.

## Unknowns Requiring User Review

- Whether `config.json` should be sanitized before any public publication. The
  safe review found route/model registry configuration and no credential fields,
  but endpoint strings and served model names are internal operational details.
- Whether `app.py` embeds endpoints, tokens, local paths, or operational details
  that should be moved into sanitized config.
- Whether the existing live `.git` history should be preserved, archived, or
  ignored when creating the Strix canonical source repo.
- Whether `ef65a5c initialize model dispatch service repo` is already the
  desired initial source commit or just live-path scratch history.
- Whether backup snapshots contain useful history that should be manually
  summarized before exclusion.
- Whether `dispatch.log` contains request data, prompts, model responses, IPs,
  or other sensitive runtime details. It should not be copied into source.
- Whether a dependency manifest exists elsewhere or needs to be reconstructed.
- Whether the service has a systemd unit file outside the live tree that should
  be documented but not copied into the app repo.

## Recommended Include/Exclude Policy for Later Copy Step

Recommended initial copy posture:

- Include only reviewed source/control files:
  - `app.py`
  - `.gitignore`
  - `.cgcignore`
- Include `config.json` for a private homelab source candidate based on the
  completed safe review; sanitize it before any public publication.
- Do not include `.git/` from the live runtime directory.
- Do not include `dispatch.log`.
- Do not include timestamped `.bak` files.
- Do not include secrets, keys, tokens, `.env`, logs, databases, caches,
  virtualenvs, generated runtime files, or request logs.
- Add source-repo docs and tests in Strix after the initial copy, not in the
  live runtime directory.

Suggested later copy include list after approval:

```text
app.py
config.json for private homelab source candidate; sanitize before public release
.gitignore
.cgcignore
```

Suggested later copy excludes:

```text
.git/
*.bak
*.log
.env
*.env
*secret*
*token*
*key*
*.db
*.sqlite
*.sqlite3
__pycache__/
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
node_modules/
```

## Next Recommended Operator Approval Brief

Decision requested:
Approve or reject creating a Strix source repo candidate for `model-dispatch`
from a reviewed subset of `thinkcentre:/srv/model-dispatch`.

Available options:

- Option A: Create `strix:/srv/projects/model-dispatch` from the reviewed include
  list only: `app.py`, `.gitignore`, `.cgcignore`, and `config.json` only if the
  user confirms it is safe. Exclude `.git/`, logs, backups, secrets, caches,
  virtualenvs, generated files, and runtime databases. This best matches Slice 1.
- Option B: Stop and manually review `config.json` and `app.py` first before any
  copy. This is safest if there is uncertainty about embedded secrets.
- Option C: Copy the full live directory. This risks committing logs, backups,
  runtime metadata, or existing live Git metadata and should be rejected.
- Option D: Deploy from the new repo immediately. This changes live behavior and
  should be rejected for this slice.

Recommended option:
Option B if `config.json` has not been manually reviewed for secrets. Otherwise
Option A with the narrow include/exclude policy above.

What could break if the wrong option is chosen:

- Secrets, request logs, or runtime data could be committed.
- Existing live Git metadata could be mistaken for canonical source history.
- Open WebUI could be disrupted if repo creation is confused with deployment.
- Rollback could become unclear if live runtime and source ownership are mixed.

Exact next prompt to continue safely:

```text
Proceed with creating a Strix source repo candidate for model-dispatch from the
reviewed include list only. Do not deploy, restart services, edit
/srv/model-dispatch, create the ThinkCentre mirror, or change Open WebUI. Exclude
.git, logs, backups, secrets, caches, virtualenvs, generated runtime files, and
runtime databases. If config.json has not been reviewed safe, stop and request
operator review before copying it.
```
