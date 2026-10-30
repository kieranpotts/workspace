# Workspace

The root of Kieran's personal multi-repo dev tree. This repository holds the
tooling that clones and synchronizes every sibling project under
`~/dev/personal/` using the "adjacent worktree" pattern (bare clone +
per-branch worktrees), plus the assets (VS Code workspace file, devcontainer,
`AGENTS.md` template) that get symlinked to the root of that tree.

Do not confuse this file with [`root/AGENTS.md`](./root/AGENTS.md). That file
describes the *sibling-project tree* once installed (it is symlinked to
`~/dev/personal/AGENTS.md`). This file describes this repository's own
tooling (`repos.yaml`, `run/install.py`, `root/`).

The capitalized words REQUIRED, MUST, MUST NOT, RECOMMENDED, SHOULD,
SHOULD NOT, OPTIONAL, and MAY are to be interpreted as described in
[IETF RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Tech stack

- Python 3 (`run/install.py`), with `pyyaml` as its only dependency
  (`requirements.txt`).
- Docker, for building the workspace devcontainer
  (`root/.devcontainer/Dockerfile`). The container itself has no Docker.
- pre-commit, for commit-message validation.

## Project structure

- **[repos.yaml](./repos.yaml)** \
  The manifest of every managed repository: `name`, `url`, and a `worktrees`
  map (directory name → branch) per repo. Adding, removing, or renaming a
  worktree entry here is how repos are declared.

- **[run/install.py](./run/install.py)** \
  Reads `repos.yaml` and, for each repo: bare-clones it if not already present
  (`<name>/.bare`, `<name>/.git` pointer file), writes a project-root
  `AGENTS.md` from `run/AGENTS.template.md` if one doesn't already exist,
  fetches, and fast-forwards every declared worktree. Also symlinks the
  `LINKED_ASSETS` (`personal.code-workspace`, `AGENTS.md`, `CLAUDE.md`,
  `.devcontainer`, `.zed`) from `root/` into `~/dev/personal/`, and runs
  `pre-commit install` in any cloned repo that has a `.pre-commit-config.yaml`.

- **[run/AGENTS.template.md](./run/AGENTS.template.md)** \
  Template written as `AGENTS.md` into each newly-cloned project root
  (outside any worktree). Orients agents to the bare-clone/worktree layout.
  Not the same file as this AGENTS.md or `root/AGENTS.md`.

- **[root/](./root)** \
  Contents surfaced at `~/dev/personal/` via symlink: `personal.code-workspace`
  (VS Code multi-root workspace), `AGENTS.md` (workspace-wide agent guide,
  describing the sibling-project tree), `.devcontainer/` (the one devcontainer
  for the whole workspace, built on the `kieranpotts/devcontainer` base image,
  running as its non-root `code` user, with no Docker inside), and
  `.zed/settings.json` (Zed's project settings for the whole tree, mirroring
  the editor settings in `personal.code-workspace`).

- **[docs/](./docs)** \
  Requirements, installation, and usage docs for this workspace tooling.

## Tools

- `pip install -r requirements.txt` to install `pyyaml` before running the
  installer.
- `python3 run/install.py` to clone/update all repos declared in
  `repos.yaml` and refresh the symlinked root assets.
- `docker build -t personal-workspace root/.devcontainer` to verify the
  devcontainer image builds. Run it on the host: there is no Docker in the
  devcontainer.

## Rules

- MUST add a `repos.yaml` entry (and run `python3 run/install.py`) to bring a
  new repository into the workspace, rather than cloning it manually. Manual
  clones are not tracked and will not be kept in sync.

- MUST commit changes to `repos.yaml`. It is the single source of truth for
  which repositories and worktrees exist.

- MUST NOT hand-edit a generated project-root `AGENTS.md` (the one written by
  `install.py` from `run/AGENTS.template.md`) expecting it to persist.
  `install.py` only writes it when absent, but the template is the source of
  truth for its content.

- Worktrees created manually with `git worktree add` (outside `repos.yaml`)
  MUST be understood as untracked: `install.py` will not recreate or remove
  them.

- To remove a repository, delete its `repos.yaml` entry and run
  `rm -rf ~/dev/personal/<name>`.

## References

The following technical standards (TS) govern this project. Fetch and ingest
the relevant standards as-and-when required for the task at hand.

- [**TS-9: Version Control**](https://kieranpotts.com/standards/009) \
  Use when working with Git. Covers commits, branching, merging, integration
  strategies, cutting releases, and configuring Git/PR/CI tooling.

- [**TS-35: Python**](https://kieranpotts.com/standards/035) \
  Use when writing, reviewing, or refactoring Python code.

- [**TS-58: Docker**](https://kieranpotts.com/standards/058) \
  Use when designing Dockerfiles, building Docker images, or running Docker
  containers.
