# Patch Directory

No upstream candidate patches are published on this branch yet.

Clean candidate code is published as branches in the Linux fork:

```text
https://github.com/crescenzo77/linux.git
candidate/a733-pinctrl-clean
candidate/a733-ccu-clean
candidate/a733-board-binding-clean
candidate/a733-mmc-binding-clean
candidate/a733-platform-clean
```

Future patches placed here must be generated from a clean kernel tree, apply
with `git am`, and pass the checks listed in
[docs/upstream-discipline.md](../docs/upstream-discipline.md).

Diagnostic lab patches belong outside this public branch.
