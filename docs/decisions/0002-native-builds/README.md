# Native builds for applyto, website, and resume

- Authors: Kieran Potts [@kieranpotts]
- Created: 2026-10-30
- Decision date: 2026-10-30
- PR: N/A

## Status

ACCEPTED

## Context

Three repositories run their builds in Docker containers:

- **applyto** builds the cover letter with
`docker run asciidoctor/docker-asciidoctor:1.108`. Its devcontainer has the
`docker-outside-of-docker` feature, which mounts the host's Docker socket, so
that it could.

- **website** runs Node and Antora through a `Dockerfile` and `docker-compose.yml`,
for its builds and its local preview servers.

- **resume** compiles the CV with `pdflatex` in the `kieranpotts/latex` image,
through `run/start`, `docker exec`, and `run/stop`.

After ADR 0001, agents now run in a workspace-level devcontainer, not in
repository-level ones. A constraint of ADR 0001 is that agents running in the
shared devcontainer MUST NOT get root access on the host. Access to the host's
Docker daemon gives root on the host, so these builds cannot use it from the
devcontainer — see ADR 0003.

## Decision

The build scripts for applyto, website, and resume will now be run natively, on
both the host and guest systems, rather than in a running Docker container
(or devcontainer).

Each repository will pin its toolchain in `mise.toml`, and its scripts run the
tools through `mise exec`. That is the same on the host, in the devcontainer,
and in CI, whether or not mise is activated in the calling shell.

There is one code path per repository, not a Docker path and a native one.

## Consequences

Each toolchain is installed per machine, and per devcontainer, by hand
(eg. `make setup`, `run/install`). Toolchains installed in the devcontainer are
lost when it is rebuilt — see ADR 0001.

The pins have to be kept to what the Docker images used to provide.

For the website's preview servers to listen on ports 8080 and 8081 in the
devcontainer, the devcontainer publishes those ports on the host --- see ADR 0001.

## Alternatives

**Keep the Docker builds, and give the devcontainer Docker.** Every way of doing
that either gives root on the host or puts the host at risk. See ADR 0003.

**Keep the Docker builds, and run them on the host only.** Every build would be
a hand-off to a human.

**Offer both a Docker build and a native one.** That is two code paths per
repository to keep producing identical output.
