# Current Slice

## Slice 2: Build advisor-packet script

Create a small local script named `advisor-packet` that runs from a project working tree and prints a compact markdown packet for the web UI advisor.

The script should collect:
- Current slice, if present
- Decision log, if present
- Agent status, if present
- Agent instructions, if present
- Git status
- Git diff stat
- Bounded git diff excerpt
- Bounded recent coder log, if present

Constraints:
- No network calls
- No model API calls
- No autonomous approval
- No watcher/daemon behavior
- Local files and git only
- Output must be bounded by default

Acceptance criteria:
- Running the script in `/srv/projects/homelab` produces markdown suitable for Open WebUI.
- It works even if optional files are missing.
- It does not fail outside a Git repo; it should report that Git info is unavailable.
- It accepts an optional output path.
