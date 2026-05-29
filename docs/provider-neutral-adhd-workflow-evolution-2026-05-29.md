# Provider-Neutral ADHD Workflow Evolution - 2026-05-29

## Purpose

This document records how the local-agent workflow changed during the planning
conversation on 2026-05-29.

It is intentionally long-form. The active operating spec is:

- `docs/provider-neutral-adhd-workflow.md`

The archived first draft is:

- `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md`

This history exists so future agents can see why the workflow changed, not just
what the final rules are.

## 1. Starting Point

The session resumed from a homelab workflow project focused on local models,
Codex Desktop, model-dispatch, Open WebUI, Aider, and possible future tools such
as OpenCode, Codex CLI, OpenRouter free models, Hermes, and CodeGraphContext.

The live state was validated first:

- Strix was running the llama.cpp/GGUF multi-model arrangement.
- AMD was running the RTX 3090 coder model and RX 7900 XT experimental model.
- ThinkCentre `model-dispatch.service` was active.
- The expected Strix homelab commits were present.
- The expected ThinkCentre model-dispatch commits were present.
- The known untracked ThinkCentre model-dispatch backups were still present and
  intentionally untouched.

The initial recommended slice was to create a concise local-agent workflow
runbook. The first draft became:

- `docs/local-agent-workflow-runbook.md`

That draft described the basic loop:

```text
planner/advisor defines one bounded task
  -> patch tool edits only the selected repo and files
  -> reviewer inspects the Git diff
  -> user chooses Commit, Revise, Revert, or Inspect more
```

The draft was useful but incomplete. It leaned too strongly toward the current
validated Aider paths and did not yet capture the user's real workflow needs.

## 2. User Problem Clarification

The user clarified that the central problem was not simply how to run local
models or how to use Aider.

The actual problem:

```text
The user is unfamiliar with coding, has ADHD, wants to vibe-code and do dev
work, and needs a workflow that scaffolds around drift, fatigue, unclear
explanations, and context loss.
```

The user described the main friction points:

- Ideas are easy; implementation details are harder.
- Higher-level technical language causes comprehension problems.
- LLM drift is frustrating and feels like the user failed to maintain context.
- A good session finishes the project without delay from drift or
  hallucinations.
- A bad session loses context and becomes tainted by hallucinated direction.
- Too little structure is dangerous.
- Too much structure is also dangerous if it causes side quests or process
  overload.
- The user trusts code output more than their own code comprehension, so the
  explanation of what changed matters heavily.
- The user wants strong adherence to the slice task.
- The user prefers Codex Desktop because it reduces web UI to terminal
  copy/paste fatigue.

The workflow therefore had to become a human-support workflow, not only a tool
integration workflow.

## 3. Review Card Clarification

The user asked for clarification around review format and final decision
choices.

The simplified review card became:

```text
Layman review:
I changed <plain description>.
I did it because <reason>.
I did not touch <scary/out-of-scope things>.
I checked <proof>.
Risk: <plain risk level and why>.

Recommendation: Commit / Revise / Revert / Inspect more.
Your choices: Commit / Revise / Revert / Inspect more.
```

The decision words mean:

- `Commit`: keep this patch.
- `Revise`: fix this patch a little.
- `Revert`: throw this patch away.
- `Inspect more`: do not decide yet; gather more evidence.

The review card was adopted because it turns a Git diff into a plain-language
receipt and a simple next decision.

## 4. ADHD Guardrail Decisions

Several ADHD-specific guardrails were selected.

### 4.1 Strict Drift Guardrails

The assistant should interrupt drift early.

If a tool proposes work outside the slice, the workflow should say:

```text
Stop. This is outside the slice.
Park it for later.
Return to the current task.
```

Pleasant language is appreciated, but the workflow should not spend many tokens
being overly soft. Direct language is acceptable when the user is overloaded.

### 4.2 Plain Language First

The default explanation style should be layman's terms first.

Technical names may follow, but they should be brief and clearly separated from
the plain explanation.

The user also accepted short "caveman language" for routine moments.

### 4.3 Smallest Useful Proof

Testing should prove the current slice.

Testing must not become its own side quest.

Default rule:

- run the smallest useful proof
- stop when the slice is proven
- expand testing only when the change is risky or the user asks

Excessive testing can itself be treated as drift.

### 4.4 Resume Notes Are For Drift Protection

Resume notes should be created or updated after meaningful work:

- patch
- decision
- blocker
- session end

They must not be used to pressure shorter conversations, reduce token use, or
push the user away from the preferred tool.

## 5. Session Start Language Changed

The initial language sounded too much like Codex Desktop would always be the
tool doing the asking.

The user corrected this.

The workflow now uses the term:

```text
planner surface
```

instead of assuming Codex is always present.

Before work starts, the active planner surface should establish:

- mode: plan, patch, review, debug, or resume
- repo/project
- provider tier for the session
- current slice
- what must not be touched

This keeps the workflow usable by Codex Desktop, ChatGPT, Open WebUI, a local
model, a future CLI coder, or a human-written slice.

## 6. Aider Over-Correction

The first draft leaned too hard into Aider because Aider had been validated as a
bounded patch tool.

The user pushed back because the workflow should not become "the Aider
workflow."

Corrected principle:

```text
Aider is behind the slice, not behind Codex.
Aider is one patch tool, not the workflow identity.
```

Aider is useful because it can edit named files with local models, but it does
not replicate the Codex Desktop experience.

Codex Desktop is closer to a cockpit:

- inspect files
- run commands
- edit files
- explain what happened
- keep the conversation in one place

Aider is closer to a patch tool:

- useful for bounded edits
- not a planner
- not a full low-friction operating environment

The final role split became:

```text
Planner = defines the bounded task
Patch tool = edits only inside that task
Reviewer = explains the diff
Operator = runs commands/checks when delegated
Resume keeper = records state
User = final decision maker
```

## 7. Provider Neutrality

The user corrected another important issue: permanently binding the workflow to
Codex Desktop would create paid-provider lock-in.

Corrected principle:

```text
The workflow is permanent.
The provider/tool is swappable.
```

The workflow must support:

- frontier models when available
- local models when cost or limits matter
- free cloud models as explicit fallback
- manual edits
- future CLI coders

No workflow step may permanently require Codex, ChatGPT, OpenAI API access,
Claude, Aider, OpenCode, OpenRouter, or any single tool.

## 8. Provider Tiers

The provider tier system emerged from the user's need for a financial
contingency plan.

### 8.1 Tier 1: Frontier / Comfort Tools

Examples:

- Codex Desktop
- ChatGPT
- Claude Code, if explicitly selected

These are preferred when available because they reduce friction and keep more of
the session in one place.

### 8.2 Tier 2: Local Tools

Examples:

- Open WebUI through model-dispatch
- local models on Strix or AMD
- Codex CLI with local provider, if validated
- Aider with local models
- other local CLI coders, if validated

This is the main contingency tier when paid tools are unavailable,
rate-limited, or financially constrained.

### 8.3 Tier 3: Free Cloud Tools

Examples:

- OpenRouter free models

These are explicit fallback tools only. They must not route to paid models
automatically.

## 9. Readiness Labels

The user wanted functional replacements always ready, but also wanted honesty
about what had actually been proven.

The workflow adopted readiness labels:

- `Validated`: proved end-to-end on a bounded real slice.
- `Smoke-tested`: tool responds, but full workflow is not proven.
- `Candidate`: plausible, not proven yet.
- `Blocked`: tried and currently not usable.

This prevents two bad outcomes:

- hiding useful fallback candidates because they are not fully validated yet
- pretending unproven tools are ready

## 10. Tool Status From The Discussion

### 10.1 Codex Desktop

Codex Desktop is the preferred current comfort cockpit.

Why:

- it reduces copy/paste fatigue
- it keeps planning, commands, edits, and review together
- it has been the most helpful current surface for the user

Status:

- `Validated` as current preferred cockpit
- not mandatory

### 10.2 Codex CLI

The installed Codex CLI help showed local provider flags:

```text
--oss
--local-provider <OSS_PROVIDER>
```

Supported local providers shown by the CLI:

- `lmstudio`
- `ollama`

Status:

- `Candidate`
- promising for local contingency work
- not yet validated with this homelab workflow or model-dispatch

### 10.3 Claude Code CLI

Claude Code is useful with Anthropic-backed models.

Clean local LLM support was not established as a reliable contingency path.

Status for local LLM use:

- `Candidate`
- not primary

### 10.4 Aider

Aider is validated for bounded local patches through:

- Strix Coder-Next llama.cpp
- AMD coder through model-dispatch

Status:

- `Validated` as one local patch tool

Boundary:

- not the workflow identity
- not the planner
- no auto-commit
- no deployment
- no service changes
- no autonomous broad work

### 10.5 OpenCode

OpenCode was installed and configured enough to list local models, but local
provider runs produced no usable output or edits.

Status:

- `Blocked` for local model patching

Boundary:

- do not use as a real patch tool until separately fixed and validated

### 10.6 Open WebUI

Open WebUI through model-dispatch is the main local web planner/reviewer
fallback.

Status:

- `Smoke-tested` for local model access
- needs workflow validation with review cards and slice packets

Tradeoff:

- useful local fallback
- more copy/paste fatigue than Codex Desktop

### 10.7 OpenRouter Free

OpenRouter free models are allowed only as explicit fallback tools.

Status:

- `Candidate`

Boundary:

- no automatic paid fallback
- do not use as hidden route

### 10.8 Other Local CLI Coders

Several popular local-capable CLI coder candidates were identified:

- Goose
- OpenHands
- Cline CLI

Status:

- `Candidate`

They should not be promoted until bounded validation proves them.

## 11. Terminal Prompts Explained

The user asked whether "terminal prompts" meant using a CLI coder.

The clarified answer:

Terminal prompts are reusable prompt files or command templates. They can be
used with local models, reviewers, or future CLI coders.

There are two different uses:

### 11.1 CLI Advisor / Reviewer

This does not edit files.

Example:

```text
review prompt + git status + git diff -> review card
```

This is safer because it is read-only.

### 11.2 CLI Coder

This can edit files.

Examples:

- Aider
- Codex CLI
- OpenCode
- other CLI coders

This is riskier and needs stronger boundaries because it can mutate the repo.

## 12. AnythingLLM Discussion

AnythingLLM was discussed as a possible workflow component.

It was compared with CodeGraphContext.

Practical distinction:

```text
AnythingLLM = document memory / chat with notes
CodeGraphContext = code structure memory / ask about repo shape
Hermes = observer / reviewer / recorder / preservation checker
```

Best fit for AnythingLLM:

- project memory
- local knowledge desk
- local reviewer candidate
- long-lived project notes and decisions

Not best fit:

- primary code editor
- patch tool
- command runner
- replacement for Codex Desktop cockpit

Decision:

AnythingLLM should be parked until the primary workflow is completed and
reviewed.

## 13. Hermes And CodeGraphContext Discussion

The user asked about Hermes and CodeGraphContext because they should eventually
become part of the workflow.

Existing homelab docs were inspected.

Current Hermes posture:

- observer
- summarizer
- reviewer
- recorder
- preservation checker

Hermes must not currently:

- edit canonical repos
- restart services
- change model routing
- install live skills without review
- become an approval daemon
- run hidden background jobs
- supervise failures autonomously

Current CodeGraphContext posture:

- may read/index approved canonical repos
- may help inspect code structure
- must not directly mutate canonical working trees
- write-capable use belongs in disposable sandboxes or worktrees

Decision:

Further Hermes and CodeGraphContext workflow expansion should be parked until
the primary Provider-Neutral ADHD Workflow is documented and reviewed.

## 14. Archive Instead Of Delete

The user interrupted when the assistant said it would replace the old runbook
draft.

The user clarified:

```text
We do not delete files.
We archive them or put them in quarantine.
```

The old draft was then archived instead of deleted:

- `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md`

The new active workflow document was created separately:

- `docs/provider-neutral-adhd-workflow.md`

This archive/quarantine rule should apply to future workflow-history files.

## 15. Context Window Concern

The user asked how the assistant prevents losing early planning decisions after
the context window fills.

The answer:

```text
It cannot be solved by chat memory alone.
Important decisions must be written to durable repo docs.
```

The workflow now treats:

```text
conversation = temporary
repo docs = memory
Git = truth
```

This became the Context Preservation Rule in the active workflow doc.

Important planning decisions should be written into durable markdown before
planning continues far enough for those decisions to fall out of context.

## 16. Final Current Workflow Shape

The current workflow shape is:

```text
planner surface establishes mode, repo, provider tier, slice, do-not-touch list
  -> slice packet locks the task
  -> patch tool edits only inside the slice, if patching is needed
  -> operator runs the smallest useful proof
  -> reviewer gives layman review card
  -> user chooses Commit / Revise / Revert / Inspect more
  -> resume keeper records state after meaningful work
```

Core invariant:

```text
Roles are stable.
Tools are swappable.
User remains final approver.
```

## 17. Current Documentation State

As of this history note, the relevant docs are:

- `docs/provider-neutral-adhd-workflow.md`
  - active operating spec
- `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md`
  - long-form history of how the workflow changed
- `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md`
  - archived first draft

The primary workflow doc intentionally parks the following until later:

- AnythingLLM
- Hermes
- CodeGraphContext

Those should receive their own bounded documentation slices after the primary
workflow is accepted.
