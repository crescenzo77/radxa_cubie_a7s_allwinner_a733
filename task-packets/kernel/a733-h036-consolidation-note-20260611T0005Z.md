# A733 H036 Consolidation Note

During the H036 handoff, the original consolidation path from the handoff,
`/Users/enzo/Documents/Homelab/kernel-a733-400b-model-prompt-20260609.md`, was
temporarily not present in the active filesystem. The user later resolved the
Mac file paths, and the file is present again.

Authoritative current state is now:

- Hypothesis queue:
  `/Users/enzo/projects/homelab/task-packets/kernel/a733-hypothesis-queue.json`
- H036 result:
  `/Users/enzo/projects/homelab/task-packets/kernel/a733-h036-desc-er-result-20260611T0005Z.json`
- Model squeeze decision:
  `/Users/enzo/projects/homelab/task-packets/kernel/a733-model-squeeze-20260611T0005Z.json`
- Public status:
  `/Users/enzo/projects/Home Lab/cubie-a7s-armbian/docs/status.md`

H036 result: setting the IDMAC descriptor end-of-ring bit produced descriptor
word 0 `0x8000003c`, but SDMMC0 still stalled at `IDST=0x00004000` with
descriptor memory unchanged. H036 is closed.

H037 follow-up: the restored consolidation file was updated with H036 and H037.
H037 found public U-Boot is PIO-only for sunxi MMC data and does not justify a
Linux normal-IDMAC behavior patch.

Model squeeze result: all four avenues are useful for speculation, but only
source-backed, one-variable tests with falsifiers should enter the queue. The
rerunnable helper is `/Users/enzo/projects/homelab/scripts/a733-model-squeeze`.
