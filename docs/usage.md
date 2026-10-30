# Usage

## Dev Container

This repository ships with one devcontainer for the whole workspace, in [`root/.devcontainer/`](../root/.devcontainer), which the installer symlinks to `~/dev/personal/.devcontainer`. Every repository in the workspace is loaded into that one container. No repository has a devcontainer of its own.

The container is built on the [`kieranpotts/devcontainer`](https://github.com/kieranpotts/docker-devcontainer) base image, which provides the common toolchain: pre-commit, mise, Node and npm, Python, ripgrep, GnuPG, and ShellCheck. It runs as the base image's non-root `code` user, so files written to the bind-mounted workspace are owned by you on the host. The whole tree is mounted at the same path as on the host, so the links between each bare clone and its worktrees resolve inside the container.

### Opening the workspace

Install and run Docker on the host first.

- **VS Code:** install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. Open `~/dev/personal/personal.code-workspace` (or the `~/dev/personal` folder), then click **Reopen in Container** when prompted, or select **Dev Containers: Reopen in Container** from the command palette (`Ctrl+Shift+P`). The VS Code extensions the workspace needs are installed in the container automatically.
- **Zed:** open `~/dev/personal`, then open it in the dev container. Zed picks up the workspace's project settings from `~/dev/personal/.zed/settings.json`. Zed extensions are not installed automatically from the devcontainer config: declare them under `auto_install_extensions` in your Zed user settings.

Opening a single repository's folder does not offer a container. Open the workspace root instead, or attach to the running container (`personal-workspace`) and open the folder from there.

Use the **rebuild** options to bump the underlying image to the latest release.

### Installing a repository's dependencies

The container installs no repository's dependencies or toolchain. When you start work on a repository, run its own install by hand, inside the container, for example `./run/install`, `make install`, or `npm ci`. See that repository's README or AGENTS.md.

On every start, the container does install the pre-commit Git hooks of every repository listed in `personal.code-workspace`. This installs only the hook scripts. Hooks installed from the container fall back to the `pre-commit` on `PATH` when run from the host, and the other way round, so committing works from either side as long as pre-commit is installed on both.

### Git, SSH, and commit signing

Your Git configuration and `~/.ssh` are mounted into the container read-only, so `git commit`, `git pull`, and `git push` work as on the host. Configure dotfiles such as `~/local.gitconfig` on the host. See the [dotfiles repository](https://github.com/kieranpotts/dotfiles) for details.

Commits are signed by the host's GnuPG agent, and passphrase prompts appear in the host's pinentry. VS Code forwards the agent itself. For editors that do not, such as Zed, the container connects to the host's agent on start. This only works on Linux hosts, because it depends on `$XDG_RUNTIME_DIR/gnupg` and `gpgconf` on the host. On other hosts, remove the GnuPG parts of `initializeCommand` and the two GnuPG mounts from `devcontainer.json`, or the container will not start.

### Docker

There is no Docker in the container: no Docker CLI or daemon, and no access to the host's Docker daemon. Access to the host's daemon is equivalent to root on the host, and coding agents run in the container.

So run the scripts that need Docker in a terminal on the host. These are in asciibook, docker-devcontainer, docker-latex, gh-runner, json-schema, and the-timeless-way. Build images for publishing, and push them, from the host only, so registry credentials never reach the container.

Website's local preview runs inside the container. Its ports, 8080 and 8081, are published on the host, so open the preview in the host's browser at `http://localhost:8080`.

> **Tip:** Use the following command, on the host, from this repository's root directory, to verify image creation:
>
> ```
> $ docker build -t personal-workspace root/.devcontainer
> ```

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

- 🚫 **Restricted**: Private or sensitive repositories with limited access or sharing restrictions.
- 📝 **Work-in-progress**: Actively being worked on!
