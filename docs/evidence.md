# Evidence Register

This page records facts that are useful for future upstream patches. It avoids
large logs and generated artifacts.

## A733 GMAC0

Vendor DT evidence for A733 GMAC0:

```text
reg = <0x04500000 0x8000>, <0x04508000 0x1000>
compatible = "allwinner,sunxi-gmac-210", "snps,dwmac-5.20"
clock-names = "stmmaceth", "pclk", "phy", "ptp_ref"
reset-names = "stmmaceth", "ahb"
```

Vendor board evidence for Cubie A7S:

```text
GMAC0 pins: PH0-PH15, function "rgmii0"
MDC:        PH8
MDIO:       PH9
PHY clock:  PH15
PHY reset:  PH16, active low
```

Local mainline traces showed the second GMAC0 resource at `0x04508000` becomes
live after the `stmmaceth` reset line is deasserted. Candidate wrapper values
observed under the generic DWMAC path included:

```text
0x000 = 0x00008000
0x084 = 0x00000200
0x08c = 0x03080808
0x090 = 0x03080832
0x094 = 0x00000008
```

These values are evidence for wrapper behavior only. They are not a final
mainline programming model.

## Vendor Source Lead

Orange Pi's `orange-pi-5.15-sun60iw2` branch contains Allwinner BSP files:

```text
bsp/drivers/stmmac/dwmac-sunxi.c
bsp/drivers/stmmac/dwmac-sunxi.h
bsp/configs/linux-5.15/sun60iw2p1.dtsi
```

The BSP GMAC210 definitions identify wrapper offset `0x00` as a configuration
register containing interface and delay-chain fields. Any upstream driver work
must translate this into clean named macros and reviewed binding properties.

## Negative Results

The following local experiments did not clear the DWMAC DMA software reset
condition by themselves:

- generic `snps,dwmac-5.20` binding without Allwinner wrapper setup;
- alternate reset ordering between `stmmaceth` and `ahb`;
- mapping the current GMAC0 MBUS clock as generic `pclk`;
- enabling the vendor-evidenced `phy` clock on the generic path;
- adding generic AXI configuration alone.

The active question is still wrapper/domain/clock sequencing, not confirmed
Ethernet functionality.
