# Current Slice

## Slice 11: Prepare Codex SSH readiness

Prepare Codex SSH readiness without changing remote hosts, live services, SSH configuration, or keys.

## Purpose

Make Codex useful without repeated copy/paste by ensuring `strix` can inspect `amd` and `thinkcentre` over SSH predictably.

Slice 10 is paused until SSH readiness is understood. The immediate blocker observed during Slice 10 was:

    Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf

## Scope

Diagnostics planning only:

- Diagnose the local SSH client config problem shown above.
- Verify hostname resolution for `amd` and `thinkcentre`.
- Verify whether passwordless SSH already works.
- Propose safe SSH key setup if needed.
- Document that agents may inspect remote hosts read-only by SSH.
- Require explicit approval before remote mutation.

## Constraints

- Do not run `sudo`.
- Do not modify remote hosts.
- Do not change live services.
- Do not edit SSH config yet.
- Do not create SSH keys yet.
- Do not print secrets.
- Do not capture passwords.
- Do not edit remote files.
- Do not generate SSH keys until explicitly approved.
- Do not make live production changes based on network responses without explicit approval.

## Read-Only Diagnostic Command Block

The next execution step should be limited to read-only diagnostics:

    hostname
    id
    ls -ld /etc/ssh /etc/ssh/ssh_config.d /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
    stat -c '%U:%G %a %n' /etc/ssh /etc/ssh/ssh_config.d /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
    getent hosts amd thinkcentre
    ssh -F /dev/null -o BatchMode=yes -o PasswordAuthentication=no -o ConnectTimeout=5 amd 'hostname'
    ssh -F /dev/null -o BatchMode=yes -o PasswordAuthentication=no -o ConnectTimeout=5 thinkcentre 'hostname'

If the diagnostic output shows SSH keys or host aliases are missing, stop and write an approval brief before generating keys, editing SSH config, or changing remote `authorized_keys`.

## Acceptance Criteria

- Repo docs explain what must be checked.
- The next command block is limited to read-only diagnostics.
- No remote hosts are modified.
- No live services are changed.
- Git diff is shown for review.
- Stop before commit.
