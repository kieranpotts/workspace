# {title}

This repository is checked out using a bare-clone-plus-worktrees layout.

- `.bare`. Bare clone (Git internals only).
- `.git`. Pointer file (`gitdir: ./.bare`) so Git commands work from this directory.
- `<worktree>`. A working tree checked out at a specific branch. There is always a
  `default` worktree. Additional worktrees may be declared in the workspace manifest.

Use the following commands to create and delete worktrees.

```sh
# Add a worktree for an existing remote branch.
git worktree add <worktree-name> origin/<branch>

# Add a worktree and create a new local branch from the current HEAD.
git worktree add -b <branch> <worktree-name>

# Remove a worktree.
git worktree remove <worktree-name>
```
