# Upstream Submission Discipline

This project treats LKML and subsystem review as the target environment.

## Repository Hygiene

The public branch must not contain:

- generated kernels, DTBs, initrds, or root filesystems;
- UART logs or compressed boot captures;
- one-off operator scripts tied to local hostnames;
- diagnostic register scans presented as production code;
- commit messages that describe experiments as if they were upstream fixes.

Generated files and local lab scripts belong outside the public branch.

## Patch Rules

Candidate patches must:

- apply cleanly with `git am`;
- build from a clean kernel tree;
- pass `git diff --check`;
- pass relevant `scripts/checkpatch.pl` checks;
- pass `make dt_binding_check` for binding changes;
- pass `make dtbs_check` for DTS changes;
- avoid `pr_info()` trace noise and ad hoc register dumps;
- use named register macros for hardware offsets;
- use `dev_dbg()` or existing tracepoints for optional debug messages;
- include a human `Signed-off-by:` trailer only after human review.

## Commit Message Rules

Kernel commit messages should:

- use imperative present tense in the subject;
- state the problem first;
- describe the exact technical change;
- avoid project history unless it is necessary for review;
- avoid "diagnostic-only", "temporary", "do not submit", and similar wording in
  candidate patches;
- keep lab conclusions in cover letters or project notes, not in production
  code commits.

## Patch Split

Expected final split:

1. dt-bindings for A733/A733-Cubie compatible strings and clocks.
2. CCU support required by accepted bindings.
3. pinctrl/GPIO IRQ layout fix or SoC data addition.
4. DTS board enablement.
5. GMAC210 Ethernet glue support, only when the wrapper behavior is proven.

Each patch must be independently reviewable and routed to the right maintainers.

## AI Assistance

Linux kernel documentation permits AI-assisted work only with human
responsibility and transparency. AI agents must not add `Signed-off-by:`.
If AI assistance contributes to a kernel patch, disclose it using the documented
trailer format:

```text
Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]
```

The human submitter remains responsible for licensing, correctness, testing,
and the DCO certification.
