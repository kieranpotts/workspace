# Workspace

The root of Kieran's personal multi-repo dev tree. This repository holds the
tooling that clones and synchronizes every sibling project under
`~/dev/personal/` using the "adjacent worktree" pattern (bare clone +
per-branch worktrees), plus the assets (VS Code workspace file, devcontainer,
`AGENTS.md` template) that get symlinked to the root of that tree.

Do not confuse this file with [`root/AGENTS.md`](./root/AGENTS.md) — that file
describes the *sibling-project tree* once installed (it is symlinked to
`~/dev/personal/AGENTS.md`); this file describes this repository's own
tooling (`repos.yaml`, `run/install.py`, `root/`).

The capitalized words REQUIRED, MUST, MUST NOT, RECOMMENDED, SHOULD,
SHOULD NOT, OPTIONAL, and MAY are to be interpreted as described in
[IETF RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Tech stack

- Python 3 (`run/install.py`), with `pyyaml` as its only dependency
  (`requirements.txt`).
- Docker, for the devcontainer (`root/.devcontainer/Dockerfile`).
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
  `LINKED_ASSETS` (`personal.code-workspace`, `AGENTS.md`, `.devcontainer`)
  from `root/` into `~/dev/personal/`, and runs `pre-commit install` in any
  cloned repo that has a `.pre-commit-config.yaml`.

- **[run/AGENTS.template.md](./run/AGENTS.template.md)** \
  Template written as `AGENTS.md` into each newly-cloned project root
  (outside any worktree) — orients agents to the bare-clone/worktree layout.
  Not the same file as this AGENTS.md or `root/AGENTS.md`.

- **[root/](./root)** \
  Contents surfaced at `~/dev/personal/` via symlink: `personal.code-workspace`
  (VS Code multi-root workspace), `AGENTS.md` (workspace-wide agent guide,
  describing the sibling-project tree), and `.devcontainer/` (Ubuntu-based
  container definition, non-root `vscode` user with host-matching UID/GID).

- **[docs/](./docs)** \
  Requirements, installation, and usage docs for this workspace tooling.

## Tools

- **`pip install -r requirements.txt`** to install `pyyaml` before running the installer.
- **`python3 run/install.py`** to clone/update all repos declared in `repos.yaml` and refresh the symlinked root assets.
- **`docker build -f root/.devcontainer/Dockerfile -t personal-workspace .`** to verify the devcontainer image builds.

## Rules

- MUST add a `repos.yaml` entry (and run `python3 run/install.py`) to bring a
  new repository into the workspace, rather than cloning it manually — manual
  clones are not tracked and will not be kept in sync.

- MUST commit changes to `repos.yaml` — it is the single source of truth for
  which repositories and worktrees exist.

- MUST NOT hand-edit a generated project-root `AGENTS.md` (the one written by
  `install.py` from `run/AGENTS.template.md`) expecting it to persist —
  `install.py` only writes it when absent, but the template is the source of
  truth for its content.

- Worktrees created manually with `git worktree add` (outside `repos.yaml`)
  MUST be understood as untracked: `install.py` will not recreate or remove
  them.

- To remove a repository, delete its `repos.yaml` entry and run
  `rm -rf ~/dev/personal/<name>`.

## References

This project follows Kieran Potts' technical standards. Read the relevant
standard(s) below for the current task; their RFC 2119 rules MUST be followed
unless explicitly overridden elsewhere in this file.

- **[TS-9: Version Control](https://raw.githubusercontent.com/kieranpotts/standards/refs/heads/latest/dev/src/modules/ROOT/partials/009/AGENTS.md)**
- **[TS-35: Python](https://raw.githubusercontent.com/kieranpotts/standards/refs/heads/latest/dev/src/modules/ROOT/partials/035/AGENTS.md)**
- **[TS-58: Docker](https://raw.githubusercontent.com/kieranpotts/standards/refs/heads/latest/dev/src/modules/ROOT/partials/058/AGENTS.md)**
