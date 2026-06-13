# Maintainer Feedback

Feedback received on 2026-06-13 indicates that the v1 DTS submission should
not be treated as ready for acceptance as-is.

Actionable items:

- Move the UART0 pin definition from the Cubie A7S board DTS into the main
  A733 DTSI, matching the pattern used for other Allwinner SoCs.
- Re-evaluate timing of the DT submission because the series is early until at
  least the relevant A733 clock support lands.

Practical consequence:

- Do not send a v2 just to churn the thread.
- Track prerequisite RTC, clock, and pinctrl status first.
- Prepare any v2 from a clean kernel branch only after the dependency story
  and DTSI pin placement are clear.
