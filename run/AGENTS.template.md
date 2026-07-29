# {title}

This repository is checked out using a bare-clone-plus-worktrees layout.

- `.bare`: bare clone (Git internals only).
- `.git`: pointer file (`gitdir: ./.bare`) so Git commands work from this directory.
- `<worktree>`: a working tree checked out at a specific branch. There is always a
  `default` worktree; additional worktrees may be declared in the workspace manifest.

To add a new worktree, run from this directory:

```sh
# Add a worktree for an existing remote branch.
git worktree add <worktree-name> origin/<branch>

# Add a worktree and create a new local branch from the current HEAD.
git worktree add -b <branch> <worktree-name>
```

To remove a worktree:

```sh
git worktree remove <worktree-name>
```
