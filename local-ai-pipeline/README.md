# Local Kernel Proof Pipeline

This directory backs up the local kernel-validation pipeline used for the
Radxa Cubie A7S / Allwinner A733 work.

Codex Desktop remains the operator surface. The Mac dispatches work over SSH,
but validation runs on Linux hosts:

- `192.168.50.252`: AMD validation host and proof-log store
- `192.168.50.11`: Strix review and Cubie UART host

The proof logs are the authority for pass/fail claims. Model review output is
advisory and must not replace terminal proof.

Important entry points:

- `runbooks/kernel-layout.md`
- `runbooks/kernel-proof-harness.md`
- `runbooks/kernel-review-handoff.md`
- `scripts/kernel-proof`
- `scripts/kernel-maintainer-review`
- `tools/validate/proof_runner.py`
- `task-packets/kernel/`
- `tools/proof-logs/`

Do not add human trailers, create a submission series, or send patches from
this pipeline without explicit human approval.
