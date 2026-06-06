# Cubie A7S Hardware Lab

Status: board facts recorded, automation not enabled
Operator surface: Codex Desktop only

## Immediate Kernel Targets

The next kernel work is for two Radxa Cubie A7S devices:

- `cubie2`: `192.168.50.85`
- `cubie3`: `192.168.50.95`

Current active kernel-work target:

- `192.168.50.95` is the only live A733 board currently safe to use for
  staged kernel boot proof.

Excluded from kernel work:

- `192.168.50.65` must not be used for patch, boot, staging, SSH probe,
  network-discovery, UART-proof, or root-install work. It is reserved for Wyze
  camera object detection. If it appears to be an A733/Cubie-like host, treat
  that as a reason to exclude it, not as permission to use it.

Quick network observation:

- `192.168.50.95` answered a one-packet ping check.
- `192.168.50.85` did not answer the same quick check.
- 2026-06-06 follow-up: `192.168.50.95` still answered one ping;
  `192.168.50.85` still did not.
- 2026-06-06 SSH probe: `192.168.50.95` has SSH reachable, but the current
  key/user attempts were denied; `192.168.50.85` timed out on port 22.
- 2026-06-06 refresh: `192.168.50.95` still answers ping and has port 22 open;
  `192.168.50.85` still does not answer ping.
- 2026-06-06 passive neighbor-cache sweep across Mac, Strix, ThinkCentre, and
  AMD found Radxa-like MAC prefix `08:51:49` only at excluded `192.168.50.65`
  and Cubie3 `192.168.50.95`. The stale Cubie2 address `192.168.50.85`
  appeared only as incomplete/failed where present. No alternate Cubie2 IP was
  found passively.
- 2026-06-06 read-only UART IP query on the Cubie2 candidate adapter returned
  0 bytes. It did not reveal a Cubie2 IP address.

Treat reachability as a live lab condition, not a permanent fact.

Treat `192.168.50.65` as a permanent exclusion unless the operator explicitly
changes that rule.

Use the bounded helper instead of an open-ended TCP probe:

```sh
scripts/cubie-network-status
scripts/cubie-network-status --json
```

## UART Host

Both Cubie UART connections terminate on `192.168.50.11`.

Observed serial devices on `192.168.50.11`:

- `/dev/ttyUSB0`
- `/dev/ttyUSB1`
- `/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0`
  currently points to `/dev/ttyUSB1`

2026-06-06 USB identity check:

- both adapters report as Silicon Labs CP2102 devices with serial `0001`
- `/dev/ttyUSB0` is on path `pci-0000:c3:00.4-usb-0:1.1:1.0`
- `/dev/ttyUSB1` is on path `pci-0000:c3:00.4-usb-0:1.2:1.0`
- because the adapters report the same serial, prefer `/dev/serial/by-path/`
  names over `/dev/serial/by-id/` names for stable capture commands
- Strix kernel logs show `cp210x` attached `usb 1-1.1` to `/dev/ttyUSB0`
  and `usb 1-1.2` to `/dev/ttyUSB1`
- `stty` confirms both adapters are readable at 115200 baud

2026-06-06 passive capture check:

- `/dev/ttyUSB0`: 10 seconds at 115200 baud, 0 bytes captured
- `/dev/ttyUSB1`: 10 seconds at 115200 baud, 0 bytes captured
- no active serial readers were reported
- by-path capture verification also passed:
  - `pci-0000:c3:00.4-usb-0:1.1:1.0-port0`: 5 seconds, resolved to
    `/dev/ttyUSB0`, 0 bytes captured
  - `pci-0000:c3:00.4-usb-0:1.2:1.0-port0`: 5 seconds, resolved to
    `/dev/ttyUSB1`, 0 bytes captured

This confirms the devices exist and are readable, but it does not establish the
board-to-tty mapping.

2026-06-06 prompt probe:

- `pci-0000:c3:00.4-usb-0:1.1:1.0-port0` returned `cubie-3 login:` and is
  confirmed as Cubie3.
- `pci-0000:c3:00.4-usb-0:1.2:1.0-port0` returned 0 bytes after an Enter
  probe. It remains only a Cubie2 candidate until boot or login text identifies
  the board.
- A fixed read-only hostname/IP query on the 1.2 adapter also returned 0
  bytes, so UART has not revealed a Cubie2 IP address.

Do not assume the board-to-tty mapping yet. Confirm by capturing boot output
from one board at a time.

Use:

```sh
scripts/cubie-uart list
scripts/cubie-uart capture /dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.2:1.0-port0 cubie3-boot-probe 30
scripts/cubie-uart readonly-ip-query /dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.2:1.0-port0 cubie2-ip-query 12
scripts/cubie-uart pull-logs
scripts/cubie-uart-report
scripts/cubie-event-log list
scripts/cubie-runtime-evidence
```

To open a passive capture window on both UART adapters before a human manually
power-cycles one board, use:

```sh
scripts/cubie-boot-capture-window 120 cubie-manual-boot
```

That helper captures both UARTs and pulls the logs. It does not power-cycle
anything and still does not identify which board is on which UART until boot
text is observed. After pulling logs, it also prints a compact UART report that
flags non-empty captures and common boot/error markers, records capture-start
and capture-end events, and writes a runtime evidence packet.

For a fuller manual evidence session, use:

```sh
scripts/cubie-manual-boot-session 120 cubie-manual-boot
```

That wrapper performs a bounded pre-capture network check, opens the UART
capture window, performs a bounded post-capture network check, prints the
latest manual event log, writes final runtime evidence, and prints read-only
UART mapping candidates plus the deterministic runtime gate. It still does not
power-cycle anything, claim a reset happened, or update inventory.

Use `scripts/cubie-runtime-evidence` after any capture window to create a
reviewable evidence packet. If UART logs are still empty, the packet explicitly
marks runtime evidence as missing rather than implying a boot proof.

When the human operator touches a board, log the action before or immediately
after it happens:

```sh
scripts/cubie-event-log add --board cubie3 --event manual-reset --note "manual reset during cubie-manual-boot capture"
scripts/cubie-event-log list
```

Prefer including the capture label in the note so mapping tools can correlate
the manual action:

```sh
scripts/cubie-event-log add --board cubie3 --event manual-reset --note "label=cubie-manual-boot manual action during capture"
scripts/cubie-uart-map-candidates
scripts/cubie-runtime-gate
scripts/cubie-uart-inventory-proposal
scripts/cubie-runtime-proof-bundle
```

`scripts/cubie-runtime-gate` classifies the current state without model
judgment. Current expected status before the Cubie3 sudo/root install is
`root-install-required`. After the installer adds the non-default extlinux
entry, the expected status is `boot-selection-required` until a UART capture
proves the selected mainline boot. Use `--json` for machine-readable output,
and use `--strict` only when a non-zero exit should stop an automation until
runtime proof is ready.

`scripts/cubie-stage-boot-artifacts` writes only to the board user's staging
directory. Its generated root installer copies `SHA256SUMS` into the
`/boot/mainline-a733-*` install directory, verifies the installed Image/DTB
copy, updates extlinux, and runs `sync` before reporting success.

Use `scripts/cubie-root-install-handoff` to print the current root-install
handoff from verified staging state. It is read-only and reports the exact
sudo/root install command plus the post-install UART capture command. With
`--strict`, it returns non-zero until the installed boot files and checksums
are detected.

If Codex should wait while the human performs the root install, run
`scripts/cubie-root-install-handoff --wait 600 --run-capture`. It polls for the
installed/checksummed boot entry and starts the UART capture session only after
that gate passes. It does not reboot or power-cycle the board.

`scripts/cubie-uart-inventory-proposal` is also read-only. It emits a proposed
board UART mapping only after a strong candidate exists; it never edits the
inventory.

`scripts/cubie-runtime-proof-bundle` writes a timestamped proof directory under
`task-packets/kernel/runtime-proof/`. Each bundle includes runtime evidence,
gate output, UART mapping candidates, inventory proposal output, and a
`manifest.json` with SHA256 hashes for the generated artifacts.

Manual event logs are stored locally under:

```text
tools/hardware-logs/cubie-events.jsonl
```

That log is ignored by git, but `scripts/cubie-runtime-evidence` includes its
latest entries in generated evidence packets.

UART capture logs are stored on `192.168.50.11` under:

```text
/srv/projects/cubie-uart/logs/
```

Pulled copies are ignored locally under:

```text
tools/hardware-logs/cubie-uart/
```

## Power Control

There are two Wi-Fi home automation switches formerly used to power down and
power on the Cubie boards.

Current status:

- switch IPs are not recorded here yet
- switch API/control method is not recorded here yet
- switch-to-board mapping is not confirmed here yet
- no automated power cycling is enabled
- 2026-06-06 passive ARP and short mDNS browse samples did not identify a
  confirmed switch candidate

Rules:

- never power-cycle a board from the pipeline until the switch mapping is
  confirmed
- require explicit human approval before any power-off or power-on action
- log every power event with board, switch, timestamp, reason, and operator
- capture UART before and after power events when debugging boot behavior

## Future Hardware-Lab Tools

Add narrow tools only after mapping is confirmed:

- `uart_list_devices`
- `uart_capture`
- `uart_capture_boot_window`
- `power_status`
- `power_on_confirmed`
- `power_off_confirmed`
- `power_cycle_confirmed`

Power tools must require an explicit board ID and confirmed switch ID. They
must not accept vague targets such as "the board" or "both boards".

## Historical Patch-Work Documentation Sweep

On 2026-06-06, Codex reviewed additional Mac-local, ThinkCentre, and Strix
documentation for prior Cubie A7S patch work.

Relevant Mac-local history:

- `/Users/enzo/Downloads/mainline-cleanup-workflow.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-11-first-controlled-real-run.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-12-two-agent-loop.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-13-review-bundle-enhancement.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-14-full-read-review-bundle-enhancement.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-15-enforced-two-agent-doc-loop.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-5-openhands-hil-viability.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-6-openhands-safety-harness.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-7-agent-bakeoff.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-8-qwen-code-goose-bakeoff.md`
- `/Users/enzo/projects/Home Lab/research/kernel-llm-bench/round-9-mcp-safety-harness.md`

Mac-local workflow lessons:

- validation must include content completeness, not only syntax
- review bundles must prove required files were fully read, not just opened
- typed patch/edit tools are safer than raw model-generated diffs
- reviewer output with caveats is not a pass for upstream-facing work
- local agent harnesses must stay behind bounded tools; unrestricted default
  modes failed earlier safety tests
- the mainline lane requires evidence-bound patch admission, trailer hygiene,
  and publication scans before public or upstream-facing output

Relevant ThinkCentre history:

- `/srv/projects/kernel-services/cortex/ingest/a733-rfc-recheck-20260606.md`
- `/srv/projects/kernel-services/cortex/ingest/a733-overlap-scan-20260606.md`
- `/srv/projects/kernel-services/cortex/ingest/a733-inflight-ccu-pinctrl-state-20260606.md`
- `/srv/projects/kernel-services/cortex/ingest/cubie-hardware-readiness-20260606.md`
- `/srv/projects/kernel-services/cortex/logs/cortex-bringup-proof-20260606.md`

ThinkCentre workflow lessons:

- independent CCU/PRCM, pinctrl, and GMAC submission work remains on hold
  until in-flight Linux RFC overlap is resolved
- the research sidecar is useful for evidence retrieval and review, but its
  summaries do not replace source inspection or hardware proof
- Qdrant stays private and loopback-bound on ThinkCentre; public repo docs must
  not leak private service paths, local topology, or generated model logs

Relevant Strix history:

- `/srv/projects/cubie-a7s-local-agent/A733_PROGRESS_ACTION_PLAN_20260530.md`
- `/srv/projects/cubie-a7s-local-agent/UPSTREAM_SUBMISSION_DISCIPLINE.md`
- `/srv/projects/cubie-a7s-local-agent/A733_UNCERTAINTY_REGISTER_20260530.md`
- `/srv/projects/cubie-a7s-local-agent/A733_ETHERNET_ENABLEMENT_NOTES.md`
- `/srv/projects/cubie-a7s-local-agent/CURRENT_TEST_TOPOLOGY.md`
- `/srv/projects/cubie-a7s-local-agent/FIRST_BOOT_EXECUTION_CHECKLIST_20260530.md`
- `/srv/projects/cubie-a7s-local-agent/LIVE_VENDOR_EVIDENCE_20260530.md`
- `/srv/projects/cubie-a7s-local-agent/PUBLIC_REPOSITORY_STAGING.md`
- `/srv/projects/cubie-a7s-local-agent/UART0_PINCTRL_EVIDENCE_20260529.md`
- `/srv/projects/cubie-a7s-local-agent/UART_BOOT_CAPTURE_20260530.md`
- `/srv/projects/cubie-a7s-local-agent/VENDOR_UBOOT_DTB_HANDOFF_ANALYSIS_20260531.md`
- `/srv/projects/cubie-a7s-local-agent/VENDOR_UBOOT_SOURCE_INSPECTION_20260601.md`
- `/srv/projects/cubie-a7s-local-agent/MAINLINE_RFC_V7_BOOT_STAGING_20260530.md`
- `/srv/projects/cubie-a7s-local-agent/MAINLINE_RFC_V7_REBASE_VALIDATION_20260531.md`
- `/srv/projects/cubie-a7s-local-agent/PUBLICATION_PRIVACY_AUDIT_20260602.md`
- `/srv/projects/cubie-a7s-local-agent/patches/mainline-a733/eth-prep/README.md`
- `/srv/projects/cubie-a7s-local-agent/patches/mainline-a733/rfc-v5/README.md`
- `/srv/projects/cubie-a7s-local-agent/patches/mainline-a733/rfc-v6/README.md`
- `/srv/projects/cubie-a7s-local-agent/patches/mainline-a733/rfc-v7/README.md`

Strix workflow lessons:

- an older first-boot checklist already identified the same root-write/reboot
  blocker: noninteractive SSH could not write `/boot`, root SSH was denied,
  and there was no confirmed noninteractive reset/power path
- historical UART logs show prior RFC v7 hybrid DTB work reached an
  interactive mainline serial REPL on `/dev/ttyS0`; treat that as design
  evidence, not as proof for the current public artifacts
- after writing extlinux or initrd changes, run `sync` before any power cut or
  reset; one older test booted a stale entry after a rapid power cut
- the older storage-aware REPL reached userspace but did not expose MMC block
  nodes, so fresh runtime proof must explicitly cover SDMMC0/root device
  behavior before making storage claims
- prior `no-PIO-IRQ`, IRQ-bank-map, and pinctrl trace branches are diagnostic
  evidence only; they must not be promoted into an upstream patch series
- the GMAC0 path has evidence for address, Port H RGMII pins, MDIO address 1,
  and probe when pinctrl or PIO IRQ handling is bypassed, but not full
  Ethernet support
- the recurring Port H `PH0` stall points toward A733 PIO IRQ handling,
  pending IRQ state, or chained-handler behavior; the missing `vcc-ph` supply
  and zero-based IRQ-bank-map tests did not fully explain it
- clean mainline DTBs failing under vendor U-Boot is a bootloader handoff
  constraint, not evidence that vendor-only node names belong in upstream DTS
- public-facing output must be scanned for private paths, lab IPs, AI/tool
  trailers, placeholder identities, and unverified claims before publication
- older Strix public-staging notes mention a different public Linux fork and an
  older identity; do not reuse those submission details for the current public
  repo or current sign-off identity
