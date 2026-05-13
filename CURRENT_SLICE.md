# Current Slice

## Slice 22: Create Cubie camera node deploy skeleton

Create the initial repository skeleton for `cubie-camera-node` on Strix without deploying anything to Cubies yet.

## Purpose

Prepare a clean, Git-tracked project structure for future Cubie camera-node work while preserving the rule that Cubies are runtime-only appliance nodes.

The Cubies should not receive MCP tooling, coding agents, code graph tools, or source-development state.

## Current State

The MCP/OpenCode CodeGraphContext slice is complete:

- CodeGraphContext OpenCode adapter template documented.
- Codex rollback procedure documented.
- OpenCode isolated MCP validation succeeded on AMD.
- Live OpenCode MCP enablement was deferred.
- Decision recorded in `DECISIONS.md`.
- ThinkCentre homelab mirror is current.

Latest relevant homelab commit:

- `b04f175 defer live opencode codegraphcontext enablement`

## Scope

Documentation and repo skeleton only:

- Confirm or create `strix:/srv/projects/cubie-camera-node`
- Create basic project files if missing:
  - `README.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENTS.md`
  - `deploy/`
  - `configs/`
  - `scripts/`
- Confirm ThinkCentre bare mirror exists:
  - `/srv/git/cubie-camera-node.git`
- Do not deploy to Cubies yet.

## Constraints

- Do not install anything on Cubies during this slice.
- Do not run workload services on Cubies yet.
- Do not add MCP tooling to Cubies.
- Do not create hidden daemons or auto-deploy jobs.
- Use Git for source movement.
- Keep Strix as canonical source host for this project.
- Keep ThinkCentre as bare mirror only.

## Acceptance Criteria

- Cubie camera-node repo skeleton exists on Strix.
- The repo clearly documents Cubies as runtime-only targets.
- ThinkCentre mirror is confirmed or created.
- No Cubie runtime state is changed.
- Git diff is reviewed before commit.
