# A733-SDMMC-H210: Normalized RFC/RFT Send Candidate, Not Sent

Captured: 2026-06-13T06:38:18Z

## Purpose

Prepare a cleaner not-sent send candidate where the whole five-message series
uses the `RFC/RFT` subject prefix.

This supersedes H209 as the preferred not-sent send candidate. H209 remains
valuable because it caught the recipient propagation issue: cover-letter-only
`To`/`Cc` headers did not address patches 1-4 correctly. H210 keeps H209's
correct command-line recipient model and normalizes the subject prefixes.

No mail was sent.

## Candidate Bundle

- Mac path: `/Users/enzo/projects/homelab/task-packets/kernel/a733-h210-rfc-rft-normalized-sendemail-candidate/`
- Strix path: `/srv/projects/homelab/task-packets/kernel/a733-h210-rfc-rft-normalized-sendemail-candidate/`
- Base: `d9aa2e15caae`
- H200 exact tested head: `de486cb24c361a86cba26738f24332df780872b0`
- Recreated Strix apply-check head: `f36c6468eac1477986b2893f32c845b041571817`

Files:

```text
0000-cover-letter.patch
0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

Subjects:

```text
[RFC/RFT 0/4] clk: sunxi-ng: a733: keep Cubie A7S SDMMC0 path live
[RFC/RFT 1/4] clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
[RFC/RFT 2/4] clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
[RFC/RFT 3/4] clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
[RFC/RFT 4/4] clk: sunxi-ng: a733: keep GIC and CPU peri clocks critical
```

## SHA256

The patch hashes differ from H200/H209 because the email `Subject:` prefixes
were normalized from `PATCH` to `RFC/RFT`. The source hunks are unchanged.

```text
f08381cdca45431e24af2a2e172506239a53852b3bacf037e21a0f8800c5e3be  0000-cover-letter.patch
6cc2b2a3fd5d26b8c36340b2b83369a8c3455af5898756acedc6f29c2e25f01f  0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
865ef2eaaf01b213a80158fae2a8b4338cdf89e9ae90444d37b9080c06d804c7  0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
3f28b742b4e66539d8a5f5cd055103a1cf875b89779a9eb61dd993c2bcb79f6c  0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
70b70b56f834fdc92b51f52988ac356514c21e6b840031db6ccadb7df716d33f  0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## Validation

- `python3 tools/validate/public_hygiene_gate.py --json task-packets/kernel/a733-h210-rfc-rft-normalized-sendemail-candidate`: PASS
- `python3 tools/validate/trailer_gate.py --json task-packets/kernel/a733-h210-rfc-rft-normalized-sendemail-candidate/000[1-4]-*.patch`: PASS
- `git send-email --dry-run` with explicit `--to/--cc` recipients: PASS
- Dry-run result count: five `Result: OK` messages
- Strix `git am --3way` from `d9aa2e15caae`: PASS
- Strix `git diff --check d9aa2e15caae..HEAD`: PASS
- Strix source diff against H200 for `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`: clean

## Send Rule

Do not send H210 now. H204 still lacks confirmed public indexing in checked
views, and H210 exists so the exact RFC/RFT series is ready if a maintainer
asks for patch text or if a later reviewed send decision is made.

Before any real send:

1. Refresh the public thread one more time.
2. Re-run public-hygiene and trailer gates.
3. Re-run `git send-email --dry-run` using explicit `--to/--cc` recipients.
4. Remove `--dry-run` only if the send is intentionally chosen.
