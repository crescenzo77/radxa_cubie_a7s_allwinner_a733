# Kernel Machine Install Checklist

Status: private operator checklist
Last checked: 2026-06-06
Operator surface: Codex Desktop only

## Purpose

Keep the headless kernel workflow repeatable without installing Docker Desktop
or model runtimes on the Mac. The Mac remains the Codex Desktop dispatcher.
Linux machines run validation, local inference, review, storage, and UART work.

This file records install commands and readiness checks only. It is not a
public kernel-submission artifact.

## Current Readiness Snapshot

Read-only checks on 2026-06-06 showed the pre-repair state:

| host | role | OS | present | missing/useful |
| --- | --- | --- | --- | --- |
| local Mac | dispatcher only | macOS 26.5.1 arm64 | `git`, `rg`, `python3`, `cmake`, Docker CLI | no Docker Desktop/containers desired, no models desired |
| `192.168.50.252` | validation and mixed-GPU model host | Ubuntu 26.04 x86_64 | `git`, `rg`, Docker, Compose v5.1.3, `nvidia-smi`, `vulkaninfo`, `python3`, `cmake`, `ninja` | `clinfo` optional |
| `192.168.50.11` | Strix review and UART host | Ubuntu 26.04 x86_64 | `git`, `rg`, Docker, Compose v5.1.4, `vulkaninfo`, `python3`, `screen`, Cubie UART by-path devices | `cmake`, `ninja`, `picocom`, `minicom`, `clinfo` useful before repair |
| `192.168.50.225` | ThinkCentre Qdrant/mirror host | Ubuntu 26.04 x86_64 | `git`, `rg`, Docker, Compose v5.1.3, `curl`, `jq`, `python3`, `cmake` | `ninja` optional |

All host commands below use IP addresses rather than local names.

Run the read-only readiness gate before installing anything:

```sh
scripts/kernel-machine-readiness
scripts/kernel-machine-readiness --json
scripts/kernel-machine-readiness --strict
```

`--strict` fails only when a required current-workflow check is missing.
Optional tools are reported separately. Latest read-only checks found no
missing required tools, but optional helper packages are still absent on AMD,
Strix, and ThinkCentre; all three Linux hosts require a sudo password for
package repair.

Use the workflow status aggregator when deciding what Codex should do next:

```sh
scripts/kernel-workflow-status
scripts/kernel-workflow-status --json
scripts/kernel-workflow-status --strict
scripts/kernel-workflow-status --runtime-strict
scripts/kernel-workflow-status --maintainer-ready-strict
scripts/kernel-workflow-status --maintainer-ready-blockers
scripts/kernel-workflow-status --maintainer-next-action
scripts/kernel-workflow-status --maintainer-operator-brief-shell
scripts/kernel-workflow-status --next-action
scripts/kernel-workflow-status --next-command
scripts/kernel-workflow-status --next-shell
```

It combines machine readiness, local model offload status, idle review ledger
state, public repo backup state, and the Cubie runtime gate into one concise
read-only report. Override `KERNEL_PUBLIC_REPO` when checking a different
public-facing kernel checkout. Use `--strict` for workflow health and
`--runtime-strict` only for gates that must fail until exact Cubie hardware
runtime proof exists. Use `--maintainer-ready-strict` only for a pre-submission
or patch-prep stop gate; it additionally requires the A733 export shape and
public hygiene gates to pass. Use `--maintainer-ready-blockers` when a compact
blocker list is easier to hand to a local review lane than the full dashboard.
Use `--maintainer-next-action` when Codex needs the ordered next step toward
maintainer readiness rather than the generic Cubie runtime action.
Use `--maintainer-operator-brief-shell` when the operator should preview the
live proof step before entering sudo credentials or UART.

## Mac Dispatcher

Do not install Docker Desktop or run local models on the Mac for this workflow.
The only expected Mac-side packages are normal dispatcher tools:

```sh
brew install git ripgrep python@3.12 cmake
```

Readiness check:

```sh
git --version
rg --version
python3 --version
cmake --version
```

If container work ever becomes necessary on the Mac, pause and discuss Colima
or another lightweight option first.

## AMD `192.168.50.252`

AMD is the validation lab and mixed-GPU local-model host. It runs the Linux
validation container, stores proof logs, and hosts both the RTX 3090 fast lane
and the RX 7900XT research lane.

Install or repair baseline packages:

```sh
sudo apt update
sudo apt install -y \
  git ripgrep curl jq python3 python3-venv python3-pip \
  build-essential cmake ninja-build pkg-config \
  perl bc bison flex libssl-dev libelf-dev dwarves \
  device-tree-compiler yamllint sparse \
  docker.io docker-compose-plugin \
  vulkan-tools mesa-vulkan-drivers clinfo
sudo usermod -aG docker,render,video "$USER"
```

NVIDIA container runtime check:

```sh
nvidia-smi
docker compose version
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu24.04 nvidia-smi
```

If the final command cannot see the RTX 3090 from inside Docker, install or
repair NVIDIA Container Toolkit using NVIDIA's current Ubuntu apt instructions,
then run:

```sh
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Workflow checks from Codex Desktop:

```sh
scripts/kernel-proof status
scripts/kernel-proof self-test
scripts/kernel-token-offload status
```

## Strix `192.168.50.11`

Strix is the long-review lane and Cubie UART host. It should keep Vulkan first
unless Vulkan fails a concrete agent/review requirement.

Install or repair baseline packages:

```sh
sudo apt update
sudo apt install -y \
  git ripgrep curl jq python3 python3-venv python3-pip \
  build-essential cmake ninja-build pkg-config \
  docker.io docker-compose-plugin \
  vulkan-tools mesa-vulkan-drivers clinfo \
  screen picocom minicom
sudo usermod -aG docker,render,video,dialout "$USER"
```

Readiness checks:

```sh
docker compose version
vulkaninfo --summary
groups
ls -l /dev/serial/by-path
screen --version
picocom --version
```

Workflow checks from Codex Desktop:

```sh
scripts/kernel-token-offload status
scripts/cubie-uart list
scripts/cubie-runtime-gate --skip-network --json
```

## ThinkCentre `192.168.50.225`

ThinkCentre is the private Qdrant/cortex and mirror host. It should not become
the required live patching authority; it stores searchable evidence and mirrors.

Install or repair baseline packages:

```sh
sudo apt update
sudo apt install -y \
  git ripgrep curl jq python3 python3-venv python3-pip \
  build-essential cmake ninja-build pkg-config \
  docker.io docker-compose-plugin openssh-server
sudo usermod -aG docker "$USER"
sudo systemctl enable --now ssh
```

Readiness checks:

```sh
docker compose version
docker ps --format '{{.Names}} {{.Status}}'
git --version
rg --version
```

Workflow checks from Codex Desktop:

```sh
scripts/kernel-cortex status
scripts/kernel-research-query "A733 CCU pinctrl RFC overlap"
```

## Cubie3 `192.168.50.95`

Do not install development tooling here unless runtime evidence collection
requires it. Cubie3 is a target board, not a build host.

Optional runtime-inspection packages:

```sh
sudo apt update
sudo apt install -y \
  curl jq iproute2 ethtool usbutils i2c-tools device-tree-compiler
```

Current required interactive handoff:

```sh
scripts/cubie-corrected-root-operator-brief
ssh -tt enzo@192.168.50.11 'cd /srv/projects/homelab && git pull --ff-only mac-mini main && scripts/cubie-interactive-root-install-session --confirm-target-ip 192.168.50.95'
```

Codex Desktop runs on the Mac, but live Cubie root-install, UART, and U-Boot
selection work belongs on Strix because the serial adapters are attached there.

## Permanent Exclusion

Do not probe, stage, boot, or install anything for kernel work on:

```text
192.168.50.65
```

It is reserved for Wyze camera object detection.
