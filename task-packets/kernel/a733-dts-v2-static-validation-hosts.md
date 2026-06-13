# A733 DTS v2 Static Validation Hosts

Status: local-only host suitability note
Updated: 2026-06-13

This note records which current machines are suitable for a future local-only
DTS v2 static proof. It is not a build log, not DTB proof, not checkpatch
proof, not maintainer routing proof, not send approval, and not permission to
mutate hardware. It is also not permission to mutate hardware or kernel trees.

## Cycle Boundary

Cycle A733-CYCLE-054 used read-only inventory only:

- no kernel tree edits
- no build commands
- no hardware boot, reboot, power, install, UART capture, or board SSH probe
- no public communication
- no public push from this cycle

## Mac Mini

Host:

- hostname: `enzos-Mac-mini.local`
- kernel: Darwin 25.5.0 arm64

Relevant paths:

- `/Users/enzo/projects/linux-a733-sparse`
  - branch: `candidate/a733-platform-clean-v4`
  - head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
  - status: clean
  - limitation: sparse checkout lacks top-level `Makefile`,
    `scripts/checkpatch.pl`, and `scripts/get_maintainer.pl`
- `/Users/enzo/projects/linux-a733`
  - branch: `candidate/a733-platform-clean-v6`
  - head: `b1f20d455a600d33999cf893fdf0df8fb2ace538`
  - status: dirty with known non-A733 quarantined files
  - has `scripts/checkpatch.pl` and `scripts/get_maintainer.pl`

Tools observed:

- `/usr/bin/make`
- `/opt/homebrew/bin/dtc`
- no `aarch64-linux-gnu-gcc` on PATH

Conclusion: Mac mini is suitable for coordination, preview-patch
`git apply --check` against the clean sparse tree, and documentation. It is not
currently sufficient as the DTS v2 static proof host because the clean sparse
tree is incomplete and the full tree is quarantined.

## Strix

Host:

- hostname: `strix`
- kernel: Linux 7.0.0-15-generic x86_64

Relevant paths:

- `/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
  - branch: detached `HEAD`
  - head: `8fde5d1d47f69db6082dfa34500c27f8485389a5`
  - status: dirty A733 prerequisite stack with modified bindings, DTS
    Makefile, clock, and pinctrl files plus untracked A733 source files
  - has `scripts/checkpatch.pl` and `scripts/get_maintainer.pl`
- `/srv/projects/cubie-a7s-armbian-public`
  - branch: `main...public/main [ahead 215]`
  - head: `db53521a63f9cc6a4fc684a927b3bac78173b859`
- `/srv/projects/homelab`
  - branch: `main...thinkcentre/main [ahead 195]`
  - head: `d46aa0c6a79dde80baf9cf0f0a18b47e9495e0e7`
  - status: dirty and not authoritative for current Mac-mini coordination
    state

Tools observed:

- `/usr/bin/aarch64-linux-gnu-gcc`
- `/usr/bin/make`
- `/usr/bin/dtc`
- `scripts/checkpatch.pl` in the mainline tree
- `scripts/get_maintainer.pl` in the mainline tree

Conclusion: Strix is the best observed future static-validation host because
it has a complete Linux source tree, cross compiler, `make`, `dtc`,
`checkpatch.pl`, and `get_maintainer.pl`. It must not be used in-place for a
proof pass until the proof is isolated in a temporary clean worktree or another
intentionally isolated tree, because the observed mainline tree is dirty and detached.

## ThinkCentre

Host:

- hostname: `thinkcentre`
- kernel: Linux 7.0.0-22-generic x86_64

Relevant paths:

- `/srv/projects/a733-prereq-stack-current`
  - branch: detached `HEAD`
  - head: `8fde5d1d47f69db6082dfa34500c27f8485389a5`
  - status: dirty A733 prerequisite stack matching the observed Strix
    prerequisite-tree shape
  - has `scripts/checkpatch.pl` and `scripts/get_maintainer.pl`
- `/srv/projects/kernel-work/scratch/strix-mainline-linux`
  - missing
- `/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
  - missing
- `/srv/projects/homelab`
  - branch: `main...origin/main [ahead 11, behind 238]`
  - head: `52103585e8087c6a41496286b29b64b7905b14a6`
  - status: dirty with Hermes/hourly/workflow files and not authoritative for
    current Mac-mini coordination state

Tools observed:

- `/usr/bin/make`
- no `aarch64-linux-gnu-gcc` on PATH
- no `dtc` on PATH
- `scripts/checkpatch.pl` in `/srv/projects/a733-prereq-stack-current`
- `scripts/get_maintainer.pl` in `/srv/projects/a733-prereq-stack-current`

Conclusion: ThinkCentre is useful for coordination and source inspection but
is not the best immediate DTS v2 static proof host. It needs a compiler, `dtc`,
and a clean or intentionally isolated full tree before it can record a static
proof pass.

## Future Static Proof Selection

Preferred next host: Strix, but only through an isolated proof workspace.

A future proof cycle should:

- create or identify a temporary full Linux worktree isolated from dirty
  prerequisite work
- record exact base commit, branch, tree path, and out-of-tree `O=` build path
- apply `task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch`
  or the equivalent generated local delta
- run the commands from
  `task-packets/kernel/a733-dts-v2-static-proof-plan.md`
- record logs, generated patch hash, DTB hash, checkpatch result,
  get-maintainer output, and final dirty-tree state
- keep communication posture `local-only` and hardware posture `no boot, no install, no UART capture, no power action`

Stop if the selected tree is dirty outside the contracted proof delta, if the
toolchain is incomplete, or if isolation would require mutating a shared kernel
tree without a prior contract.
