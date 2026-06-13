# A733 H165 RFC source cross-check

Captured: 2026-06-13T03:09Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Cross-check the current CCU RFC feedback draft against the archived patch 7 source and local sunxi-ng update-bit implementation details.

This note is documentation only. It does not approve sending mail, publishing patches, kernel commits, hardware runs, service changes, or model-routing changes.

## Archived patch checked

Source: Patchew series mbox for:

- `https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/mbox`

Relevant patch:

- Subject: `[PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates`
- Message-id: `<20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech>`

## Direct source matches

Patch 7 adds or exposes the exact clocks discussed in H163:

- `nsi_clk` at register `0x580`
  - patch context shows `SUNXI_CCU_MP_DATA_WITH_MUX_GATE_FEAT(..., 0x580, ...)`
  - flags include `CCU_FEATURE_UPDATE_BIT`
- `bus_nsi_clk`
  - `0x584`, `BIT(0)`, flags `0`
- `ahb_store_clk`
  - `0x5c0`, `BIT(24)`, flags `0`
- `ahb_cpus_clk`
  - `0x5c0`, `BIT(28)`, flags `0`
- `mbus_msi_lite0_clk`
  - `0x5e0`, `BIT(29)`, flags `0`
- `mbus_store_clk`
  - `0x5e0`, `BIT(30)`, flags `0`

This supports the H163 choice to target patch 7/8 and the H163 claims about which clocks need discussion.

## Update-bit implementation nuance

Local Strix source checked:

- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft/drivers/clk/sunxi-ng/ccu_common.h`
- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft/drivers/clk/sunxi-ng/ccu_mp.c`
- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft/drivers/clk/sunxi-ng/ccu_mux.c`
- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft/drivers/clk/sunxi-ng/ccu_gate.c`
- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft/drivers/clk/sunxi-ng/ccu_div.c`

Findings:

- `CCU_FEATURE_UPDATE_BIT` is defined as `BIT(11)`.
- `CCU_SUNXI_UPDATE_BIT` is defined as `BIT(27)`.
- `ccu_mux.c`, `ccu_gate.c`, and `ccu_div.c` OR in `CCU_SUNXI_UPDATE_BIT` when `CCU_FEATURE_UPDATE_BIT` is set.
- `ccu_mp.c::ccu_mp_set_rate()` rewrites the M/P fields but does not OR in `CCU_SUNXI_UPDATE_BIT`.
- `ccu_mp_set_parent()` delegates to the mux helper, so a parent change can use the update-bit path.

Draft wording should therefore avoid saying simply that the common set_parent/set_rate path always pulses the update bit.

More precise wording:

- "The NSI clock has `CCU_FEATURE_UPDATE_BIT`, but no consumer in the tested boot path changes its parent/rate/enable state in a way that commits the boot-programmed value before SDMMC0 IDMA uses the fabric. The MP rate path itself also does not OR in `CCU_SUNXI_UPDATE_BIT`; parent/gate/div helper paths do."

## Draft impact

H163 is technically close, but its sentence:

> the common set_parent/set_rate path never pulses the update bit

is too broad.

Prepare a v5 draft that says:

- no tested boot-path consumer commits NSI before SDMMC0 IDMA;
- parent/gate/div helpers can pulse update bits;
- MP `set_rate()` does not OR the update bit;
- maintainer guidance is needed on whether to add an A733 probe fixup or adjust framework behavior for update-bit MP clocks.

## Guardrails

- Do not send H163 as-is.
- Do not send a v5 draft without final human review.
- Do not use this note as approval for hardware proof or kernel commits.
