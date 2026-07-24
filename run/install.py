#!/usr/bin/env python3
"""Install all repositories listed in repos.yaml.

Each repo is checked out using the "adjacent worktree" pattern, rooted under
REPOS_DIR (default: ~/dev/personal):

  ~/dev/personal/<name>/.bare           — bare clone (Git internals only)
  ~/dev/personal/<name>/.git            — file containing "gitdir: ./.bare"
  ~/dev/personal/<name>/<worktree_name> — working tree checked out at <branch>

The `.git` pointer file lets `git` commands run from the project root
(~/dev/personal/<name>) as well as from inside `.bare`.

For each repo:
  - If not yet cloned, does `git clone --bare` into `.bare`, writes the `.git`
    pointer, fixes the fetch refspec, then `git worktree add` for every
    declared worktree.
  - If already cloned, fetches then fast-forwards every existing worktree.

Requires: pip install pyyaml
Usage:    python run/install.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(__file__).resolve().parent.parent
MANIFEST = WORKSPACE / "repos.yaml"

# Directory inside this workspace repo whose contents mirror what should be
# surfaced at the root of REPOS_DIR (~/dev/personal) — see `link_workspace_assets`.
ROOT_ASSETS_DIR = WORKSPACE / "root"

# Base directory under which all repositories are cloned. Each repo's bare clone
# lands at <REPOS_DIR>/<name>/.bare, with working trees as sibling directories.
REPOS_DIR = Path.home() / "dev" / "personal"

# Entries inside ROOT_ASSETS_DIR that should be surfaced at the root of REPOS_DIR
# (~/dev/personal) via symlink, so the whole tree can be opened as a single VS
# Code workspace / devcontainer from one place, and so AGENTS.md is visible to
# agents working in any sibling project.
LINKED_ASSETS = ["personal.code-workspace", "AGENTS.md", ".devcontainer"]

SEP = "─" * 60


def maybe_install_pre_commit(dest: Path) -> None:
    if not (dest / ".pre-commit-config.yaml").exists():
        return
    if shutil.which("pre-commit") is None:
        return
    print("  Installing pre-commit hooks ...")
    result = run(["pre-commit", "install"], dest)
    if result.returncode != 0:
        print(f"  ⚠️  pre-commit install failed: {result.stderr.strip()}", file=sys.stderr)
    else:
        print("  ✓ pre-commit hooks installed.")


def link_workspace_assets() -> None:
    """Symlink selected assets from ROOT_ASSETS_DIR into REPOS_DIR (~/dev/personal).

    Creates, e.g., ~/dev/personal/personal.code-workspace → the copy in this repo's
    `root/` directory, so the workspace file, devcontainer config, and AGENTS.md
    are reachable from the root of the dev tree. Symlinks are relative, so the
    whole tree can be relocated intact.
    """
    print(SEP)
    print("Linking workspace assets into", REPOS_DIR)

    for asset in LINKED_ASSETS:
        source = ROOT_ASSETS_DIR / asset
        link = REPOS_DIR / asset

        if not source.exists():
            print(f"  ⚠️  Source not found, skipping: {source}", file=sys.stderr)
            continue

        target = Path(os.path.relpath(source, REPOS_DIR))

        # Already a symlink — replace it only if it points somewhere else.
        if link.is_symlink():
            if Path(os.readlink(link)) == target:
                print(f"  ✓ {asset} already linked.")
                continue
            link.unlink()
        elif link.exists():
            # A real file/dir is sitting where the link should go — don't clobber it.
            print(f"  ⚠️  {link} exists and is not a symlink — skipping.", file=sys.stderr)
            continue

        link.symlink_to(target, target_is_directory=source.is_dir())
        print(f"  ✓ Linked {asset} → {target}")


def run(args: list[str], cwd: Path, *, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)


def current_branch(worktree: Path) -> str | None:
    """Return the branch currently checked out in `worktree`, or None if detached."""
    result = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], worktree)
    if result.returncode != 0:
        return None  # detached HEAD (or not a worktree)
    return result.stdout.strip()


def switch_branch(bare: Path, worktree: Path, branch: str) -> subprocess.CompletedProcess:
    """Check `branch` out into an existing worktree, creating a tracking branch if needed.

    Mirrors `add_worktree`'s tracking behaviour: if a local branch already
    exists we switch to it and (re)assert its upstream; otherwise we create it
    from `origin/<branch>` with tracking configured. Run from the worktree so
    `git switch` acts on that working tree.
    """
    branches = run(["git", "branch", "--list", branch], bare)
    if branches.stdout.strip():
        result = run(["git", "switch", branch], worktree)
        if result.returncode == 0:
            run(["git", "branch", f"--set-upstream-to=origin/{branch}", branch], worktree)
        return result
    return run(["git", "switch", "--track", "-c", branch, f"origin/{branch}"], worktree)


def add_worktree(bare: Path, worktree: Path, branch: str) -> subprocess.CompletedProcess:
    """Add a worktree for `branch`, falling back to HEAD if the branch is absent.

    Git commands run from the bare repo, which means they're not reliant
    upon the `.git` pointer file being in place at the project root.

    Uses `--track -b <branch> origin/<branch>` rather than plain
    `git worktree add <path> <branch>` — the latter DWIMs a local branch
    from the remote-tracking ref but does not set its upstream, so `git
    status`/`pull`/`push` in the resulting worktree have no `[origin/...]`
    tracking info until the user sets it manually.

    A local branch named `branch` may already exist (e.g. left over from a
    worktree that was later removed, or from before tracking was set up by
    this function) — `-b` would fail with "branch already exists" in that
    case, so fall back to checking it out directly, then explicitly set its
    upstream since a plain checkout doesn't configure tracking either.
    """
    branches = run(["git", "branch", "--list", branch], bare)
    branch_exists = bool(branches.stdout.strip())

    if branch_exists:
        result = run(["git", "worktree", "add", str(worktree), branch], bare)
        if result.returncode == 0:
            run(["git", "branch", f"--set-upstream-to=origin/{branch}", branch], bare)
    else:
        result = run(
            ["git", "worktree", "add", "--track", "-b", branch, str(worktree), f"origin/{branch}"],
            bare,
        )
    if result.returncode != 0 and "invalid reference" in result.stderr:
        # Branch doesn't exist on remote yet — check out whatever HEAD is.
        print(f"  Branch '{branch}' not found — adding worktree at HEAD ...")
        result = run(["git", "worktree", "add", str(worktree)], bare)
    return result


def set_default_branch(bare: Path, branch: str) -> None:
    """Point the bare repo's HEAD at `branch` (its default branch per the manifest).

    A bare clone's HEAD tracks the origin's default at clone time and never
    updates afterwards, so it drifts once the manifest's `default` worktree
    names a different branch. Repointing it keeps `git symbolic-ref HEAD` — and
    anything that reads the default branch (e.g. `git clone`, PR base pickers) —
    consistent with the manifest. Only repoint once the local branch exists, so
    HEAD never dangles at a ref with no commits.
    """
    if not run(["git", "branch", "--list", branch], bare).stdout.strip():
        return
    ref = f"refs/heads/{branch}"
    if run(["git", "symbolic-ref", "HEAD"], bare).stdout.strip() == ref:
        return
    result = run(["git", "symbolic-ref", "HEAD", ref], bare)
    if result.returncode != 0:
        print(f"  ⚠️  Could not set default branch to '{branch}': {result.stderr.strip()}", file=sys.stderr)
    else:
        print(f"  ✓ Default branch (HEAD) set to '{branch}'.")


def ensure_bare_repo(name: str, url: str, project: Path, bare: Path) -> bool:
    """Clone the bare repo if it doesn't exist yet. Returns True on success."""
    if bare.exists():
        return True

    print(f"  Not cloned yet — bare-cloning from {url} ...")
    bare.parent.mkdir(parents=True, exist_ok=True)
    result = run(["git", "clone", "--bare", url, str(bare)], WORKSPACE)
    if result.returncode != 0:
        print(f"  ❌ FAILED to clone: {result.stderr.strip()}", file=sys.stderr)
        shutil.rmtree(project, ignore_errors=True)
        return False

    # Drop a `.git` pointer file at the project root pointing into `.bare`.
    # Without it, `git worktree`/`git fetch` only work from inside `.bare`.
    # With it, every git command works from the project root instead.
    (project / ".git").write_text("gitdir: ./.bare\n")

    # A bare clone omits the `remote.origin.fetch` config, so plain `git fetch`
    # won't populate refs/remotes/origin/* — and `git worktree add <remote-branch>`
    # then misbehaves. Set the standard refspec to restore normal fetch behaviour.
    run(["git", "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*"], bare)

    return True


def sync_worktree(
    bare: Path,
    worktree_path: Path,
    branch: str,
    worktree_name: str,
    just_cloned: bool,
) -> bool:
    """Ensure a single worktree exists and is up-to-date. Returns True on success."""
    if just_cloned or not worktree_path.exists():
        action = "Adding" if just_cloned else "Re-adding"
        print(f"  {action} worktree '{worktree_name}' for branch '{branch}' ...")
        result = add_worktree(bare, worktree_path, branch)
        if result.returncode != 0:
            print(f"  ❌ FAILED to add worktree: {result.stderr.strip()}", file=sys.stderr)
            return False
        maybe_install_pre_commit(worktree_path)
        return True

    # If the worktree is on a different branch than the manifest now declares,
    # switch it before syncing. Refuse if that would strand uncommitted changes.
    checked_out = current_branch(worktree_path)
    if checked_out != branch:
        was = checked_out if checked_out is not None else "a detached HEAD"
        dirty = run(["git", "status", "--porcelain"], worktree_path).stdout.strip()
        if dirty:
            print(
                f"  ⚠️  [{worktree_name}] on '{was}' but manifest wants '{branch}', "
                f"and there are uncommitted changes — not switching. "
                f"Commit or stash first: cd {worktree_path}",
                file=sys.stderr,
            )
            return False
        print(f"  [{worktree_name}] Switching from '{was}' to '{branch}' ...")
        result = switch_branch(bare, worktree_path, branch)
        if result.returncode != 0:
            print(f"  ❌ FAILED to switch branch: {result.stderr.strip()}", file=sys.stderr)
            return False

    # Fast-forward the working tree branch to match origin.
    print(f"  [{worktree_name}] Merging origin/{branch} (fast-forward only) ...")
    result = run(["git", "merge", "--ff-only", f"origin/{branch}"], worktree_path)
    if result.returncode != 0:
        print(f"  ❌ FAILED to fast-forward: {result.stderr.strip()}", file=sys.stderr)
        print(
            f"     The working tree may have local commits. Check manually: cd {worktree_path}",
            file=sys.stderr,
        )
        return False

    print(f"  [{worktree_name}] ✓ Up to date.")
    maybe_install_pre_commit(worktree_path)
    return True


def sync_repo(
    name: str,
    url: str,
    worktrees: dict[str, str],
    project: Path,
    bare: Path,
) -> bool:
    print(SEP)
    print(name)

    just_cloned = not bare.exists()
    if not ensure_bare_repo(name, url, project, bare):
        return False

    print("  Fetching ...")
    result = run(["git", "fetch", "--prune", "origin"], bare)
    if result.returncode != 0:
        print(f"  ❌ FAILED to fetch: {result.stderr.strip()}", file=sys.stderr)
        return False

    all_ok = True
    for worktree_name, branch in worktrees.items():
        worktree_path = project / worktree_name
        if not sync_worktree(bare, worktree_path, branch, worktree_name, just_cloned):
            all_ok = False

    # Keep the bare repo's HEAD pointed at the manifest's default branch — this is the
    # `default` worktree's branch by convention.
    default_branch = worktrees.get("default")
    if default_branch:
        set_default_branch(bare, default_branch)

    return all_ok


def main() -> int:
    with open(MANIFEST) as f:
        config = yaml.safe_load(f)

    repos = config.get("repos", [])
    ok = 0
    failed = 0

    for repo in repos:
        name = repo["name"]
        worktrees = repo.get("worktrees")
        if not worktrees:
            print(f"⚠️  '{name}' has no 'worktrees' map — skipping.", file=sys.stderr)
            failed += 1
            continue

        project = REPOS_DIR / name
        success = sync_repo(
            name=name,
            url=repo["url"],
            worktrees=worktrees,
            project=project,
            bare=project / ".bare",
        )
        if success:
            ok += 1
        else:
            failed += 1

    link_workspace_assets()

    print(SEP)
    print(f"Synced: {ok}  |  Failed: {failed}")

    if failed > 0:
        print(f"\n⚠️  {failed} repository/repositories failed to sync.", file=sys.stderr)
        print("    Run the script again to retry — successful syncs are skipped.", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
