# A733 H249 H245/H247 V2 Fallback Bundle

This directory contains no-send material only.

Use it only if maintainers ask for common `CCU_FEATURE_UPDATE_BIT` handling or
otherwise request a v2 shape broader than the submitted narrow A733 NSI update
bit expression.

Review caveat from H250: this fallback is a registration-time commit of
boot-programmed update-bit state. It is not a claim that every future
update-bit `set_rate()` path has been audited or fixed.

Contents:

- `cover-letter-v2-fallback-not-sent.txt`

The source patches remain the H245 artifact patches:

- `0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch`
- `0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch`
- `0003-clk-sunxi-ng-commit-update-bit-clocks-during-registr.patch`
- `0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch`

Do not send from this directory directly. Before any public use, regenerate or
reconfirm the full series from the current source tree and rerun:

- recipient/thread freshness;
- public hygiene;
- trailer hygiene;
- `git am --3way` from the selected base;
- `git diff --check`;
- strict checkpatch;
- focused build/static checks;
- hardware-proof relevance check.
