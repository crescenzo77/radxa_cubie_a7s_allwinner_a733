# Cubie A7S Hardware Lab

Status: board facts recorded, automation not enabled
Operator surface: Codex Desktop only

## Immediate Kernel Targets

The next kernel work is for two Radxa Cubie A7S devices:

- `cubie2`: `192.168.50.85`
- `cubie3`: `192.168.50.95`

Quick network observation:

- `192.168.50.95` answered a one-packet ping check.
- `192.168.50.85` did not answer the same quick check.

Treat reachability as a live lab condition, not a permanent fact.

## UART Host

Both Cubie UART connections terminate on `192.168.50.11`.

Observed serial devices on `192.168.50.11`:

- `/dev/ttyUSB0`
- `/dev/ttyUSB1`
- `/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0`
  currently points to `/dev/ttyUSB1`

Do not assume the board-to-tty mapping yet. Confirm by capturing boot output
from one board at a time.

Use:

```sh
scripts/cubie-uart list
scripts/cubie-uart capture /dev/ttyUSB1 cubie3-boot-probe 30
scripts/cubie-uart pull-logs
```

UART capture logs are stored on `192.168.50.11` under:

```text
/srv/projects/cubie-uart/logs/
```

Pulled copies are ignored locally under:

```text
tools/hardware-logs/cubie-uart/
```

## Power Control

There are two Wi-Fi home automation switches formerly used to power down and
power on the Cubie boards.

Current status:

- switch IPs are not recorded here yet
- switch API/control method is not recorded here yet
- switch-to-board mapping is not confirmed here yet
- no automated power cycling is enabled

Rules:

- never power-cycle a board from the pipeline until the switch mapping is
  confirmed
- require explicit human approval before any power-off or power-on action
- log every power event with board, switch, timestamp, reason, and operator
- capture UART before and after power events when debugging boot behavior

## Future Hardware-Lab Tools

Add narrow tools only after mapping is confirmed:

- `uart_list_devices`
- `uart_capture`
- `uart_capture_boot_window`
- `power_status`
- `power_on_confirmed`
- `power_off_confirmed`
- `power_cycle_confirmed`

Power tools must require an explicit board ID and confirmed switch ID. They
must not accept vague targets such as "the board" or "both boards".
