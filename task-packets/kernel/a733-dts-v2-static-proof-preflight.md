# A733 DTS v2 Static Proof Preflight

Status: local-only read-only preflight
Updated: 2026-06-13

This note records a read-only Strix preflight for a future DTS v2 static proof.
It is not a build log, not a patch, not static proof, not send approval, and
not permission to mutate kernel trees or hardware.

## Boundary

Cycle A733-CYCLE-059 performed only read-only inspection:

- no kernel tree edits
- no worktree creation
- no kernel tree copy
- no patch application
- no build commands
- no board boot, reboot, power, install, UART capture, or board SSH probe
- no public communication

## Host And Tree

- host: `strix`
- kernel: Linux 7.0.0-15-generic x86_64
- source tree: `/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
- tree status: detached `HEAD`, dirty A733 prerequisite stack
- head: `8fde5d1d47f69db6082dfa34500c27f8485389a5`

## Required File Status

Read-only preflight observed:

| File | Git status | SHA-256 |
|---|---|---|
| `arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi` | untracked | `83fb09c191c7ac32ed680c44b3459346fecec4d1a9e13d12a49ee575169c5688` |
| `arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts` | untracked | `19680b27e13d0454a46382f35f871c8a0392878cfa75055fe63e0ded127fa51d` |
| `arch/arm64/boot/dts/allwinner/Makefile` | modified | `0b750e9ec64e35036e5be6acf18c4e19cb435e079dd3036dc809b0e4b2207bac` |

Conclusion: do not use a plain detached `git worktree add` at
`8fde5d1d47f69db6082dfa34500c27f8485389a5` for a future proof pass, because it
would omit the observed untracked A733 DTS/DTSI prerequisite files.

## Tool Status

Read-only preflight observed:

- `/usr/bin/aarch64-linux-gnu-gcc`
- `/usr/bin/make`
- `/usr/bin/dtc`
- `scripts/checkpatch.pl`: present
- `scripts/get_maintainer.pl`: present

Tooling appears sufficient for a future static proof after the tree-isolation
problem is resolved.

## Future Isolation Decision

Allowed future proof methods:

- use a committed prerequisite branch or commit where the A733 DTS/DTSI files
  and DTS Makefile update are present, then create a clean temporary worktree
- use a contracted temporary isolated copy that explicitly preserves the
  observed untracked A733 files, records copy commands, records source and
  isolated tree status, and records hashes before applying the DTS v2 preview

Blocked future proof method:

- a plain detached worktree at
  `8fde5d1d47f69db6082dfa34500c27f8485389a5` without preserving untracked A733
  prerequisite files

## Commands Run

```sh
ssh -o BatchMode=yes -o ConnectTimeout=8 strix '<read-only source tree, file, and tool preflight>'
```

The command inspected `git status`, `rev-parse`, selected file status and
hashes, tool paths, and helper-script presence only.

## Next Step

The next local-only static proof cycle should first choose one of the allowed
future proof methods above. If it cannot positively preserve the A733
prerequisite files in an isolated tree, it must stop and log the proof as
blocked. In short: stop and log the proof as blocked.
