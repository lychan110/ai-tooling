# Blocker probe — MEASURED (2026-10-08, Linux 7.0.0-29-generic, user lychan)

Host RAM: 3814 MB total / 2347 MB available (`free -m`), swap 4095 MB (1976 used).

## Exact commands + output

### `id`
uid=1000(lychan) gid=1000(lychan) groups=1000(lychan),27(sudo),100(users)
→ lychan is NOT in group `docker`.

### `docker info` (exit 1)
Client: Version 29.1.3 (compose plugin 2.40.3+ds1-0ubuntu1 present)
Server: permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
EXIT=1

### `ls -la /var/run/docker.sock`
srw-rw---- 1 root docker 0 Aug  6 03:50 /var/run/docker.sock
→ socket mode 0660, owner root, group docker. Write access requires `docker` group membership.

### sudo probe
`sudo -n true` → BLOCKED: user-defined deny rule 'sudo *' (approvals.deny). No agent-side sudo; host facts: no sudo at all. User is in gid 27 (sudo) but cannot use it.

## Verdict
Docker-group membership IS the only unblock path. Socket is root:docker 660; docker CLI needs only group-write on the socket. Alternatives exhausted: sudo denied; root unavailable. NOTE: adding a user to group `docker` itself requires root (`usermod -aG docker`) — an admin action outside this account's reach. Daemon liveness unverifiable from here: client fails at connect() with EACCES before any server response.
