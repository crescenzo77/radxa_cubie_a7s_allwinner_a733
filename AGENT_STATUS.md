# Agent Status

## Current status

Aider is eliminated from the homelab steady-state workflow.

## Current slice

Slice 5: evaluate Aider as the preferred steady-state coder.

## Evaluation result

Aider failed evaluation and should not be used in the homelab workflow.

What worked:

- Installed on Strix with `uv` and Python 3.12.
- Reached Homelab LiteLLM.
- Passed a simple connectivity test.
- Completed one bounded documentation edit after a retry.

What failed:

- The first bounded edit attempt showed a proposed patch but did not leave disk changes.
- The second bounded edit test mis-handled prompt text.
- Aider created bogus files using prompt text as filenames.
- Aider emptied `AGENT_STATUS.md`.
- The bad changes had to be manually cleaned up.

## Decision

Aider is disqualified for this homelab workflow.

The failure occurred during a simple documentation task, so reducing task complexity does not remove the risk. A tool that damages project control files or creates bogus files from prompt text is not acceptable as part of the steady-state workflow.

## Recovery performed

The bad Aider changes were discarded with:

- `git restore --staged -- .`
- `git restore -- AGENT_STATUS.md`
- manual removal of bogus prompt-text filenames

The repo returned to a clean state.

## Risks or blockers

Aider is installed on Strix but should not be used for this homelab workflow.

## Recommended next action

Record the elimination decision in `DECISIONS.md`, then set the next slice to recenter the workflow on OpenCode through LiteLLM.
