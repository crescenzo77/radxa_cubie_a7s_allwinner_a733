# AI Assistance Policy

This repository may use AI assistance for note organization, code review, and
experimental patch drafting. Kernel submissions require stricter handling.

For Linux kernel patches:

- AI agents do not certify the DCO.
- AI agents must not add `Signed-off-by:`.
- A human must review every line and accept full responsibility.
- AI involvement must be disclosed when it contributes to a patch.
- The disclosure must use the kernel-documented `Assisted-by:` format.

Example trailer for a future kernel patch, adjusted to the actual tools used:

```text
Signed-off-by: Crescenzo <crescenzo@gmail.com>
Assisted-by: OpenAI:GPT-5 Codex
```

Do not add this trailer mechanically. Add it only to actual kernel patches where
AI assistance contributed to the final content and after human review.
