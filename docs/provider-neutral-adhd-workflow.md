# Provider-Neutral ADHD Workflow

## 1. Purpose

This workflow exists so the user can do vibe-driven development without losing
control of the project.

It is designed to protect against:

- wrong repo work
- lost context
- tool drift
- hallucinated direction
- excessive testing
- unclear technical explanations
- copy/paste fatigue
- paid-provider lock-in

The workflow should support frontier models, local models, free fallback
models, manual work, and future CLI coding tools without permanently depending
on any single provider.

Core rule:

```text
The workflow is permanent.
The provider/tool is swappable.
```

## 1.1 Workflow Principle

Roles stay stable. Tools may change per session.

Stable roles:

- Planner
- Patch tool
- Reviewer
- Operator
- Resume keeper
- User

No role is permanently bound to Codex, ChatGPT, OpenAI API access, Claude,
Aider, OpenCode, OpenRouter, or any single tool.

## 1.1.1 Provider Neutrality

Codex Desktop may be the preferred current cockpit because it reduces friction,
keeps work in one place, and avoids constant web UI to terminal copy/paste.

Codex Desktop is preferred, not mandatory.

If a paid frontier tool becomes unavailable, rate-limited, or financially
constrained, the workflow must keep working by switching the provider for the
same role.

## 1.1.2 ADHD Scaffold Requirement

The workflow must reduce cognitive load.

It should use:

- clear slice boundaries
- plain-language explanations
- small review cards
- explicit do-not-touch lists
- strict drift interruption
- minimal necessary testing
- resume notes after meaningful work

If the process itself becomes a burden, simplify the current slice instead of
adding more ceremony.

## 1.1.3 Context Preservation Rule

Chat memory is temporary. Repo docs and Git state are durable memory.

If a planning decision matters, it should be written into a durable markdown
file before the conversation continues far enough for the decision to fall out
of context.

Use:

- `CURRENT_SLICE.md` for the active task
- `DECISIONS.md` for durable decisions and rationale
- `AGENT_STATUS.md` for current handoff state
- workflow docs for reusable process rules
- Git diff/log for what actually changed

## 1.2 Provider Tiers

Provider tier is a session choice. The active planner surface should establish
which tier is being used before work begins.

### 1.2.1 Tier 1: Frontier / Comfort Tools

Examples:

- Codex Desktop
- ChatGPT
- Claude Code, if explicitly selected

Use when available and worth the cost because these tools reduce friction and
help keep planning, command execution, review, and explanation together.

### 1.2.2 Tier 2: Local Tools

Examples:

- Open WebUI through model-dispatch
- local models on Strix or AMD
- Codex CLI with local provider, if validated
- Aider with local models
- other local CLI coders, if validated

This is the main contingency path when paid tools are unavailable,
rate-limited, or financially constrained.

### 1.2.3 Tier 3: Free Cloud Tools

Examples:

- OpenRouter free models

These are explicit fallback tools only. They must not route to paid models
automatically.

## 1.3 Readiness Labels

Every tool path should be labeled honestly.

- `Validated`: proved end-to-end on a bounded real slice.
- `Smoke-tested`: tool responds, but full workflow is not proven.
- `Candidate`: plausible, not proven yet.
- `Blocked`: tried and currently not usable.

Do not promote a candidate into normal use until a bounded validation slice
proves it.

## 1.4 Role Model

### 1.4.1 Planner

The planner turns vague intent into one bounded slice.

The planner may be:

- Codex Desktop
- ChatGPT
- Open WebUI local model
- OpenRouter free model
- CLI coder in planning mode
- human-written slice

The planner must not silently expand the task.

### 1.4.2 Patch Tool

The patch tool edits files only inside the approved slice.

The patch tool may be:

- Codex Desktop
- Aider
- Codex CLI
- OpenCode, if later validated
- another CLI coder, if later validated
- manual edits

The patch tool is not allowed to become the planner. It must stop after one
reviewable diff unless the user explicitly approves more work.

### 1.4.3 Reviewer

The reviewer explains what changed in layman's terms and recommends one next
decision:

- Commit
- Revise
- Revert
- Inspect more

The reviewer does not approve automatically.

### 1.4.4 Operator

The operator runs commands and checks when explicitly delegated.

This role is separate because not every planner, reviewer, or patch tool should
be trusted with shell access.

### 1.4.5 Resume Keeper

The resume keeper records state after meaningful work.

Resume notes exist to prevent drift. They must not be used to pressure shorter
conversations or push the user away from a preferred tool.

### 1.4.6 User

The user is the final decision maker.

Only the user approves:

- commit
- deployment
- service changes
- provider switch
- scope expansion

## 1.5 Session Start Rule

Before work starts, the active planner surface should establish:

- mode: plan, patch, review, debug, or resume
- repo/project
- provider tier for the session
- current slice
- what must not be touched

Use the phrase `planner surface` instead of assuming Codex is always active.
Codex Desktop is one possible planner surface.

## 1.6 Slice Packet

Every task should be reducible to a slice packet:

```text
Repo:
Mode:
Goal:
Allowed files:
Forbidden files:
Do not touch:
Patch tool, if any:
Checks:
Stop condition:
Review format:
```

The slice packet is the anti-drift object. If a tool starts making assumptions,
return to the slice packet.

## 1.7 Review Card

Every patch review should include:

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

Technical detail may follow, but the plain explanation must be clearly marked.

## 1.8 Testing Rule

Testing should prove the current slice, not become a side quest.

Default:

- run the smallest useful proof
- stop when the slice is proven
- expand testing only when risk is high or the user asks

Excessive testing can itself be treated as drift.

## 1.9 Drift Rule

If a tool proposes work outside the slice:

```text
Stop. This is outside the slice.
Park it for later.
Return to the current task.
```

Side topics may be acknowledged briefly, but they should not take over the
session.

## 1.10 Current Tool Posture

### 1.10.1 Codex Desktop

Codex Desktop is currently the preferred comfort cockpit because it reduces
copy/paste fatigue and keeps planning, command execution, review, and
explanation in one place.

Status: `Validated` as current preferred cockpit.

Codex Desktop is preferred, not mandatory.

### 1.10.2 Aider

Aider is one validated local patch tool.

Status: `Validated` for bounded local patches through Strix and AMD local
models.

Aider is not the workflow identity.

Aider must not:

- plan the slice
- broaden scope
- auto-commit
- deploy
- change services
- become autonomous

### 1.10.3 Codex CLI

Codex CLI appears to support local providers such as Ollama or LM Studio, but
the local-provider workflow is not yet validated in this homelab.

Status: `Candidate`.

### 1.10.4 Claude Code CLI

Claude Code is useful with Anthropic-backed models, but local LLM use is not a
clean validated contingency path.

Status for local LLM use: `Candidate`, not primary.

### 1.10.5 OpenCode

OpenCode local provider path was tested and is currently blocked.

Status: `Blocked` for local model patching.

It must not be used as a real patch tool until separately fixed and validated.

### 1.10.6 OpenRouter Free

OpenRouter free models are allowed only as explicit fallback tools.

Status: `Candidate` until validated under this workflow.

No automatic paid fallback is allowed.

### 1.10.7 Open WebUI

Open WebUI through model-dispatch is the main local web planner/reviewer
fallback.

Status: `Smoke-tested` for local model access and useful planning/review
surface; still needs review-card workflow validation.

### 1.10.8 AnythingLLM

AnythingLLM may later be useful as project memory or local review support.

Status: `Candidate`.

Park AnythingLLM until the primary workflow is documented and reviewed.

### 1.10.9 Hermes

Hermes may later serve as observer, reviewer, recorder, drift detector, and
preservation checker.

Status: existing conservative role remains in force.

Park additional Hermes workflow expansion until the primary workflow is
documented and reviewed.

### 1.10.10 CodeGraphContext

CodeGraphContext may later serve as code context and structural repo
understanding.

Status: existing conservative role remains in force.

Park additional CodeGraphContext workflow expansion until the primary workflow
is documented and reviewed. Write-capable use must remain sandbox/worktree-only.

## 1.11 Contingency Principle

Every important role should have:

- best current tool
- local fallback
- free fallback
- readiness label

If the chosen tool becomes unavailable, the workflow should pause and offer the
next viable replacement for the same role. It should not silently switch tools.

## 1.12 Initial Contingency Matrix

| Role | Best current tool | Local fallback | Free fallback | Current note |
|---|---|---|---|---|
| Planner | Codex Desktop / ChatGPT | Open WebUI local model | OpenRouter free | Local and free paths need workflow validation |
| Patch tool | Codex Desktop or manual edits | Aider with local AMD/Strix model | Candidate CLI coder/free path | Aider is validated, not mandatory |
| Reviewer | Codex Desktop / ChatGPT | Open WebUI local model | OpenRouter free | Review-card validation still needed |
| Operator | Codex Desktop or user terminal | user terminal with local prompts | none by default | Shell access remains explicit |
| Resume keeper | Codex Desktop / ChatGPT | local model summary through Open WebUI | OpenRouter free | Resume notes protect context |

## 1.13 Tool Failure Playbook

If a chosen tool is unavailable, rate-limited, too expensive, or behaving badly:

1. Keep the same slice packet.
2. Switch only the role provider, not the task.
3. Prefer local replacements before free cloud replacements when practical.
4. Run the same review card.
5. Do not silently switch providers.

If the replacement is not validated:

1. Label it `Candidate`.
2. Test it on a safe non-critical slice first.
3. Promote it only after proof.

## 1.14 Immediate Documentation Boundary

Finish this primary workflow before expanding AnythingLLM, Hermes, or
CodeGraphContext.

The next documentation slices may cover:

- AnythingLLM as project memory and local review support.
- Hermes as observer, reviewer, recorder, drift detector, and preservation
  checker.
- CodeGraphContext as code context and structural repo understanding.

Do not expand those tools until the primary Provider-Neutral ADHD Workflow is
reviewed and accepted.
