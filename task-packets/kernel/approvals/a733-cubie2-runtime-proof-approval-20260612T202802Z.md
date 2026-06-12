# cubie2 Runtime Proof Approval Packet

Generated: 2026-06-12T20:28:02Z
Status: `needs-approval`

## Board

- Board: `cubie2`
- IP: `192.168.50.85`
- UART host: `192.168.50.11`
- UART device: `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1.2:1.0-port0`
- UART resolved device: `/dev/ttyUSB1`
- UART mapping status: `inferred-a733-boot-menu-by-elimination`
- Inventory: `/Users/enzo/projects/homelab/inventory/hardware/cubie-a7s-lab.json`

## Artifact

- Artifact directory: `/srv/projects/kernel-work/outgoing/a733-v4-abc8d07b0a63-20260606T152409Z`
- Required checksums are enforced by `scripts/cubie-stage-boot-artifacts` and the generated installer.

## Approval Requested

Approve these steps separately:

1. Stage artifacts into the board user's home directory.
2. Run the generated root-required installer that writes `/boot`.
3. Reboot or select the new boot entry and capture UART evidence.

## Exact First Command After Approval

```sh
scripts/cubie-stage-boot-artifacts 192.168.50.85
```

## Stop Conditions

- Do not run this for `cubie1` unless its exclusion is explicitly lifted.
- Do not write `/boot` without explicit approval for the installer step.
- Do not reboot or change boot defaults without explicit approval.
- Capture UART evidence and run `scripts/cubie-corrected-root-proof-gate` before claiming runtime proof.
