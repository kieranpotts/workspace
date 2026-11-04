# One devcontainer for the whole workspace

- Authors: Kieran Potts [@kieranpotts]
- Created: 2026-10-29
- Decision date: 2026-10-30
- PR: N/A

## Status

ACCEPTED

## Context

Every repository in the workspace had a devcontainer of its own. Although they
share the same base image, that's ~40 devcontainer configurations to maintain
separately. The devcontainer configs mostly differed in their `postCreateCommand`
extensions, but had started to drift in other ways, increasing maintenance
cost.

There are many cross-repository dependencies between my personal projects. The
container-per-repository model does not suit cross-repository work. As coding
agents increasingly do that work, so they need an isolated environment that
encapsulates all of the relevant repositories.

The constraints are:

- Devcontainers MUST work in VS Code, Zed Editor, and IntelliJ IDEA.

- Coding agents run in the container. Coding agents MUST NOT get root on the
  host.

- The links between each bare clone (`<owner>/<name>/.bare`) and its worktrees
  are absolute paths. This means they will only resolve if the tree is mounted
  at the same path as on the host.

## Decision

I will migrate to a single workspace-level devcontainer, into which all of
my personal repositories will be mounted. All repository-level devcontainer
configurations will be removed.

The existing base image, `kieranpotts/devcontainer:latest`, is kept. The base
image provides pre-commit, mise, Node and npm, Python, ripgrep, GnuPG, and
ShellCheck. All of these are on `PATH` for every process, not only interactive
shells, so Git hooks, editor tasks, and agents find them.

The whole tree is bind-mounted at its host path (`workspaceMount`), so the bare
clones' links to their worktrees resolve.

The container is named `personal-workspace` (via `runArgs`).

The host's Git config files and `~/.ssh` are mounted read-only, as before.
`initializeCommand` creates any missing mount sources, because Docker will not
start a container with a missing bind mount source.

On every start, `postStartCommand` runs `post-start.sh`, which does two things.
(1) It runs `pre-commit install` in every repository that has a
`.pre-commit-config.yaml` file at its root. Git hooks are written to each bare
clone's `hooks/` directory, so every worktree under a repository is covered by
the same pre-commit hooks. (2) If the code editor has not forwarded the host's
GnuPG agent, the script instead points the container's `gpg` at the host's agent.
VS Code forwards the agent; Zed does not. This allows commit messages, generated
from either VS Code or Zed, to be signed.

However, the container will not install any repository's other dependencies or
toolchains. Each repository's own install, eg. `./run/install` or `npm ci`, is
required to be run manually. Each repository's `README.md`, `CONTRIBUTING.md`,
or `AGENTS.md` says how.

`postStartCommand` changes into the workspace folder first, because otherwise
Zed runs lifecycle commands from `/data` by default.

Existing VS Code settings and extensions are configured in `devcontainer.json`.
It omits extensions that run on the host side, such as Dev Containers, WSL,
Container Tools, and VS Code Speech. It also leaves out extensions that cannot
work in the container, such as the ones that call Ollama on the host's
`localhost`. Zed reads `auto_install_extensions` from user settings only, not
from project settings or `devcontainer.json`, so Zed extensions such as
`asciidoc`, `env`, and `make` would need to be installed in the running
container manually.

## Consequences

There is one devcontainer to maintain, and repositories can no longer drift
apart. Humans and agents can work across repositories in one isolated
environment.

Opening a single repository's folder no longer offers a devcontainer to launch
into. Users should now open the workspace root, or attach to the running
container and open the workspace root folder from there.

The following behavior was verified through a proof-of-concept.

`git commit -S` from the guest makes a signed commit. VS Code signs through its
own forwarded agent, and Zed through the redirect that `post-start.sh` writes.

Files written in the container are owned by the host user (`kieran`), because
the guest `code` user has the same UID.

`node` and `npm` work under `sh -c`, with no shell startup files read. A
repository's own mise toolchain works in the container.

Pre-commit hooks work on either side, as long as the `pre-commit` framework is
installed and instantiated in both the host and the guest.

A toolchain change for one repository rebuilds the container for all of them.
To keep that rare, each repository pins its own toolchain in a `mise.toml` file,
instead of having it baked into an image.

Toolchains that mise installs in the container live in the container's own
filesystem (`/home/code/.local/share/mise`), so they are lost on every rebuild,
and each repository's install has to be run again. But dependencies installed
into the repository itself, such as `node_modules`, survive rebuilds. If
reinstalling gets tiresome, a named volume mounted at
`/home/code/.local/share/mise` would keep the toolchains.

GnuPG forwarding works on Linux hosts only. It depends on `$XDG_RUNTIME_DIR/gnupg`
and on `gpgconf` being installed on the host. On other hosts, `initializeCommand`
fails and the container will not start, unless the GnuPG parts of
`initializeCommand` and the two GnuPG mounts are removed.

## Alternatives

**Install every repository's dependencies on create.** Most of those toolchains
would go unused in any one session, the first start would be slow, and one
repository's failing install would stop the whole container from starting.

**Reference the base image directly from `devcontainer.json`.** This is one
file fewer, but it leaves no place for workspace-wide tooling. Switching later
is trivial, either way.

**`forwardPorts` instead of `appPort`.** `forwardPorts` depends on the editor's
own port forwarding, which differs between VS Code and Zed.
