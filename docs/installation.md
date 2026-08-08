# Installation

> [!NOTE]
> On Windows, the workspace SHOULD be established in WSL. The `devtools` repository SHOULD also be cloned directly in the host OS, manually, and optionally the `dotfiles` repository too.

## Bootstrapping the workspace

Start by cloning this repository. It is RECOMMENDED to clone it into a temporary location initially. The installer script will then set up this and other repositories properly.

```sh
git clone git@github.com:kieranpotts/workspace.git ~/dev/tmp
cd ~/dev/tmp
```

Create and activate a virtual environment, then install the dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The `.venv` directory is excluded from version control. The `python3 -m venv` and `pip install` steps are one-time operations. However, the virtual environment must be re-activated in each new shell session:

```sh
source .venv/bin/activate
```

Now you can run this script to clone and sync all the other repositories:

```sh
python3 run/install.py
```

Alternatively, rather than activating the Python virtual environment, the script can be invoked directly without activation:

```sh
.venv/bin/python run/install.py
```

The `install.py` script reads `repos.yaml` and clones any repository not yet present locally. Each repository is checked out using the adjacent worktree pattern, rooted under `~/dev/personal/` – see [Usage](./usage.md) for details of the worktree filesystem structure.

For each already-cloned repository, the installer fetches from the remote then fast-forwards every working tree. It is safe to run multiple times.

The base directory (`~/dev/personal/`) is configurable via the `REPOS_DIR` constant at the top of [run/install.py](../run/install.py).

The `install.py` also clones this workspace repository, so it is now safe to delete the temporary clone of this repository you made at the start.

## Workspace assets

The installer surfaces the contents of this repository's [`root/`](../root) directory at the root of the dev tree (`~/dev/personal`), via relative symlinks, so the entire collection of repositories can be opened as a single VS Code workspace or devcontainer from one place, and so `AGENTS.md`/`CLAUDE.md` are visible to agents working in any sibling project:

```
~/dev/personal/personal.code-workspace  →  kieranpotts/workspace/default/root/personal.code-workspace
~/dev/personal/AGENTS.md                →  kieranpotts/workspace/default/root/AGENTS.md
~/dev/personal/CLAUDE.md                →  kieranpotts/workspace/default/root/CLAUDE.md
~/dev/personal/.devcontainer            →  kieranpotts/workspace/default/root/.devcontainer
```
