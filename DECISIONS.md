# Decisions

## 2026-05-29 — Use Aider as preferred bounded patch executor

Decision:
Use Aider as the preferred bounded patch executor for planned strict slices.
Aider is the tool chosen to perform the coding/editing action while staying
behind the slice boundary and not crossing into planning.

Policy:

- The planner defines the slice, scope, files, checks, and stop condition before
  Aider runs.
- Aider executes the bounded patch and stops after one reviewable diff.
- Aider must not plan, broaden scope, auto-commit, deploy, change services, or
  become autonomous.
- OpenCode remains blocked for local model patching and must not be treated as
  the next preferred patch tool until separately fixed and validated.

Rationale:
The user was instructed to use Aider because it best matches the desired role
separation: it can perform the coding action for each strict slice while the
planner and reviewer remain separate roles.

## 2026-05-29 — Preserve plans with canonical plan index

Decision:
Use `PLAN_INDEX.md` as the canonical registry for current, superseded,
archived, and quarantined workflow plans. Do not delete old workflow, plan,
history, or draft files when a new plan is created.

Current active plan:

- `docs/provider-neutral-adhd-workflow.md`

Protected long-context master history/evolution file:

- `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md`

Policy:

- Mark exactly one operating plan as `Current` unless the user explicitly wants
  multiple active plans for different projects.
- Preserve old plans by marking them `Superseded`, `Archived`, or `Quarantined`.
- Use `docs/archive/` for useful old plans and drafts.
- Use `docs/quarantine/` only for misleading or unsafe plans that should not be
  followed without explicit review.
- Record replacements and reasons in `PLAN_INDEX.md` in the same diff as the new
  plan.
- Never delete the protected long-context master history/evolution file.

Rationale:
The user wants to create new plans without losing the progression of discussion,
decisions, and prior directions. A registry preserves history while making the
current plan unmistakable for future agents.

## 2026-05-28 — Aider passes tiny code edit through AMD local coder

Decision:
Treat AMD `local/amd-coder` as validated for one tiny bounded Aider code edit,
while keeping Aider evaluation-only.

Validated path:

- Endpoint: `http://192.168.50.225:4010/v1`
- model-dispatch alias: `local/amd-coder`
- Container: `qwen3-coder-30b`
- Harness: llama.cpp CUDA
- Model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- Aider model: `openai/local/amd-coder`
- Repo edited: `/srv/projects/cubie-camera-node`
- File created: `scripts/cubie-node-summary`
- Commit: `d6246ef add Cubie node summary helper`

Rationale:
This extends the AMD validation from a one-line documentation edit to a tiny
real code-file edit with syntax and runtime checks, without changing services
or deployment state.

Boundaries:

- This validates only one tiny one-file shell-script edit.
- It does not validate multi-file code edits, tests, service edits, or
  autonomous coding workflows.
- Aider remains a bounded patch tool, not a planner or default autonomous
  coder.

## 2026-05-28 — OpenCode local provider path remains blocked

Decision:
Keep OpenCode out of the normal patch workflow. The local model provider path
is installed and configurable, but it still does not produce usable model output
or edits through `opencode run`.

New findings:

- Adding explicit AMD model limits removed the earlier context-size rejection.
- OpenCode still produced no edit through AMD `local/amd-coder`.
- Plain OpenCode chat through AMD and Strix emitted only step start/finish
  events with zero recorded model tokens.
- Direct model-dispatch tool-loop smoke passed for both `local/amd-coder` and
  `local/strix-coder`.

Conclusion:
The blocker is specific to OpenCode's local provider/run path, not to the
llama.cpp coder backends or model-dispatch OpenAI-style tool-call support.

Policy:

- Do not use OpenCode as the patch tool yet.
- Do not change model-dispatch, Open WebUI, Docker, systemd, or routing to make
  OpenCode work.
- Use Aider as the currently validated bounded patch-tool path.
- Treat any further OpenCode work as a separate debugging slice.

## 2026-05-28 — OpenCode local-model preflight is partial, not validated

Decision:
Treat OpenCode as installed on Strix but not yet validated as a working local
patch tool.

Validated facts:

- OpenCode version `1.15.12` is installed on Strix at
  `/home/enzo/.local/npm-global/bin/opencode`.
- A project-local OpenCode config can use `@ai-sdk/openai-compatible` against
  model-dispatch at `http://192.168.50.225:4010/v1`.
- OpenCode can list configured local models from that config.

Trial results:

- AMD `local/amd-coder` failed before editing because OpenCode's build-agent
  request exceeded the AMD model's advertised context.
- Strix `local/strix-coder` exited without editing, with zero recorded model
  tokens and no tool calls in the exported OpenCode session.

Policy:

- Do not promote OpenCode into the normal workflow yet.
- Do not change model-dispatch or Open WebUI defaults for OpenCode.
- Do not switch Strix runtimes for OpenCode testing unless explicitly selected.
- Keep Aider as the currently validated bounded patch-tool path.

## 2026-05-28 — Aider passes bounded edit through AMD local coder

Decision:
Treat AMD `local/amd-coder` as validated for one tiny bounded Aider
documentation edit, while keeping Aider evaluation-only.

Validated path:

- Endpoint: `http://192.168.50.225:4010/v1`
- model-dispatch alias: `local/amd-coder`
- Container: `qwen3-coder-30b`
- Harness: llama.cpp CUDA
- Model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- Aider model: `openai/local/amd-coder`
- Repo edited: `/srv/projects/cubie-camera-node`
- Commit: `cd4b5a1 validate AMD coder bounded patch`

Rationale:
This proves the RTX 3090 AMD lane can participate in the same bounded
patch-review workflow as the Strix Coder-Next path, through model-dispatch and
without changing service defaults.

Boundaries:

- This validates only one tiny one-file documentation edit.
- It does not validate broad repo maps, multi-file edits, service edits, or
  autonomous coding workflows.
- Aider remains evaluation-only until broader checks are deliberately selected.
- No model-dispatch, Open WebUI, Docker, or systemd changes were made.

## 2026-05-28 — Use provider-neutral patch-review workflow

Decision:
Use a provider-neutral patch-review workflow for coding-agent trials.

Workflow:

- Planner/advisor writes a bounded prompt.
- Patch tool makes one reviewable Git diff.
- Reviewer / Review Coach inspects the diff.
- User decides Commit, Revise, Revert, or Inspect more.

Reviewer options include Codex desktop, ChatGPT, Open WebUI with a local model,
OpenCode in review-only mode, Claude Code, or another explicit reviewer chosen
by the user. The reviewer role is not tied to one provider.

Patch tool options include Aider for strict named-file edits, Codex when
explicitly selected, and OpenCode as the preferred next local-model coding-agent
candidate to evaluate.

Policy:

- Aider remains conditionally allowed only as a bounded patch assistant, not as
  a general autonomous coder.
- Local models can review diffs through Open WebUI without needing a coding
  agent.
- Local models need a coding harness only when they are expected to edit files.
- Running Codex on Strix with a local model is not proven in this homelab and
  remains a separate investigation.
- Commit only after proof and user approval.

## 2026-05-28 — Aider passes bounded edit through Strix llama.cpp Coder-Next

Decision:
Treat the restored Strix llama.cpp/GGUF Coder-Next endpoint as validated for
one tiny bounded Aider documentation edit, while keeping Aider evaluation-only.

Validated path:

- Endpoint: `http://127.0.0.1:8082/v1`
- Container: `qwen3-coder`
- Harness: llama.cpp Vulkan
- Model: `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`
- Aider model: `openai/Qwen3-Coder-Next-UD-Q4_K_XL.gguf`
- Repo edited: `/srv/projects/cubie-camera-node`
- Commit: `8de720a clarify next hardware checklist step`

Rationale:
This gives Strix an always-live Coder-Next Aider path without returning to the
memory-heavy concurrent vLLM setup. It fits the restored four-model local menu:
Strix handles long-context llama.cpp/GGUF models, AMD handles fast agentic work
and experiments.

Boundaries:

- This validates only one tiny one-file documentation edit.
- It does not validate broad repo maps, multi-file edits, service edits, or
  autonomous coding workflows.
- Aider remains evaluation-only until broader checks are deliberately selected.

## 2026-05-28 — Return Strix default to llama.cpp GGUF multi-model harness

Decision:
Use the former llama.cpp/GGUF Strix pair as the default always-live Strix model
arrangement, and use AMD for fast agentic coding plus experimental models.

Current intended roles:

- Strix `qwen3-6` / `local/strix-reasoning`: Qwen3.6 GGUF on llama.cpp
  Vulkan for long-context reasoning and review.
- Strix `qwen3-coder` / `local/strix-coder`: Qwen3-Coder-Next GGUF on
  llama.cpp Vulkan as the always-live local code model candidate.
- AMD `qwen3-coder-30b` / `local/amd-coder`: RTX 3090 fast agentic coding
  workhorse.
- AMD `gemma4-7900xt` / `local/amd-small`: RX 7900 XT backup and experimental
  lane.

Rationale:
The vLLM Qwen3.6 AWQ harness is validated for clean tool-call behavior, but it
reserves enough memory that concurrent large vLLM serving on Strix is not safe
in the tested shape. The llama.cpp/GGUF pair fits Strix's strength better:
large unified memory and multiple local models live at once.

Boundaries:

- Do not remove the vLLM Qwen3.6 AWQ runtime; keep it as a validated reference
  tool-call harness.
- Do not assume llama.cpp/GGUF Coder-Next is Aider-compatible until revalidated.
- Do not treat `local/amd-small` as a clean agent model until its thinking
  output behavior is controlled.
- Do not plan local Qwen 3.7 testing until official open weights or a concrete
  compatible quant are available.

## 2026-05-28 — Aider passes first real bounded non-critical repo edit

Decision:
Treat Aider as validated for one real bounded documentation edit in a
non-critical repo through `local/code-test`, but keep it evaluation-only and
off the core workflow.

Validated path:

- Repo: `/srv/projects/cubie-camera-node`
- Target file: `README.md`
- Commit: `3af1c05 document next hardware readiness step`
- Mirror push: `thinkcentre:/srv/git/cubie-camera-node.git`
- Strix mode before and after: restored to `tool`
- Aider path: `scripts/aider-code-test`
- Model: `openai/local/code-test`
- API base: `http://192.168.50.225:4010/v1`
- Edit format: `diff`
- Non-streaming request
- Repo map disabled with `--map-tokens 0`
- Auto-commits disabled

Validation passed:

- `scripts/strix-vllm-mode code` completed.
- `scripts/model-tool-loop-smoke --model local/code-test` passed before Aider.
- Aider edited only `README.md`.
- Generated Aider history files were removed before commit.
- `git diff --check` passed.
- The committed diff was one file and four inserted lines.
- Push to the ThinkCentre mirror succeeded.
- `scripts/strix-vllm-mode tool` restored the Qwen3.6 baseline.
- `scripts/model-tool-loop-smoke --model local/tool-test` passed after restore.

Important boundaries:

- This validates only a tiny, explicit, one-file documentation edit in a
  non-critical repo.
- This does not validate broad repo maps, long context, multi-file edits,
  auto-commits, service edits, deployment work, or autonomous coding workflows.
- Aider remains evaluation-only.
- Do not use Aider on long control/history docs in the homelab repo.
- Do not promote Aider into the default walking skeleton without a separate
  explicit decision.

Rationale:
The throwaway test proved local Aider compatibility. This real repo trial proves
the same path can produce a small reviewable diff in a non-critical project
while preserving the required manual review, commit, push, and Strix restore
steps.

## 2026-05-28 — Aider passes bounded edit through local/code-test

Decision:
Treat Aider as validated for one narrow throwaway edit through `local/code-test` while the Strix Coder-Next runtime is active, but do not make it a default workflow yet.

Validated path:

- `scripts/strix-vllm-mode code`
- model-dispatch alias `local/code-test`
- served model `qwen3-coder-next-awq-agent-test`
- Aider `0.86.2`
- model argument `openai/local/code-test`
- API base `http://192.168.50.225:4010/v1`
- edit format `diff`
- non-streaming request
- repo map disabled with `--map-tokens 0`
- throwaway repo under `/tmp`

Validation passed:

- Coder-Next mode switch completed.
- `scripts/model-tool-loop-smoke --model local/code-test` passed before the Aider run.
- Aider edited only `README.md` in the throwaway repo.
- Aider received output tokens and exited `0`.
- The resulting diff changed only `old line` to `aider local code test passed`.
- The restore trap switched Strix back to `tool` mode.
- `scripts/model-tool-loop-smoke --model local/tool-test` passed after restore.

Important boundaries:

- This validates only a tiny, explicit, one-file edit.
- This does not validate Aider in the homelab repo.
- This does not validate broad repo-map behavior, auto-commits, long context, multi-file edits, or autonomous coding-agent workflows.
- Keep Aider off default workflows until a real bounded slice passes review in a non-critical repo.
- The old `aider-strix-coder` launcher still points at `127.0.0.1:8082` and the GGUF/llama.cpp path; it is not the validated vLLM Coder-Next path.

Rationale:
The earlier Aider failure against Qwen3.6 showed that coding-agent protocol compatibility must be tested separately from the OpenAI tool-call loop. This result proves that the Coder-Next vLLM path can support a minimal Aider edit when configured directly and narrowly.

## 2026-05-28 — Strix Qwen3-Coder-Next AWQ test runtime preserved

Decision:
Keep `cyankiwi/Qwen3-Coder-Next-AWQ-4bit` as a validated Strix vLLM code/tool test runtime, but do not make it persistent or automatic yet.

Validated path while the Coder-Next runtime is active:

- Strix runs `docker.io/kyuz0/vllm-therock-gfx1151:stable`.
- Served model name: `qwen3-coder-next-awq-agent-test`.
- vLLM listens on Strix port `8010`.
- model-dispatch exposes explicit backend alias:
  - `local/strix-qwen3-coder-next-awq-agent`
- model-dispatch exposes stable test role alias:
  - `local/code-test`
- `scripts/model-tool-loop-smoke --model local/code-test` passed.

Validation passed:

- Direct Strix vLLM `/v1/models`.
- Direct Strix vLLM normal chat.
- Direct Strix vLLM OpenAI-style `tool_calls`.
- Direct Strix vLLM multi-turn tool-result follow-up.
- model-dispatch direct chat through `local/code-test`.
- model-dispatch OpenAI-style tool call through `local/code-test`.
- Repeatable smoke test through `scripts/model-tool-loop-smoke --model local/code-test`.

Important boundaries:

- This runtime uses the same Strix port, `8010`, as the Qwen3.6 AWQ runtime.
- Only one of `local/tool-test` or `local/code-test` can work at a time with the current one-port Strix setup.
- When Qwen3.6 AWQ is active, `local/tool-test` works and `local/code-test` fails because the Coder-Next served model is absent.
- When Coder-Next AWQ is active, `local/code-test` works and `local/tool-test` fails because the Qwen3.6 served model is absent.
- Do not add `local/code-test` to auto routes or defaults until the runtime switching or port strategy is explicitly selected and revalidated.

Related negative result:
`Qwen/Qwen2.5-Coder-7B-Instruct` passed normal chat under vLLM but did not produce OpenAI-style `tool_calls` with the tested parser setup. Do not use that model for the current tool-call contract.

Rationale:
Coder-Next is the first validated local coder-oriented model for the same OpenAI-style tool-call surface, but it is still a manual test runtime. The current stable baseline remains Qwen3.6 AWQ on `local/tool-test` until runtime switching or concurrent serving is deliberately designed.

## 2026-05-26 — Strix Qwen3.6 AWQ vLLM tool-loop validation

Decision:
Treat Strix vLLM with `cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit` as the first validated local model/harness candidate for agent-facing tool-loop behavior.

Validated path:

- Strix runs `docker.io/kyuz0/vllm-therock-gfx1151:stable`.
- Served model name: `qwen36-awq-agent-test`.
- vLLM listens on Strix port `8010`.
- model-dispatch exposes explicit backend alias:
  - `local/strix-qwen36-awq-agent`
- model-dispatch exposes stable test role alias:
  - `local/tool-test`
- `local/tool-test` routes to `local/strix-qwen36-awq-agent`.

Required launch characteristics observed during validation:

- `--skip-mm-profiling`
- `--enable-auto-tool-choice`
- `--tool-call-parser qwen3_xml`
- `--default-chat-template-kwargs '{"enable_thinking": false}'`
- `--generation-config vllm`
- `--trust-remote-code`
- `--enforce-eager`

Validation passed:

- Direct Strix vLLM `/v1/models`.
- Direct Strix vLLM normal chat.
- Direct Strix vLLM JSON-only response.
- Direct Strix vLLM OpenAI-style `tool_calls`.
- Direct Strix vLLM multi-turn tool-result follow-up.
- Remote Framework access to Strix vLLM.
- Open WebUI manual selection through model-dispatch.
- model-dispatch direct chat through `local/strix-qwen36-awq-agent`.
- model-dispatch OpenAI-style tool call through `local/strix-qwen36-awq-agent`.
- model-dispatch multi-turn tool-result follow-up.
- Repeatable smoke test committed at `scripts/model-tool-loop-smoke`.
- Stable role alias `local/tool-test` validated for chat and tool calls.

Important boundaries:

- `local/tool-test` is manual/test-only.
- Do not add this model to `auto-local`, `auto-coding-local`, `auto-reasoning-local`, `advisor`, `reasoning`, `coding`, `review`, or `small` until explicitly selected and revalidated.
- Existing llama.cpp model containers on Strix and AMD were intentionally stopped during the inference harness work.
- This is not yet a persistent service design.
- This does not prove long-context stability, production reliability, speed, or all-agent compatibility.
- Aider is not validated for this model path; Aider connected but received an empty response and made no edit.
- Continue using the repeatable smoke test before relying on the alias after restarts or model changes.

Rationale:
The main reliability goal is not only better model quality. It is consistent local model behavior across tools, skills, and agents: clean non-thinking output, predictable OpenAI-compatible response fields, valid JSON, real `tool_calls`, and clean multi-turn tool-result handling. This Strix vLLM path is the first local Qwen3.6-class setup in the homelab that passed that contract.

## 2026-05-26 — Homelab walking skeleton before broader cleanup

Decision:
Build a minimal walking skeleton for homelab cleanup and buildout before adding more tools, moving services, or expanding automation.

Rationale:
The user needs a safe, ADHD-friendly workflow that works from the Framework laptop without relying on IDE clutter, hidden automation, or broad coding-agent freedom. Recent testing showed that Aider can connect to the local Strix coder endpoint, but it is not reliable enough yet for the core skeleton. It attempted broad rewrites on long workflow/control Markdown files and had to be reverted.

Walking skeleton:
- Framework remains the user seat: browser planner plus terminal sessions.
- Strix is the normal project home for new non-GPU projects.
- The homelab repo on Strix is the first walking-skeleton project.
- Planner asks for targeted evidence instead of guessing.
- Planner gives exact commands or controlled manual edit steps.
- User runs the commands.
- Review Coach reviews diffs in layman's terms using the documented fixed format.
- User commits and pushes to the ThinkCentre mirror.

Evaluation-only for now:
- Aider.
- OpenCode.
- OpenHuman.
- CodeGraphContext write workflows.
- Autonomous reviewer/oracle loops.

Policy:
- Do not make Aider, OpenCode, OpenHuman, or CodeGraphContext write workflows required for the first skeleton.
- Do not add hidden automation, approval daemons, or automatic reviewer loops.
- Do not move services or redesign host roles as part of the walking skeleton.
- Continue to preserve old decisions as history, but let newer decisions define current operating policy.

## 2026-05-26 — Review Coach format

Decision:
Use a two-level fixed Review Coach format for reviewing coding-agent output.

Rationale:
The user needs reviews in layman's terms with predictable structure. This reduces mental load, avoids dense technical review language, and helps the user make a clear commit/revise/revert decision without needing to manually understand every line of code.

Policy:
- The Review Coach must speak in layman's terms.
- Every review must end with one of:
  - Commit
  - Revise
  - Revert
  - Inspect more
- Use the short fixed review for tiny, low-risk changes.
- Use the full fixed review for anything involving code, services, configs, multiple files, databases, storage, Docker, systemd, routing, or unclear scope.

Short review format:
- Changed:
- Scope:
- Risk:
- Recommendation:

Full review format:
- What changed:
- Scope check:
- Risk:
- Proof:
- What to inspect:
- Recommendation:

## 2026-05-26 — Strix-local Aider launcher validated but restricted

Decision:
Use `/home/enzo/.local/bin/aider-strix-coder` as the approved Strix-local Aider launcher for bounded, named-file edits only.

Rationale:
The launcher successfully used the local Strix coder endpoint at `http://127.0.0.1:8082/v1` with model `openai/Qwen3-Coder-Next-UD-Q4_K_XL.gguf`, avoided the OpenRouter onboarding prompt, disabled auto-commits, and stored main history files outside the repo.

Aider still creates `.aider.tags.cache.v4/`, so repos approved for Aider use should ignore `.aider*`.

Aider is not currently reliable for long history/control Markdown files. A test against `DECISIONS.md` and `WORKFLOW.md` attempted broad rewrites and had to be reverted.

Policy:
- Use Aider with named files only.
- Do not run bare `aider` in homelab repos.
- Do not allow Aider auto-commits.
- Do not use Aider as planner.
- Do not use Aider yet on `DECISIONS.md`, `WORKFLOW.md`, `CURRENT_SLICE.md`, `AGENT_STATUS.md`, or `PROJECT_PLAN.md`.
- Use Aider for small isolated docs, scripts, and code patches after planner-generated prompts.
- User reviews diffs and commits manually.

## 2026-05-26 — Strix bulk storage mount

Decision:
Rename the old unused Strix `/models` mount to `/bulk` and make `/bulk` the
persistent mount for UUID `80475fbf-4c66-42d1-8f31-1492e0f14c64`.

Rationale:
The previous `/models` mount name implied an active model-runtime location, but
Strix currently uses the WD_BLACK root drive for active projects and LLM
runtime data. The SanDisk SSD is better documented as replaceable bulk storage.

Consequences:
- `/bulk` is `/dev/nvme0n1p1`, ext4, label `bulk`, on the SanDisk SSD Plus
  2TB A3N.
- `/bulk` has about 1.8T capacity and was almost empty at validation time.
- `/models` is no longer mounted, and the empty `/models` directory was
  removed.
- `/etc/fstab` now contains:

```text
UUID=80475fbf-4c66-42d1-8f31-1492e0f14c64  /bulk  ext4  defaults,nofail  0  2
```

- The change was reboot-tested successfully.
- Strix LLM containers `qwen3-6` and `qwen3-coder` came back healthy after
  reboot.
- Health checks passed for both Strix NVMe drives:
  - SanDisk `/bulk`: SMART passed, `critical_warning` 0, `media_errors` 0,
    error log entries 0, `available_spare` 100%, `percentage_used` 1%.
  - WD_BLACK root: SMART passed, `critical_warning` 0, `media_errors` 0,
    error log entries 0, `available_spare` 100%, `percentage_used` 0%.

Policy:
- `/srv/projects` on the WD_BLACK root drive remains the trusted active
  project/source home.
- `/srv/llm` on the WD_BLACK root drive remains the active Strix LLM
  runtime/model location for now.
- `/bulk` is available for replaceable bulk, cache, scratch, model downloads,
  and artifacts.
- `/bulk` must not be used for canonical source repos, sole-copy databases,
  irreplaceable scanned documents, registry primary data, or only-copy project
  history.

## 2026-05-05 — Two-surface workflow

Decision:
Use a two-surface workflow: web UI advisor/planner plus self-hosted coding agent.

Rationale:
This reduces copy/paste and context-window bloat without building a fragile autonomous approval system.

Consequences:
- The user remains the final approver.
- `advisor-packet` is only a local context packet generator.
- Markdown files and Git are the durable project state.
- Codex may be used manually during setup, but must not become infrastructure.

## 2026-05-06 — Slice 5 evaluation

Decision:
Aider is the preferred first candidate for the steady-state coder evaluation.
OpenCode remains available as a fallback.
Aider is not the final default until this bounded edit test is reviewed and accepted.
Aider must use Homelab LiteLLM, not direct paid-provider APIs.
No automation, daemon, watcher, or background job should be created around Aider.

Rationale:
Aider was tested as a candidate for the steady-state coder in the two-surface workflow.
It meets the requirements for Git-centered, terminal-based, bounded editing.
It does not pollute system Python and works inside a Git repo.
It produces reviewable diffs and respects workflow constraints.

Consequences:
- Aider is being evaluated as the first preferred coding agent.
- OpenCode remains available as a fallback.
- No automation or background processes are created around Aider.
- The final default will be determined after reviewing this bounded edit test.

## 2026-05-06 — Aider eliminated from homelab workflow

Decision:
Aider will not be used in the homelab steady-state workflow.

Rationale:
Aider installed cleanly and reached Homelab LiteLLM, but it failed a simple bounded documentation task in an unacceptable way. It created bogus files using prompt text as filenames and emptied `AGENT_STATUS.md`, one of the repo's control files. The repo had to be manually recovered.

This failure happened on a simple task, so simpler scope is not a sufficient safety control.

Consequences:
- Aider is not the default coder.
- Aider is not a fallback coder for the homelab workflow.
- Do not build wrappers, scripts, automation, or process steps around Aider.
- OpenCode through LiteLLM becomes the next coder path to evaluate and recenter around.
- The two-surface workflow remains valid: web UI advisor, OpenCode coder, `advisor-packet`, markdown state files, and Git review.

## 2026-05-06 — Transition away from LiteLLM active routing

Decision:
LiteLLM will be phased out of the active OpenCode and Open WebUI routing path.

Rationale:
The useful part of the current setup is the OpenRouter free-model discovery and free-only filtering, not LiteLLM itself. LiteLLM adds a large credential-bearing routing layer. The safer target is to preserve the free-model allowlist mechanism while generating OpenCode-safe provider config directly.

Target:
- OpenCode uses direct local-coder by default.
- OpenRouter is available only as a generated free-only manual fallback.
- Open WebUI moves back to direct local model endpoints.
- LiteLLM is kept temporarily for rollback, then removed from the active path after testing.

Consequences:
- Do not delete or stop LiteLLM yet.
- Do not remove OpenRouter fallback.
- Do not expose the broad OpenRouter paid catalog to OpenCode.
- Do not build a custom router or LiteLLM clone.
- Move free-model artifacts toward `/srv/openrouter-free/`.

## 2026-05-11 — Open WebUI model-dispatch compatibility layer

Decision:
Open WebUI uses `model-dispatch` on ThinkCentre as its active OpenAI-compatible model endpoint.

Live endpoint:

- `http://192.168.50.225:4010/v1`
- Service: `model-dispatch.service`
- Path: `/srv/model-dispatch`
- Host: `thinkcentre`

Rationale:
Open WebUI needs a stable OpenAI-compatible `/v1/models` and `/v1/chat/completions` surface that can present local-first routes, explicit local models, and verified OpenRouter-free choices without exposing the broad paid OpenRouter catalog or keeping LiteLLM in the active path.

Consequences:
- Open WebUI no longer actively routes through LiteLLM.
- LiteLLM remains rollback/history unless explicitly reactivated.
- The dispatcher exposes local auto routes: `auto-local`, `auto-coding-local`, `auto-reasoning-local`, and `auto-small-local`.
- The dispatcher exposes explicit local models for Strix reasoning, Strix coder, AMD coder, and AMD Gemma backup.
- The dispatcher exposes `openrouter-free/openrouter/auto-free-router` before specific verified free models.
- OpenRouter remains free-only, explicit/manual, and fail-closed.
- OpenCode remains direct-local on AMD and keeps its generated OpenRouter-free provider behavior separate from Open WebUI.
- Follow-up decisions remain: token-estimation improvements, LiteLLM rollback retention, whether `model-dispatch` should get its own repo, and the future Continue.dev path.

## 2026-05-12 — Defer live OpenCode CodeGraphContext MCP enablement

Decision:
Do not enable CodeGraphContext MCP in live OpenCode yet. Keep it documented as optional validated tooling.

Rationale:
OpenCode MCP compatibility has been validated through disabled-candidate, isolated-enabled, and isolated read-only sessions on AMD. However, the currently validated repos are mostly Markdown/documentation, and CodeGraphContext reports 0 functions, 0 classes, and 0 modules for them. Enabling the MCP server live would add daily tool-surface noise without a strong immediate benefit.

Consequences:
- Live OpenCode config remains unchanged.
- CodeGraphContext remains available through the documented candidate and live-enable procedure.
- Future live enablement should happen only when there is a source-code-heavy repo or a concrete workflow need.
- GitNexus remains eval-only.
- No MCP tooling is installed on Cubies.

## 2026-05-13 — CodeGraphContext write use requires sandboxing

Decision:
CodeGraphContext may evolve beyond read-only use, but write-capable use must happen only inside a disposable sandbox. CodeGraphContext may read from approved canonical project repositories, but it must not write directly to canonical working trees by default.

Valid sandboxes include Git worktrees, temporary branch checkouts, dedicated patch-proposal directories, or `/tmp` patch artifacts. Changes created in a sandbox must be promoted only through reviewed diffs, patches, manual copy, or branch review.

Rationale:
CodeGraphContext can be useful for code understanding and may become useful for patch proposal workflows, but canonical project repositories are the source of truth. Direct mutation of primary working trees by an MCP tool would blur review boundaries and could accidentally alter operational source repos, project journal repos, documentation/control repos, or future project repos.

Consequences:
- Approved canonical repositories may be indexed or read as CodeGraphContext input.
- Canonical working trees remain read-only inputs by default.
- No persistent broad mutation approval is allowed.
- No automatic MCP setup wizard may be run against primary repositories.
- The policy is path-agnostic and applies to operational source repos, project journal repos, documentation/control repos, and future project repos.
- Large videos, extracted frames, datasets, generated evidence, model outputs, and bulky review artifacts should not be duplicated into sandboxes or tracked by Git unless explicitly intended.

## 2026-05-12 — Initialize Cubie camera-node source repository

Decision:
Create the canonical `cubie-camera-node` source repository on Strix and push the initial skeleton to the ThinkCentre bare mirror.

Rationale:
Cubies should remain runtime-only appliance nodes. Source development belongs on Strix, with ThinkCentre storing the bare mirror.

Consequences:
- Canonical source repo exists at `strix:/srv/projects/cubie-camera-node`.
- ThinkCentre mirror exists at `/srv/git/cubie-camera-node.git`.
- Mirror default branch is `main`.
- Initial skeleton commit is `8fcd154 initialize cubie camera node skeleton`.
- No Cubie runtime state was changed.

## 2026-05-12 — Add Cubie camera hardware readiness checklist

Decision:
Add a hardware-first readiness checklist to the `cubie-camera-node` repository before any software deployment.

Rationale:
The cameras are old and the Cubies use microSD-backed Debian installs. Hardware, power, network, storage, and camera stream basics should be verified before building or deploying runtime services.

Consequences:
- Checklist exists at `cubie-camera-node:docs/hardware-readiness-checklist.md`.
- Cubie repo commit is `3449eba add hardware readiness checklist`.
- No Cubie runtime state was changed.
- Software deployment remains blocked until hardware readiness is reviewed.

## 2026-05-13 — Force non-streaming upstream calls in model-dispatch

Decision:
`model-dispatch` now forces `stream: false` when forwarding chat completion requests to local and OpenRouter-free upstreams.

Rationale:
Open WebUI sends streaming chat requests. The local OpenAI-compatible backends return `text/event-stream` chunks for streaming responses. `model-dispatch` is not a streaming proxy and expects one JSON response object, so it failed with `no capable model available` after trying to parse SSE output as JSON.

Consequence:
Open WebUI can continue using streaming behavior at its own API boundary, while `model-dispatch` normalizes upstream calls to non-streaming JSON. Local model routing through `auto-local` is working again.

## 2026-05-13 — Use snippet-based SearXNG web search in Open WebUI

Decision:
Open WebUI web search should use SearXNG JSON results with snippet-based retrieval by keeping `BYPASS_WEB_SEARCH_WEB_LOADER=true`. The task model should be pinned to the explicit local AMD model `amd-coder-qwen3-coder-30b-32k`, not the `auto-local` route alias.

Rationale:
SearXNG JSON search worked from inside the Open WebUI container, and Open WebUI successfully generated web-search embeddings, stored snippet results in a `web-search-*` collection, and queried those results during chat. The fragile part was Open WebUI's downstream full-page fetch path, which repeatedly failed on page loads. Snippet-based retrieval avoids that loader path while preserving working web search for both local models and OpenRouter-free models.

Consequences:
- Web search works for `auto-local` and `openrouter-free/openrouter/auto-free-router`.
- Search/query preparation is handled locally by `amd-coder-qwen3-coder-30b-32k`.
- Full-page web loading remains deferred unless a later slice shows a concrete need for it.

## 2026-05-17 — Centralize model routing and clarify host roles

Decision:
Transition toward centralized `model-dispatch` routing, Strix as the canonical
source/code-graph host, and AMD as a mode-switched compute worker.

Rationale:
Centralized `model-dispatch` routing reduces duplicated model endpoint
definitions, makes source ownership clear, frees AMD for GPU-heavy work, and
gives Open WebUI, OpenCode, Continue.dev, and scripts stable model aliases.

Consequences:
- `model-dispatch` becomes first-class infrastructure instead of an incidental
  Open WebUI compatibility layer.
- Strix becomes the primary source, development, code-graph, and reasoning host.
- AMD becomes a mode-switched GPU compute worker for coding, LoRA/training, and
  creative workloads.
- OpenCode and Continue.dev eventually move to `model-dispatch`.
- Direct AMD routing and LiteLLM remain rollback paths until their replacements
  are validated.

Non-goals:
- No hidden approval daemon.
- No paid fallback.
- No broad autonomous orchestration.
- No direct CodeGraphContext mutation of canonical repos.

## 2026-05-18 — Use Aider as bounded patch assistant

Decision:
Aider is allowed back into the homelab workflow only as a bounded repo patch
assistant for small, already-planned edits. Codex remains primary for planning,
migration choreography, approval briefs, and risky live-service work. Claude
Code remains a strong frontier-code alternative and second opinion. OpenCode is
demoted from assumed next primary agent to a later local-agent experiment.
Continue.dev remains editor assist, and Cline remains sandbox-only.

Rationale:
The previous plan over-weighted OpenCode because it fit the local
model-dispatch architecture. The user's successful workflow has mostly used
Codex, Claude, and Gemini CLI agents, while OpenCode has barely been used.
Aider better matches the desired operating style for small repo edits: narrow
diffs, Git-first work, manual review, easy rollback, and low background
complexity.

Consequences:
- Aider may be used only after a slice is planned.
- Aider use is limited to one repo, one bounded edit, and one reviewable diff.
- Aider must not be used for live deployment, service restarts, Docker/systemd,
  secrets, multi-host changes, broad architecture decisions, or approval
  decisions.
- Aider output must be validated before commit.
- Do not install Aider as part of this documentation slice.
- OpenCode remains available for later local-agent experiments, not as the
  assumed default operating agent.
- Historical Aider elimination remains preserved as prior context, not erased.

## 2026-05-23 — Consolidate Codex, Aider, vLLM, and Hermes strategy

Decision:
Use Codex as the primary manual agent for planning, sequencing, approval
briefs, documentation slices, and risky live-service work. Keep Aider as the
preferred bounded patch assistant after compatibility is validated. Treat vLLM
as the preferred candidate serving layer for local coding/reasoning models on
AMD and Strix, subject to validation. Keep Hermes limited to observing,
summarizing, reviewing, and proposing skills.

Rationale:
The workflow should follow the tools that best match task shape rather than
making OpenCode primary because it fit an earlier routing direction. Codex is
already the safest fit for high-risk sequencing and approval briefs. Aider
matches the desired bounded patch workflow if local compatibility is solved.
vLLM is the stronger candidate direction for local model serving across AMD and
Strix tests. Hermes is useful as review context, but letting it mutate repos or
operate services would blur approval and safety boundaries.

Consequences:
- OpenCode is not the assumed next primary coder; it remains a later
  local-agent experiment.
- Aider compatibility remains unresolved and must be validated before relying
  on Aider for patch workflows.
- Non-Codex agentic work must use local LLMs or verified OpenRouter-free models
  only.
- Qwen thinking-off or non-thinking mode is the baseline for Aider patch
  workflow testing.
- Reasoning-parser mode is tested separately for complex review and
  architecture work.
- vLLM validation on AMD and Strix requires future explicit slices and operator
  approval before live service changes.
- Hermes must not edit canonical repositories, install live skills, restart
  services, change routing, supervise failures autonomously, or become an
  approval daemon.
