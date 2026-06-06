# Kernel Proof Harness

Status: Linux-hosted validation image built and self-tested
Validation host: `192.168.50.252`
Operator surface: Codex Desktop only

## Purpose

This harness is the first proof-log layer for kernel work. It runs validation
commands inside a Linux container, captures exact terminal output, and writes a
hashed JSON proof log.

Models are not allowed to declare validation success. They may cite proof IDs.
The proof log is the authority.

## Location

- Dockerfile: `validation/build-validate/Dockerfile`
- Proof runner: `tools/validate/proof_runner.py`
- Dispatcher: `scripts/kernel-proof`
- Remote root: `/srv/projects/kernel-proof` on `192.168.50.252`
- Image: `local/kernel-build-validate:20260606`
- Image ID:
  `sha256:d4a2fba26625b80557c2b855acb4089d415a8cb484c212409fee64bda0fae7a8`

The Mac does not run the container. Codex Desktop dispatches by SSH to
`192.168.50.252`.

## Toolchain

The image currently includes:

- `aarch64-linux-gnu-gcc`
- `git`
- `make`
- `dtc`
- `dtschema==2026.4`
- `yamllint`
- `sparse`
- Python `ply` and `git` modules for kernel SPDX checks used by
  `scripts/checkpatch.pl`
- kernel build dependencies such as `bc`, `bison`, `flex`, `libssl-dev`, and
  `libelf-dev`

The version proof recorded:

- `git version 2.43.0`
- `GNU Make 4.3`
- `aarch64-linux-gnu-gcc 13.3.0`
- `DTC 1.7.0`
- `yamllint 1.33.0`
- `dtschema 2026.4`
- `sparse 0.6.4`
- `Python 3.12.3`

## Self-Test Proofs

The harness has recorded:

- `harness-selftest-version-report-e9cb8a475aa7`: `PASS`
- `harness-selftest-dummy-pass-11cf420fdc62`: `PASS`
- `harness-selftest-dummy-fail-2681326a77f4`: expected `FAIL`, exit code `7`
- `diffcheck-selftest-git-diff-check-ffeec6692429`: `PASS`
- `diffcheck-selftest-git-diff-check-62356085948c`: expected `FAIL`, trailing
  whitespace caught by `git diff --check`
- `external-workspace-selftest-git-diff-check-9303d5484a6a`: `PASS` from
  `/srv/projects/kernel-work/scratch`
- `external-workspace-selftest-git-diff-check-cac39e85d588`: expected `FAIL`
  from `/srv/projects/kernel-work/scratch`
- `synced-strix-mainline-git-diff-check-584ac4f56f72`: `PASS` from
  `/srv/projects/kernel-work/scratch/strix-mainline-linux`
- `synced-strix-mainline-checkpatch-current-diff-strict-4c6a137383fe`: `FAIL`
  from `/srv/projects/kernel-work/scratch/strix-mainline-linux`; the harness
  dependency path is now clean, and the remaining output is patch content:
  `0 errors, 9 warnings, 1 checks`
- `synced-strix-mainline-dt-binding-check-73bf3de72d64`: `PASS` for
  `Documentation/devicetree/bindings/clock/allwinner,sun60i-a733-ccu.yaml`
- `synced-strix-mainline-dtbs-check-b6e4c7ddfccf`: `FAIL` for
  `allwinner/sun60i-a733-cubie-a7s.dtb`; the DTSI references
  `CLK_BUS_GMAC0` and `RST_BUS_GMAC0`, but the A733 dt-bindings headers do not
  define them
- `a733-mmc-compatible-binding-dt-binding-check-562c5187dab1`: `PASS` after
  allowing `allwinner,sun60i-a733-mmc` with the existing
  `allwinner,sun20i-d1-mmc` fallback pattern
- `a733-defer-unproven-gmac-cubie-a7s-dtbs-check-94d5f0714c56`: `PASS` after
  deferring unproven GMAC from the first Cubie A7S validation slice
- `a733-defer-unproven-gmac-checkpatch-current-diff-strict-d61c953b97c1`:
  `FAIL`; remaining output is patch quality/split feedback:
  `0 errors, 7 warnings, 1 checks`

## Commands

```sh
scripts/kernel-proof status
scripts/kernel-proof build-image
scripts/kernel-proof self-test
scripts/kernel-proof pull-logs
```

Use an external scratch worktree:

```sh
VALIDATION_WORKSPACE=/srv/projects/kernel-work/scratch/strix-mainline-linux \
scripts/kernel-proof run \
  --task-id TASK-ID \
  --check git-diff-check \
  -- git diff --check
```

For git-history checks inside the container, use a standalone clone with a real
`.git/` directory under the mounted workspace. Do not use a Git worktree whose
`.git` file points outside the mount. The validation container runs with
`--network none`, so partial clones must be hydrated on the host before running
proof commands that need missing blobs.

Do not place kernel build output under `/tmp` inside this container. `/tmp` is
mounted `noexec`, so generated host tools such as `scripts/basic/fixdep` cannot
run there. Use an output directory under the mounted workspace, then remove it
after the proof run if it is only temporary.

Run strict checkpatch against the current dirty diff, including untracked files:

```sh
VALIDATION_WORKSPACE=/srv/projects/kernel-work/scratch/strix-mainline-linux \
scripts/kernel-proof run \
  --task-id TASK-ID \
  --check checkpatch-current-diff-strict
```

Run a targeted binding check:

```sh
VALIDATION_WORKSPACE=/srv/projects/kernel-work/scratch/strix-mainline-linux \
scripts/kernel-proof run \
  --task-id TASK-ID \
  --check dt-binding-check \
  -- make ARCH=arm64 dt_binding_check \
    DT_SCHEMA_FILES=Documentation/devicetree/bindings/clock/allwinner,sun60i-a733-ccu.yaml
```

Run targeted Cubie A7S DTB validation:

```sh
VALIDATION_WORKSPACE=/srv/projects/kernel-work/scratch/strix-mainline-linux \
scripts/kernel-proof run \
  --task-id TASK-ID \
  --check cubie-a7s-dtbs-check
```

Run a proof command:

```sh
scripts/kernel-proof run \
  --task-id TASK-ID \
  --check git-diff-check \
  -- git diff --check --no-index clean.txt dirty.txt
```

## Current Boundaries

- The container runs on `192.168.50.252`, not the Mac.
- Proof logs stay under `/srv/projects/kernel-proof/proof-logs` until pulled.
- The current scratch mount is `/srv/projects/kernel-proof/scratch`.
- External scratch workspaces under `/srv/projects/kernel-work/scratch` are
  supported with `VALIDATION_WORKSPACE`.
- The synced Strix kernel worktree is mounted by setting
  `VALIDATION_WORKSPACE=/srv/projects/kernel-work/scratch/strix-mainline-linux`.
- Power control and UART capture are not part of this container.

## Current Validation Frontier

The current validation slice now builds the Cubie A7S DTB without GMAC. The
remaining blockers are maintainer-quality issues: patch split, Kconfig help,
and the A733-specific pinctrl workaround in shared core code.

The current submission frontier is stricter than the validation frontier:
A733 CCU/PRCM, pinctrl, and GMAC remain on hold for candidate submission until
the workflow records coordination or rebase notes against the in-flight Linux
RFCs, reviewed clock/reset identifiers, pinctrl IRQ/bank hardware evidence,
and fresh proof IDs.
