# No Docker in the workspace devcontainer

- Authors: Kieran Potts [@kieranpotts]
- Created: 2026-10-30
- Decision date: 2026-10-30
- PR: N/A

## Status

ACCEPTED

## Context

Coding agents run in the workspace devcontainer, and they MUST NOT have root on
the host. Any way of giving the container the host's Docker daemon gives root
on the host. For example, `docker run -v /:/host` mounts the host's whole
filesystem.

Nine repositories ran scripts that need a Docker daemon. ADR moved three of
these to native builds, leaving siz repositories that still depend on a Docker
daemon:

| Repository              | Scripts                              |
| ----------------------- | ------------------------------------ |
| asciibook               | `run/start`, `run/build`, `run/stop` |
| docker-devcontainer     | `run/build`, `run/publish`           |
| docker-latex (archived) | `run/build`, `run/publish`           |
| gh-runner               | `run/build`                          |
| json-schema             | `run`                                |
| the-timeless-way        | `run/start`, `run/build`, `run/stop` |

The options are:

- Give the devcontainer a Docker daemon of its own that is not privileged on the
  host.

- Give the devcontainer no Docker at all. Repositories that depend on a Docker
  daemon will be required to run their scripts on the host, not in the container.

The host runs Pop!_OS 24.04 (Ubuntu noble), on kernel 7.2.6, with Docker Engine
29.9.2.

## Decision

We will have no Docker in the workspace devcontainer: no Docker CLI or daemon in
the image, no devcontainer `features`, and no mount of the host's Docker socket.

The consequence is that humans run the six repositories' Docker scripts in a
terminal on the host, against the host's Docker Engine. Coding agents, running
in the devcontainer, will not be able to run these scripts.

Each script is modified to check for `docker` on `PATH` first. If it is missing,
the script stops with a message to run it on the host, rather than failing with
`docker: command not found`. (gh-runner's `run/agent` has no check, because it
already falls back to `python3` without Docker.)

## Consequences

There is no route to root on the host through Docker from inside the container.
The container stays simple, and the host needs no new software.

Agents cannot build, preview, or test the six repositories, so they cannot check
their own changes there. Each such check is a hand-off to a human at a host
terminal. Humans switch between the container and a host terminal when working
on those repositories. The cost is small in practice.

## Alternatives

[**Sysbox**](https://github.com/nestybox/sysbox)  is a container runtime
(`sysbox-runc`) installed on the host beside Docker Engine. A container started
with `--runtime=sysbox-runc` can run its own Docker daemon without `--privileged`.
It does this by putting the container in a Linux user namespace, so its root
maps to an unprivileged user on the host. This would have the happy side-effect
of hardening the container itself, because the base image gives the `code` user
passwordless `sudo`. However, some issues reported on GitHub suggest that
Sysbox is unstable and increases risk on the host itself.

**Mount the host's Docker socket** (the `docker-outside-of-docker` feature).
Access to the socket is root on the host.

**Docker-in-Docker with the default runtime** (the `docker-in-docker` feature).
It needs `--privileged`, which is root on the host.

**A filtering proxy in front of the host's socket.** It cannot reliably stop
`docker run -v /:/host` and the like, so in practice it is still root on the host.

**Rootless Docker on the host, with its socket mounted in.** This is not root,
but the daemon runs as the host user. Through it, an agent could mount the whole
home directory, including the GnuPG secret keys, the password store, and the
shell startup files that run code on the host. That is a full compromise of the
user account.
