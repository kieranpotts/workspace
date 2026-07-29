# Usage

## Dev Container

This repository ships with a devcontainer configuration for the whole workspace.

To load the workspace in the devcontainer:

1. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VS Code.
2. Install and run Docker.
3. Open the workspace in VS Code as normal.
4. When prompted, click **Reopen in Container**. Alternatively, use the command palette (`Ctrl+Shift+P`) and select **Dev Containers: Reopen in Container**.

Use the **rebuild** options to bump the underlying image to the latest release.

The container is based on Ubuntu and can be customized via `root/.devcontainer/Dockerfile`.

If you see permission errors when saving mounted files or if Git creates root-owned files under `.git`, rebuild the devcontainer after updating the Dockerfile. The container is configured to run as a non-root `vscode` user with a matching host UID/GID to avoid ownership mismatches.

> **Tip:** Use the following command, from this repository's root directory, to verify image creation:
>
> ```
> $ docker build -f root/.devcontainer/Dockerfile -t personal-workspace .
> ```

When you first open the workspace in a new devcontainer, you may want to configure dotfiles such as `~/local.gitconfig` so you can commit from within the devcontainer. See the [dotfiles repository](https://github.com/kieranpotts/dotfiles) for details. You will also need to install VS Code extensions in the devcontainer.

## Managing repositories

All repositories are defined in `repos.yaml`. Each entry has three fields:

```yaml
repos:
  - name: repository-name
    url: git@github.com:kieranpotts/repository-name.git
    worktrees:
      default: main
```

The `worktrees` map declares one or more named worktrees. The key is the directory name under the project root. The value is the branch to check out. For example, the entry above creates:

```
~/dev/personal/repository-name/.bare      — Bare clone (Git internals only).
~/dev/personal/repository-name/.git       — Pointer file.
~/dev/personal/repository-name/AGENTS.md  — Project-level guide to the worktree layout.
~/dev/personal/repository-name/default    — Working tree at branch `main`.
```

The `.git` pointer file allows `git` commands to work from the project root. You don't need to be in the scope of the `.bare` worktree to manage the project's worktrees.

A repo can declare multiple worktrees:

```yaml
repos:
  - name: my-project
    url: git@github.com:kieranpotts/my-project.git
    worktrees:
      default: v2/dev
      v1: v1/dev
```

This creates two working trees: `~/dev/personal/my-project/default` (branch `v2/dev`) and `~/dev/personal/my-project/v1` (branch `v1/dev`).

To add a repository, add an entry to `repos.yaml` and run `python3 run/install.py`. To remove a repository, delete its entry from `repos.yaml` and remove its project directory (which holds the bare clone and all worktrees):

```sh
rm -rf ~/dev/personal/<name>
```

Changes to `repos.yaml` should be committed.

## Manual worktree management

The `install.py` script only manages the worktrees declared in `repos.yaml`. For temporary or experimental work, you can add additional worktrees manually using standard Git commands from the project root (eg. `~/dev/personal/kieranpotts/my-project`):

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

## Repository status indicators

Repositories are labeled in the VS Code workspace with emoji markers to indicate their status:

- 🔒 **Archived**: Read-only repositories. No pushes are permitted. These are excluded from VS Code's Git GUI.
- 🚫 **Restricted**: Private or sensitive repositories with limited access or sharing restrictions.
- 📝 **Work-in-progress**: Actively being worked on!
