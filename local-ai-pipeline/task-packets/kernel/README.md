# Kernel Task Packets

Task packets are the Phase 0 patch-intent gate. Create one before asking any
model to edit kernel code.

Example:

```sh
scripts/kernel-task-packet a733-example \
  --title "Describe the narrow kernel change" \
  --board cubie3 \
  --subsystem "arm64 dts" \
  --target-file arch/arm64/boot/dts/allwinner/example.dts \
  --proof "git diff --check" \
  --proof "scripts/checkpatch.pl --strict"
```

The packet starts in `draft` status. It does not authorize candidate branch
promotion, trailers, or email submission.
