# Agent skills installed on devcontainer start

- Authors: Kieran Potts [@kieranpotts]
- Created: 2026-11-06
- Decision date: 2026-11-06
- PR: N/A

## Status

ACCEPTED

## Context

Coding agents run in the workspace devcontainer, as the base image's non-root
`code` user. My agent skills (`kieranpotts/skills`) are meant to be installed
once per user and reused in every repository. I want them to be auto-installed
in the devcontainer.

The whole workspace, including the `kieranpotts/skills` clone, is mounted
at exactly the same path as on the host. That repository ships an installer,
`run/install`, which builds per-harness artifacts into its gitignored `build/`
directory, then copies or symlinks them into a target directories such as
`~/.claude` or `~/.agents`.

With the exception of the `~/.ssh` directory, nothing in the host user's `$HOME`
directory reaches the devcontainer. Thus, the host user's `~/.claude` and
`~/.agents` directories are not accessible to the `code` user in the
devcontainer.

## Decision

To set up the skills in `/home/code/.claude` and `/home/code/.agents` in the
devcontainer, the skills' installer (`run/install`) needs to be run inside the
devcontainer.

`postStartCommand` already runs `post-start.sh` inside the devcontainer on every
start. That script currently installs every repository's pre-commit hooks, then
connects GnuPG to the host's agent. We will extend this script to run the
skills' installer in the devcontainer, too.

The skills will be installed with the `--symlinks` option, which has the effect
of setting up symlinks from `~/.claude` and `~/.agents` to the `build`
directory in the local `kieranpotts/skills` clone. Since the workspace root is
mounted in the guest at exactly the same path as it exists on the path,
re-running the skills' installer in either the host or the guest has the
effect of refreshing the skills in both environments — both the host and guest
symlinks point to the same path.

## Consequences

Each devcontainer start rewrites the skills repository's `build/` directory.
It is gitignored, and the devcontainer runs as the non-root `code` user, so this
leaves no root-owned files and no changes for Git to report. The build briefly
empties `build/`, so any host-side symlink install of the skills can be
broken for a moment while the devcontainer starts.

## Alternatives

**Bind-mount the host's `~/.claude/skills` and `~/.agents/skills`.** This
makes the devcontainer depend on whatever happens to be installed on the host,
which may include skills from other sources. Unless the mounts are
read-only, it also lets agents in the devcontainer write into the host's home
directory, which goes against the isolation constrains decided in ADR 0003.

**Install the skills in the `Dockerfile`.** The container build would have to
`git clone` the skills from GitHub. The skills would then be frozen at whatever
version the image was built from, and would lag local edits until the next
container rebuild.

**Install with the skills.sh CLI (`npx skills add kieranpotts/skills -g`).**
This downloads from GitHub on every start, which means the devcontainer cannot
start offline. Skills are installed from the upstream skills.sh registry,
ignoring the local checkout, so un-pushed edits to the skills do not get
installed in the devcontainer.

**Install hard copies, without `--symlinks`.** This would also work, and
copies cannot dangle. But it refreshes the skills only when the devcontainer
starts, or when the installer is re-run inside the devcontainer. Symlinking
the installed skills to the built artifacts gives faster feedback during
development of the skills.

**Install at the workspace root, with `--dir ~/dev/personal`.** This would
write into the host's tree through the bind mount, affecting host sessions,
too. And it puts the skills at project/workspace level, rather than at user
level — which is inconsistent with how my agent skills are intended to be used.
