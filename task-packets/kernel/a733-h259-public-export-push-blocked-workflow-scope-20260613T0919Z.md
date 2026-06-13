# A733 H259 - Public Export Push Blocked By Workflow Scope

Captured UTC: 2026-06-13T09:19Z

## Purpose

Record the result of attempting to publish the clean Mac public/export repo to
the configured public remote after H258 proved a fast-forward dry-run shape.

This packet is documentation only. It is not a successful public push, not a
`b4 send`, not a `b4 send --reflect`, not a source change, and not a hardware,
service, cron, or model-routing action.

## Pre-Push State

Public/export repo:

```text
branch: main
head:   db53521a63f9cc6a4fc684a927b3bac78173b859
status: ## main...public/main [ahead 215]
```

Public remote before push:

```text
public/main: 57a1325c5a0758ec55094a71f5553ef37818868c
HEAD...public/main: 215 0
```

The dry-run still reported a fast-forward-shaped update:

```text
57a1325..db53521  main -> main
```

## Push Result

Actual push command:

```text
git push public main
```

Result:

```text
remote rejected: refusing to allow an OAuth App to create or update workflow
.github/workflows/kernel-validation-floor.yml without workflow scope
```

## Post-Push Verification

The public remote was fetched after the rejection.

```text
local HEAD:   db53521a63f9cc6a4fc684a927b3bac78173b859
public/main: 57a1325c5a0758ec55094a71f5553ef37818868c
HEAD...public/main: 215 0
```

Remote head remained unchanged:

```text
57a1325c5a0758ec55094a71f5553ef37818868c refs/heads/main
```

The local commits ahead of `public/main` that touch the workflow file are:

```text
1f1e80a docs: adopt kernel workflow automation gates
e74e884 workflow: adopt b4 and validation floor
```

## Interpretation

The public/export repo is still clean and fast-forward-shaped, but the current
GitHub credential cannot publish this history because it updates a workflow
file and lacks workflow scope.

No remote ref changed. The public-export publication blocker is credential
scope, not source readiness.

## Next Safe Options

- Use a GitHub credential with workflow scope and retry the same fast-forward
  push after rechecking `public/main`.
- Create a deliberate no-workflow publication strategy only if preserving the
  workflow commits on GitHub is not required.
- Continue using the internal mirror and local final DTS branch while this
  public backup is blocked.
