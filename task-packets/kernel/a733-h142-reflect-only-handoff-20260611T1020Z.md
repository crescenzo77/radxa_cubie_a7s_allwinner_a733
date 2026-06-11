# A733 H142 Reflect-Only Handoff

Status: machine-ready for human reflect review.

Do not send to the public lists from automation. The only remaining
final-send checklist gate is human review of a `b4 send --reflect` copy.

## Proven Inputs

- Final branch: `codex/final/a733-dts-v1`
- Final worktree: `/srv/projects/kernel-work/final/a733-dts-v1`
- Final head: `1d2642221795d611d607b153c119218e496856a8`
- b4 venv: `/srv/projects/kernel-work/b4-venv`
- Gate 07 result:
  `/Users/enzo/projects/homelab/task-packets/kernel/results/a733-h141-b4-final-gate-20260611T1010Z.json`

## Human Command

Run this on Strix only when ready to receive and review the reflect copy:

```sh
cd /srv/projects/kernel-work/final/a733-dts-v1
source /srv/projects/kernel-work/b4-venv/bin/activate
b4 send --reflect
```

## After Receiving Reflect Copy

Review the received email for:

- subject prefix and version
- cover letter dependency notes
- recipients and lists
- patch order
- no local CCU or pinctrl scaffolding
- no vendor U-Boot DTS workaround
- no Ethernet/VPU/display/USB-C/PCIe/wireless expansion

Only after the reflect copy is acceptable should a separate human-approved real
send be considered.
