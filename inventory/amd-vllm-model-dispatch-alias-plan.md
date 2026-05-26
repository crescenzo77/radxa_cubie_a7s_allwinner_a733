# AMD vLLM model-dispatch Alias Plan

## Purpose

Plan whether and how to add a dedicated `model-dispatch` alias for the proven
temporary AMD vLLM endpoint without implementing it yet.

This plan is intentionally conservative. The direct vLLM endpoint works, and
Aider can use it, but the runtime is temporary, RTX 3090 ownership is
mode-switched, and Open WebUI should not be taught that this endpoint is always
available.

## Current Proven Facts

- Latest homelab commit before this slice:
  `8d79196 document second direct aider vllm trial`.
- AMD vLLM with `Qwen2.5-Coder-7B-Instruct` works directly on port `18000`.
- Direct endpoint used:
  `http://192.168.50.252:18000/v1`
- Served model:
  `amd-vllm-temp-qwen2.5-coder-7b`
- Aider model string used:
  `openai/amd-vllm-temp-qwen2.5-coder-7b`
- Aider succeeded twice against the direct vLLM endpoint.
- Both Aider trials were bounded one-file docs edits.
- Aider still asks to add context/control files, but respects declined
  additions.
- `qwen3-coder-30b` was restored healthy on port `8083` after each test.
- `gemma4-7900xt` stayed healthy on port `8084`.
- `model-dispatch` and Open WebUI were not changed.
- vLLM is not currently persistent.
- vLLM owns the RTX 3090 while running.
- `qwen3-coder-30b` must be stopped while vLLM owns the RTX 3090.

## Why No Live Alias Should Be Added Yet

Do not add a live `model-dispatch` alias yet.

The direct endpoint is proven, but it is not a stable service contract. The
vLLM runtime is temporary, has no persistent start/stop procedure in this repo,
and requires taking the RTX 3090 away from the current `qwen3-coder-30b`
llama.cpp service.

Adding an alias now would create a misleading registry entry. Clients could see
an apparently available model even when vLLM is stopped and port `18000` is
closed. If that alias were added to an automatic route, Open WebUI or other
clients could route normal work into a mode that requires manual GPU switching.

The safer interpretation is:

- Direct vLLM is proven for temporary Aider trials.
- `model-dispatch` integration is not yet proven for this endpoint.
- Availability is manual and conditional, not always-on.
- Runtime repeatability should be solved before the alias becomes a normal
  routing option.

## Temporary/Manual-Only Alias Recommendation

If an alias is later added, make it explicit and manual-only.

Recommended properties:

- It should be a named explicit model, not part of `auto-local`,
  `auto-coding-local`, `auto-reasoning-local`, or `auto-small-local`.
- Its name should signal that it is temporary or manual.
- Its route should point only to the proven vLLM endpoint and served model.
- Documentation should state that it is available only while the operator has
  started vLLM and stopped `qwen3-coder-30b`.
- It should not be advertised as a default coding model.
- It should not become an automatic fallback.

The alias should exist only after a repeatable temporary vLLM start/stop
procedure exists or after the operator explicitly accepts the manual runtime
dependency.

## Alias Naming Options

Preferred names:

- `local/amd-vllm-qwen2.5-coder-7b-temp`
- `manual/amd-vllm-qwen2.5-coder-7b`
- `aider/amd-vllm-qwen2.5-coder-7b`

Acceptable but less explicit:

- `amd-vllm-qwen2.5-coder-7b`
- `local/amd-vllm-coder`

Avoid:

- `coding`
- `auto-coding-local`
- `auto-local`
- `amd-coder`
- Any name that hides the temporary/manual runtime requirement.

Best current option:

```text
local/amd-vllm-qwen2.5-coder-7b-temp
```

Rationale:

- `local/` matches existing explicit local model style.
- `amd-vllm` identifies the serving mode.
- `qwen2.5-coder-7b` identifies the model family and size.
- `temp` prevents readers from assuming always-on availability.

## Should Aider Stay Direct-To-vLLM For Now?

Yes.

Keep Aider direct-to-vLLM for one more practical one-file patch or until vLLM
runtime mode is made repeatable.

Reasons:

- Direct Aider-to-vLLM already succeeded twice.
- The earlier Aider empty-response failure was tied to the previous local
  alias/model-dispatch path, not to direct vLLM.
- Adding `model-dispatch` now would add a routing variable before runtime
  repeatability is solved.
- Aider still asks to add context/control files, so the next meaningful test is
  bounded behavior on a practical patch, not routing complexity.

The next Aider test, if needed, should remain:

- one repo
- one file
- one practical docs or code-adjacent patch
- direct base URL `http://192.168.50.252:18000/v1`
- model `openai/amd-vllm-temp-qwen2.5-coder-7b`
- no commit by Aider
- extra file requests declined

## RTX 3090 Ownership Conflict

Treat AMD RTX 3090 as mode-switched:

```text
Either qwen3-coder-30b llama.cpp on 8083
or vLLM on 18000,
not both.
```

The operating rule should be:

- Normal mode: `qwen3-coder-30b` owns RTX 3090 and serves port `8083`.
- Temporary vLLM mode: stop `qwen3-coder-30b`, start vLLM on port `18000`, run
  the bounded test, stop vLLM, restore `qwen3-coder-30b`, then verify `8083`.
- `gemma4-7900xt` on port `8084` should remain independent and healthy.

Do not encode a `model-dispatch` route that assumes both RTX 3090-backed
services are available at the same time.

## Why qwen3-coder-30b And vLLM Should Not Both Be Assumed Available

Both services compete for the same RTX 3090 VRAM.

The successful vLLM tests required stopping `qwen3-coder-30b` first. After
each test, vLLM was stopped and `qwen3-coder-30b` was restored. That proves a
manual mode switch, not concurrent service availability.

Assuming both are available would create false routing expectations:

- `model-dispatch` might advertise two AMD coder paths while only one can run.
- Open WebUI could present both models as selectable.
- `auto-coding-local` could route to a stopped backend.
- Operators could misdiagnose expected mode-switch downtime as a service
  failure.

Until there is a persistent vLLM runtime plan or a deliberate scheduler, the
dispatcher should treat vLLM as manual-only.

## model-dispatch Risks

- A live alias could advertise a stopped endpoint.
- Automatic routes could select vLLM when the RTX 3090 is in llama.cpp mode.
- Existing local aliases could become ambiguous if `amd-coder` or `coding`
  names are reused.
- Health and retry behavior may not clearly distinguish "manual backend not
  running" from "broken backend."
- Streaming and non-streaming behavior should be checked through
  `model-dispatch` before Aider depends on the alias.
- Source/config shape should be inspected read-only before proposing an exact
  patch.

## Open WebUI Risks

- Open WebUI may show the alias as a normal available model even when vLLM is
  stopped.
- Routing `auto-local` or `auto-coding-local` to vLLM would hide the manual GPU
  mode switch from users.
- Users could select the vLLM alias during normal advisor use and get failures
  while `qwen3-coder-30b` is running.
- If Open WebUI caches model lists or user selections, a temporary backend
  could produce confusing stale choices.
- Open WebUI should not be the first client to validate this route. Curl and
  Aider-specific checks should come first.

## Aider Risks

- Aider still asks to add context/control files when they are mentioned.
- Aider respected declined additions in both direct vLLM trials, but this must
  remain an explicit operator behavior.
- Aider through `model-dispatch` is not proven even though direct Aider-to-vLLM
  is proven.
- An alias could change the model string, request shape, response shape,
  timeout behavior, or streaming behavior enough to reintroduce empty-response
  failures.
- Aider should not be used for live-service changes, routing edits, broad
  refactors, or commits.

## Exact Go/No-Go Criteria Before Implementation

Go only if all are true:

- A repeatable temporary vLLM start/stop procedure exists, or the operator
  explicitly accepts a manual-only alias whose backend is often stopped.
- The procedure states that `qwen3-coder-30b` on `8083` and vLLM on `18000` are
  mutually exclusive RTX 3090 modes.
- `qwen3-coder-30b` restore and health checks are documented.
- `gemma4-7900xt` preservation checks are documented.
- `model-dispatch` source and config have been inspected read-only.
- The proposed alias name is explicit/manual-only.
- The proposed alias is not included in `auto-local`, `auto-coding-local`,
  `auto-reasoning-local`, or `auto-small-local`.
- Open WebUI auto routing remains unchanged.
- The exact endpoint remains `http://192.168.50.252:18000/v1`.
- The exact served model remains `amd-vllm-temp-qwen2.5-coder-7b` unless a later
  approved runtime slice changes it.
- Rollback consists of removing the alias from `model-dispatch` config/source
  and restarting/reloading only after operator approval.
- The implementation slice has explicit approval to edit the relevant
  `model-dispatch` source files.

No-go if any are true:

- The alias would be added to an automatic route.
- The alias name implies always-on availability.
- vLLM start/stop remains ad hoc and the operator does not accept manual-only
  exposure.
- `qwen3-coder-30b` restore is not documented.
- Open WebUI routing would change in the same step.
- The implementation would touch live `/srv/model-dispatch` without a reviewed
  source patch and approval.

## Future Implementation Phases

### Phase 1: Document Alias Plan

Create this plan and update the handoff. Do not inspect or edit
`model-dispatch` source in this phase.

### Phase 2: Create Repeatable Temporary vLLM Start/Stop Procedure

Document exact operator-reviewed commands for:

- confirming current AMD state
- stopping `qwen3-coder-30b`
- starting temporary vLLM on `18000`
- validating `/v1/models`
- validating `/v1/chat/completions`
- stopping temporary vLLM
- restoring `qwen3-coder-30b`
- confirming `8083` and `8084` health

This procedure should remain manual unless a later architecture decision
explicitly approves persistence or automation.

### Phase 3: Run One More Direct Aider Trial If Needed

Use direct vLLM for one practical single-file patch if more confidence is
needed before routing work.

Do not use `model-dispatch` in this phase.

### Phase 4: Inspect model-dispatch Source And Config Read-Only

Inspect `/srv/projects/model-dispatch` source and config only after a slice
explicitly allows read-only inspection.

Do not edit source, live config, or service state in this phase.

### Phase 5: Propose Explicit Manual Alias Only

Prepare the exact alias patch proposal. The proposal should show:

- alias name
- target base URL
- target served model
- whether it appears in `/v1/models`
- confirmation that no auto route uses it
- curl checks
- rollback patch

### Phase 6: Implement Alias Only After Approval

Edit only approved `model-dispatch` source/config files after the operator
approves the implementation slice.

Do not combine this with Open WebUI routing changes.

### Phase 7: Curl-Test Alias Through model-dispatch

After approved implementation and deployment, test:

- `GET /v1/models` through `model-dispatch`
- `POST /v1/chat/completions` through the explicit alias
- stopped-backend behavior, if safe and approved
- rollback command path

### Phase 8: Optionally Test Aider Through model-dispatch Alias

Only after curl checks pass, run a bounded one-file Aider trial through the
manual alias.

Keep direct vLLM as the rollback comparison path.

## Rollback Expectations

Before implementation:

- Rollback is simple: do nothing. The alias does not exist.

After a future source/config implementation:

- Remove the explicit manual alias from `model-dispatch`.
- Confirm no automatic route references it.
- Redeploy only after operator approval.
- Restart or reload `model-dispatch` only with an approved command block.
- Verify `/v1/models` no longer advertises the alias.
- Verify existing aliases still work.

Runtime rollback remains separate:

- Stop temporary vLLM.
- Restore `qwen3-coder-30b` on `8083`.
- Verify `gemma4-7900xt` still answers on `8084`.
- Do not infer that removing a dispatcher alias changes GPU runtime state.

## Recommendation

Do not add a `model-dispatch` alias yet.

Keep Aider direct-to-vLLM for one more practical one-file patch or until vLLM
runtime mode is made repeatable. If an alias is later added, make it
explicit/manual-only, not auto-routed. Do not route Open WebUI `auto-local` or
`auto-coding-local` to this vLLM endpoint yet. Do not expose it as always
available unless a persistent vLLM runtime exists.
