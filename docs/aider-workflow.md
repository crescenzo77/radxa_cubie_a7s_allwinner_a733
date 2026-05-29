# Aider Workflow

## Purpose

Aider is the preferred bounded patch executor for planned strict slices. Use it
for small repository edits after the slice is already planned.

Its job is to execute the coding/editing action and produce one narrow,
reviewable Git diff. It is not the planner, operator, deployment tool, service
controller, or architecture reviewer.

## When To Use Aider

Use Aider when all of these are true:

- The active slice is already written in `CURRENT_SLICE.md`.
- The files or areas in scope are clear.
- The change is local to one repository.
- The desired output is one bounded edit.
- The result can be reviewed with normal Git diff.
- The rollback path is simple: reject or revert the diff.

Good Aider tasks include:

- Small documentation updates.
- Focused test additions.
- Narrow bug fixes.
- Mechanical edits where the intended files are known.
- Tight refactors inside one module or document set.

## When Not To Use Aider

Do not use Aider for:

- Planning a slice.
- Architecture decisions.
- Live deployment.
- Service restarts or reloads.
- Docker, systemd, reverse proxy, or production config changes.
- Secrets, tokens, credentials, or `.env` changes.
- Multi-host changes.
- Broad repo rewrites.
- Autonomous follow-up work.
- Anything requiring user approval before the next command.

Use Codex Desktop or another selected planner surface for planning, sequencing,
approval briefs, and risky live-service steps. Use Aider for the bounded patch
execution step when the slice is already planned and the target files are clear.
OpenCode is currently blocked for local model patching and must not replace
Aider until a separate validation slice fixes and proves it. Keep Continue.dev
as editor assist and Cline sandbox-only.

For the full provider-neutral patch/review loop, see
`docs/patch-review-workflow.md`.

## Standard Aider Workflow

1. Read the active repo instructions and slice files:
   `AGENTS.md`, `CODEX_CONTEXT.md`, `CURRENT_SLICE.md`, `AGENT_STATUS.md`,
   `PROJECT_PLAN.md`, and `DECISIONS.md`.
2. Confirm the edit is one repo, one bounded task, and one reviewable diff.
3. Start Aider from the repository working tree.
4. Give Aider a narrow prompt with:
   - the active slice name
   - exact files or areas in scope
   - files and actions out of scope
   - required checks
   - instruction to avoid commits
5. Review the resulting diff manually.
6. Run the slice checks.
7. Update `AGENT_STATUS.md` with the handoff.
8. Stop for user review unless the user explicitly requested another bounded
   edit.

## Validation Checklist

Before accepting Aider output:

- `git status --short` shows only expected files.
- `git diff --check` passes.
- `git diff --stat` is narrow enough for the slice.
- The diff does not include unrelated formatting or churn.
- Required tests or checks were run, or marked unavailable with a reason.
- `AGENT_STATUS.md` records what changed, what did not change, files changed,
  checks run, results, risks, blockers, approval needs, and next action.
- No live service, secret, Docker, systemd, multi-host, or architecture change
  was made by Aider.

## Commit Guidance

Do not let Aider commit by default.

The user reviews the diff first. After review, commit manually with a concise
message that names the slice. If the Aider diff is wrong, reject it or revert it
with normal Git tools instead of asking Aider to broaden the task.

## Review Coach Boundary

Aider is only the patch assistant. A separate reviewer must inspect the diff
before commit.

Reviewer options include Codex desktop, ChatGPT, Open WebUI with a local model,
OpenCode in review-only mode, Claude Code, or another explicit reviewer chosen
by the user.

The reviewer checks:

- `git status --short`
- `git diff --check`
- `git diff --stat`
- the actual diff

The reviewer ends with one of:

- Commit
- Revise
- Revert
- Inspect more

## Direct vLLM Trial Note

- Use one file only.
- Confirm the direct vLLM endpoint works before launching Aider.
- Decline requests to add unrelated context files.
- Review the diff before committing.
- Reject the run if Aider edits unrelated files.

## Validated Local Code-Test Trial

The first passing local Aider trial used the Strix Coder-Next vLLM runtime
through model-dispatch:

```sh
scripts/strix-vllm-mode code
```

Then Aider ran in a throwaway repo with:

```sh
/home/enzo/.local/bin/aider README.md \
  --model openai/local/code-test \
  --openai-api-base http://192.168.50.225:4010/v1 \
  --openai-api-key dummy \
  --edit-format diff \
  --no-stream \
  --map-tokens 0 \
  --no-auto-commits \
  --no-gitignore \
  --yes-always \
  --message "Edit README.md only. Replace the line old line with the exact text: aider local code test passed. Do not change the heading."
```

Result:

- Aider `0.86.2` edited only the requested file.
- It received output tokens and exited `0`.
- The test repo diff changed only the target line.
- Strix was restored with `scripts/strix-vllm-mode tool` afterward.

Keep this as a minimal compatibility proof, not a default workflow. The
existing `aider-strix-coder` launcher still points at the older `8082`
llama.cpp/GGUF path and is not the validated vLLM Coder-Next path.

## First Real Non-Critical Repo Trial

The first real non-critical repo trial used the same Coder-Next path against
`/srv/projects/cubie-camera-node`.

Task:

- Edit `README.md` only.
- Add a short `Next safe step` section.
- Point the next work at `docs/hardware-readiness-checklist.md`.
- Do not change deployment state or any other file.

Result:

- Aider edited only `README.md`.
- The diff was one file and four inserted lines.
- Generated Aider history files were removed before commit.
- `git diff --check` passed.
- Commit: `3af1c05 document next hardware readiness step`
- Push to `thinkcentre:/srv/git/cubie-camera-node.git` succeeded.
- Strix was restored to `tool` mode and `local/tool-test` passed afterward.

Keep this as a bounded proof of Aider's patch-executor role. It promotes Aider
only for planned strict slices with clear file scope; it does not promote Aider
to planning, service edits, broad repo-map use, auto-commits, or autonomous
follow-up work.

## Validated Strix llama.cpp Coder-Next Trial

After returning Strix to the llama.cpp/GGUF multi-model harness, Aider passed a
bounded one-file edit through the restored Coder-Next endpoint:

```sh
/home/enzo/.local/bin/aider README.md \
  --model openai/Qwen3-Coder-Next-UD-Q4_K_XL.gguf \
  --openai-api-base http://127.0.0.1:8082/v1 \
  --openai-api-key dummy \
  --edit-format diff \
  --no-stream \
  --map-tokens 0 \
  --no-auto-commits \
  --no-gitignore \
  --yes-always \
  --message "Edit README.md only. Make one narrow requested edit."
```

Result:

- Endpoint: Strix `qwen3-coder` on `127.0.0.1:8082`.
- Model: `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`.
- Repo: `/srv/projects/cubie-camera-node`.
- Aider edited only `README.md`.
- Generated Aider history files were removed before commit.
- `git diff --check` passed.
- Commit: `8de720a clarify next hardware checklist step`.
- Push to `thinkcentre:/srv/git/cubie-camera-node.git` succeeded.

Repeatable helper:

```sh
scripts/aider-strix-coder-llamacpp README.md --message "Make one narrow requested edit."
```

Run the helper from the target repository working tree. It refuses to run unless
Strix Coder-Next is live on `127.0.0.1:8082`.

Keep this as a bounded proof of Aider's patch-executor role. It promotes Aider
only for planned strict slices with clear file scope; it does not promote Aider
to planning, service edits, broad repo-map use, auto-commits, or autonomous
follow-up work.

## Repeatable Helper

Use this helper for the validated Coder-Next path after switching Strix to code
mode:

```sh
cd /srv/projects/homelab
scripts/strix-vllm-mode code
scripts/aider-code-test README.md --message "Make one narrow requested edit."
```

The helper refuses to start unless `qwen3-coder-next-awq-agent-test` is active
on `127.0.0.1:8010`. It sets the validated local model, model-dispatch base URL,
diff edit format, non-streaming mode, disabled repo map, disabled auto-commits,
and disabled gitignore changes.

It does not pass `--yes-always` by default. Add that flag explicitly only for a
known throwaway or otherwise tightly bounded non-interactive trial.
