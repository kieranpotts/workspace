# Root

This repository serves as the root for all my personal code repositories. It includes:

- Scripts to automate the cloning and synchronization of all my personal software projects.
- A VS Code workspace configuration.
- A devcontainer to simplify the running of my whole personal workspace in an isolated environment.

## Requirements

[Git LFS](https://git-lfs.com/) SHOULD be installed before cloning the repositories. This is required to download PDFs and other large files from some repositories. But the `git clone` operation will succeed without it.

It is RECOMMENDED to clone and run the environment [bootstrapping script](https://github.com/kieranpotts/bootstrap) first. This will install Git LFS and other dependencies.

Python 3 is required to run the management scripts. Create and activate a virtual environment, then install the dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The `.venv` directory is excluded from version control. The `python3 -m venv` and `pip install` steps are one-time operations. However, the virtual environment must be re-activated in each new shell session:

```sh
source .venv/bin/activate
```

Alternatively, the script can be invoked directly without activation:

```sh
.venv/bin/python run/install.py
```

## Usage

> **Note:** On Windows, the workspace SHOULD be established in WSL. The `devtools` repository SHOULD also be cloned directly in the host OS, manually, and optionally the `dotfiles` repository too.

Start by cloning this repository. It is RECOMMENDED to clone it into `~/dev/kieranpotts/workspace` so that the root repository sits alongside all the other projects that `install.py` will place under `~/dev/`:

```sh
git clone git@github.com:kieranpotts/root.git ~/dev/kieranpotts/workspace
cd ~/dev/kieranpotts/workspace
```

Then clone and sync all other repositories:

```sh
python3 run/install.py
```

This reads `repos.yaml` and clones any repository not yet present locally. Each repository is checked out using the [adjacent worktree pattern](https://github.com/kieranpotts/standards), rooted under `~/dev/` (regardless of where this repository is located):

```
~/dev/<name>/.bare      — bare clone (Git internals only)
~/dev/<name>/.git       — file pointing at .bare, so git commands work from the project root
~/dev/<name>/<branch>   — working tree checked out at <branch>
```

For example, a repo with `name: kieranpotts/specs` and `branch: dev` is placed at `~/dev/kieranpotts/specs/.bare` (bare clone) with a working tree at `~/dev/kieranpotts/specs/dev`.

For each already-cloned repository it fetches from the remote then fast-forwards every working tree. It is safe to run multiple times.

The base directory (`~/dev/`) is configurable via the `REPOS_DIR` constant at the top of [run/install.py](run/install.py).

The `install.py` script does not sync the root repository itself. Run `git pull` to do that in the normal way.

## Managing repositories

All repositories are defined in `repos.yaml`. Each entry has three fields:

```yaml
repos:
  - name: repository-name
    url: git@github.com:kieranpotts/repository-name.git
    worktrees:
      default: main
```

The `worktrees` map declares one or more named worktrees. The key is the directory name under the project root; the value is the branch to check out. For example, the entry above creates:

```
~/dev/repository-name/.bare      — bare clone
~/dev/repository-name/.git       — pointer file
~/dev/repository-name/default    — working tree at branch `main`
```

A repo can declare multiple worktrees:

```yaml
repos:
  - name: my-project
    url: git@github.com:kieranpotts/my-project.git
    worktrees:
      default: v2/dev
      v1: v1/dev
```

This creates two working trees: `~/dev/my-project/default` (branch `v2/dev`) and `~/dev/my-project/v1` (branch `v1/dev`).

To add a repository, add an entry to `repos.yaml` and run `python3 run/install.py`. To remove a repository, delete its entry from `repos.yaml` and remove its project directory (which holds the bare clone and all worktrees):

```sh
rm -rf ~/dev/<name>
```

Changes to `repos.yaml` should be committed.

## Manual worktree management

The `install.py` script only manages the worktrees declared in `repos.yaml`. For temporary or experimental work, you can add additional worktrees manually using standard Git commands from the project root (eg. `~/dev/kieranpotts/my-project`):

```sh
# Add a new worktree for an existing remote branch.
git worktree add feature-branch origin/feature-branch

# Add a new worktree and create a local branch from the current HEAD.
git worktree add -b temp-fix ../temp-fix

# List all worktrees (including the bare repo).
git worktree list

# Remove a worktree directory and unregister it.
git worktree remove feature-branch

# If a worktree dir was deleted manually, clean up the stale entry.
git worktree prune
```

Worktrees created manually are NOT tracked by `install.py`. They will not be recreated on subsequent runs, and they will not be removed unless you delete them yourself.

## Dev Container

To load the workspace in the devcontainer:

1. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VS Code.
2. Install and run Docker.
3. Open the workspace in VS Code as normal.
4. When prompted, click **Reopen in Container**. Alternatively, use the command palette (`Ctrl+Shift+P`) and select **Dev Containers: Reopen in Container**.

Use the **rebuild** options to bump the underlying image to the latest release.

The container is based on Ubuntu and can be customized via `.devcontainer/Dockerfile`.

If you see permission errors when saving mounted files or if Git creates root-owned files under `.git`, rebuild the devcontainer after updating the Dockerfile. The container is configured to run as a non-root `vscode` user with a matching host UID/GID to avoid ownership mismatches.

> **Tip:** Use the following command, from this repository's root directory, to verify image creation:
>
> ```
> $ docker build -f .devcontainer/Dockerfile -t personal-workspace .
> ```

When you first open the workspace in a new devcontainer, you may want to configure dotfiles such as `~/local.gitconfig` so you can commit from within the devcontainer. See the [dotfiles repository](https://github.com/kieranpotts/dotfiles) for details. You will also need to install VS Code extensions in the devcontainer.

## Repository status indicators

Repositories are labeled in the VS Code workspace with emoji markers to indicate their status:

- 🔒 **Archived**: Read-only repositories. No pushes are permitted. These are excluded from VS Code's Git GUI.
- 🚫 **Restricted**: Private or sensitive repositories with limited access or sharing restrictions.
- 📝 **Work-in-progress**: Actively being worked on!

-----

Copyright © 2020-present Kieran Potts, all rights reserved.
