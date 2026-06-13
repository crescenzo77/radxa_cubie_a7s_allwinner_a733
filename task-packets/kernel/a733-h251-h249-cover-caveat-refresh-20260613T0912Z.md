# A733-SDMMC-H251: H249 Cover Caveat Refresh

Captured: 2026-06-13T09:12Z

## Purpose

Fold the H250 common update-bit risk audit into the no-send H249 fallback
bundle, so the fallback cover letter itself is review-safe.

This packet is documentation only. It is not a source change, not a resend
approval, and not a new public thread.

## Change

Updated:

```text
a733-h249-h245-h247-v2-fallback-no-send/cover-letter-v2-fallback-not-sent.txt
a733-h249-h245-h247-v2-fallback-no-send/README.md
```

The cover now says the common helper is scoped to the registration-time handoff
from firmware to Linux and does not claim to audit every later `set_rate()`
path for update-bit clocks.

The README now repeats the same caveat so future users of the no-send bundle do
not overclaim H245/H247.

## Interpretation

This strengthens the maintainer-directed v2 fallback without changing the
public posture:

- H215 remains the submitted narrow A733 series.
- H245/H247 remains a proven fallback if maintainers ask for common
  update-bit handling.
- H249/H251 now carry the H250 caveat directly in the no-send material.

## Next Action

No public action. Keep waiting under H219 unless maintainer response,
sender-mailbox evidence, confirmed delivery failure, or another approved
trigger changes the send posture.
