# A733 Kernel Workflow Proposal

Updated: 2026-06-10T17:22:26Z

This proposal consolidates the current A733/Cubie A7S workflow instructions,
the kernel-process review, and the lab evidence gathered so far.

## Useful Instructions To Keep

- Strix is the hardware execution host. The Mac runs Codex Desktop and issues
  commands to Strix; UART, power control, kernel builds, staging, and Cubie
  SSH should happen from Strix.
- Cubie1 remains reserved. Cubie2 and Cubie3 are the test targets.
- Passwordless `codex` sudo on Cubie2/Cubie3 is useful and should remain.
- The session exit gates are essential: update and commit the private KB,
  public status doc, and machine-readable hypothesis queue before stopping.
- The hypothesis queue should remain first-class JSON with one numbered ready
  work order and a written test procedure.
- Runtime diagnostics must be one-question tests. Build only when source or
  runtime evidence justifies the exact patch.
- Restore Cubie3 to vendor `5.15.147-21-a733` after every test session.
- Do not pollute upstream DTS for vendor U-Boot. Keep `drm_debug=1`, direct
  U-Boot loads, `clk_ignore_unused`, PIO rails, and tracing as lab-only.
- Do not expand into Ethernet, VPU, display, USB-C, PCIe, or wireless during
  the first upstream slice.
- Do not submit local A733 CCU or pinctrl scaffolding while the Junhui Liu and
  Andre Przywara RFCs are in flight.
- Use topic/candidate/review branches, `b4`, a validation floor, and a PR
  checklist for maintainer-shape work.
- Kernel AI attribution rules matter: AI must not add `Signed-off-by`; the
  human submitter owns DCO and final trailers. `Assisted-by:` is useful only
  after the human decides the exact public attribution policy.

## Instructions To Downgrade Or Reject

- Do not run blanket `allmodconfig`, `allyesconfig`, KASAN, KCSAN, lockdep, and
  cross-arch matrices for every lab diagnostic. They are too expensive for
  private hardware narrowing. Reserve them for candidate/review branches.
- Do not set `git config format.signoff true` for agent-run repositories. It
  risks AI-created `Signed-off-by` trailers. Human signoff should be explicit.
- Do not make `git send-email` or mailing-list recipient setup part of the
  daily lab loop. That belongs only after a clean maintainer-shape branch exists.
- Do not use generic subsystem-tree tables as authority. Always use
  `MAINTAINERS`, current lore searches, and the exact touched subsystem.
- Do not use "start small by fixing a warning" as project guidance. This is a
  board bring-up and evidence-management project, not a generic first-patch
  exercise.
- Do not treat `Fixes:` or `stable@vger.kernel.org` as default. The A733 work is
  new enablement unless a specific upstream regression is proven.
- Do not rely on raw flat patch files as the source of truth. Branches and `b4`
  own the submission flow; flat files are review snapshots only.
- Do not automate power control without confirmed board mapping and event logs.
  The current Cubie3 Kasa mapping is known; any new switch/board mapping must
  be re-proven before use.

## Ideal Workflow Now

1. Start every session on the Mac by reading this queue:
   `/Users/enzo/projects/homelab/task-packets/kernel/a733-hypothesis-queue.json`.
   The first `ready` item is the work order.

2. Pull the queue onto Strix before hardware work:
   `ssh strix 'cd /srv/projects/homelab && git pull --ff-only mac-mini main'`.

3. Verify the lab state:
   - Strix kernel worktree and branch are known.
   - Cubie3 SSH works as `codex@192.168.50.95`.
   - Cubie3 is on vendor `5.15.147-21-a733`.
   - UART device is free.

4. For each hypothesis, choose the cheapest valid proof:
   - Source/log audit first.
   - Instrumentation-only patch second.
   - Behavior-changing diagnostic only with source-backed reason.
   - Full maintainer cleanup only after runtime evidence is stable.

5. For runtime tests:
   - Commit the diagnostic patch before building so artifacts have exact HEADs.
   - Build with `TMPDIR=/var/tmp/...` and `O=/var/tmp/...`.
   - Stage artifacts under `/srv/projects/kernel-work/outgoing/...`.
   - Install to Cubie3 `/boot/cthu`, then `sync` and flush block buffers.
   - Use a prompt-controlled U-Boot automation that reaches `=>` before sending
     `setenv`, `ext4load`, `setenv bootargs`, and `booti`. Do not send U-Boot
     commands while extlinux is asking for a menu choice.
   - Capture UART logs and SHA256 hashes.
   - Restore vendor boot and verify `uname -r`.

6. Interpret immediately:
   - Pass/fail against the queue criteria.
   - Whether the hypothesis is closed, narrowed, or needs a rerun because the
     proof did not actually boot the intended kernel.
   - The next queue item must be executable, not prose.

7. End every session only after:
   - Homelab queue/KB commit.
   - Armbian `docs/status.md` commit.
   - Documents private KB commit.
   - Queue synced to Strix.
   - Configured remotes pushed or blocked reason recorded.
   - Cubie3 restored to vendor `5.15.147-21-a733`.
   - Backup tarball created.

## Current H016 State

H016 diagnostic commit exists on Strix:
`529f1682dd48 mmc: trace A733 descriptor fetch stamps`.

Artifact:
`/srv/projects/kernel-work/outgoing/a733-h016-descstamp-529f1682dd48-20260610T171700Z`.

The first boot attempt did not test the kernel. UART automation missed the
U-Boot prompt and sent direct U-Boot commands into the extlinux menu. Log:
`/srv/projects/cubie-uart/logs/20260610T171758Z-a733-h016-descstamp-529f1682dd48-ext4load-ttyUSB0.uart.log`,
SHA256 `3ee0a44fc2ef47139b426332539c6338d3515365052881377e595ed06d06df07`.

Cubie3 was then power-cycled and verified restored to vendor
`5.15.147-21-a733`.

Next action: rerun H016 with a safer UART automation that waits for the real
`=>` prompt or sends Ctrl-C from the extlinux menu before issuing direct U-Boot
commands.
