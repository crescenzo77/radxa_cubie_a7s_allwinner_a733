# Candidate Series Audit: 2026-06-04

This note records the current upstream-readiness audit for the local A733
candidate kernel series. It does not publish patch files.

## Local Kernel Branches

Current cleaned work branch:

```text
sources/mainline-linux-a733-upstream
a733-cubie-a7s-series-v1-clean
```

Baseline candidate inspected:

```text
sources/mainline-linux
a733-cubie-a7s-rfc-v7-rst41-public
```

The original lab/debug branches remain local working history. They are not
public `main` material.

## Audit Result

The non-Ethernet A733/Cubie A7S candidate series is the right near-term
upstream milestone. It avoids claiming Ethernet while GMAC0 still has an
unresolved DMA software reset timeout.

The candidate series still needs cleanup before submission:

- DTS/driver/binding changes must be split so binding patches stand alone.
- Human `Signed-off-by:` trailers must be added only after human review.
- Commit messages need to remove lab-history prose and stay focused on the
  problem and technical change.
- Pinctrl must model the structural GPIO IRQ bank layout correctly.
- The current `fixup: align A733 pinctrl IRQ bank count` commit must be folded
  into the matching binding, driver, and DTS commits before the branch can be
  treated as a candidate patch series.

## Pinctrl Correction

The cleaned local work branch now carries a checkpoint commit:

```text
pinctrl: sunxi: account for A733 missing Port A IRQ bank
```

The change aligns the candidate with the A733/A523 GPIO IRQ layout:

- physical Port A has zero pins;
- the IRQ register layout still reserves the Port A bank slot;
- the pinctrl driver registers eleven IRQ bank slots;
- the A733 DTSI includes the structural first parent interrupt before the
  Port B through Port K parent interrupts;
- the pinctrl binding allows eleven parent interrupts for this layout.

This is still a checkpoint, not a final patch shape. The binding, driver, and
DTS changes must be split or folded into the right patches before any upstream
submission.

Public candidate branches must not contain `fixup:` commits. The fixup commit
is acceptable only as local working state.

## Checkpatch Status

The checkpoint patch was checked with:

```text
perl scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
```

Remaining issues are expected for a checkpoint patch:

- `DT_SPLIT_BINDING_PATCH`: binding and DTS/driver changes must be separated;
- `MISSING_SIGN_OFF`: a human DCO signoff is intentionally absent until human
  review.

No whitespace errors were reported by `git diff --check`.

## Ethernet Boundary

Ethernet remains outside the initial upstream candidate series.

Do not enable GMAC0 in an upstream-facing Cubie A7S board DTS until:

- the GMAC210 wrapper programming model is defined with named registers;
- CCU clock and reset dependencies are represented by accepted bindings;
- common STMMAC code receives a stable, clocked DWMAC core;
- MDIO proves real external PHY communication;
- probe no longer reports the DMA software reset timeout.
