#!/usr/bin/env python3
"""Sync all repositories listed in repos.yaml.

For each repo:
  - If not yet cloned, clones it.
  - If already cloned, stashes any dirty working tree, switches to the
    configured default branch, pulls with rebase, then restores the
    previous branch and stash.

Requires: pip install pyyaml
Usage:    python run/sync.py
"""

import subprocess
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(__file__).resolve().parent.parent
MANIFEST = WORKSPACE / "repos.yaml"
REPOS_DIR = WORKSPACE / "repos"

SEP = "─" * 60


def run(args: list[str], cwd: Path, *, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)


def stash_count(repo_dir: Path) -> int:
    result = run(["git", "rev-list", "--walk-reflogs", "--count", "refs/stash"], repo_dir)
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def current_branch(repo_dir: Path) -> str:
    return run(["git", "branch", "--show-current"], repo_dir).stdout.strip()


def is_branch_diverged(repo_dir: Path, branch: str) -> bool:
    """Check if local branch has diverged from remote."""
    result = run(["git", "rev-list", "--left-right", f"HEAD...origin/{branch}"], repo_dir)
    return result.returncode == 0 and result.stdout.strip() != ""


def sync_repo(name: str, url: str, branch: str, dest: Path) -> bool:
    print(SEP)
    print(name)

    if not dest.exists():
        print(f"  Not cloned yet — cloning from {url} (branch: {branch}) ...")
        result = run(["git", "clone", "--branch", branch, url, str(dest)], WORKSPACE)

        # Branch may not exist yet (e.g., repo has no commits, or only its default branch).
        # Fall back to cloning without specifying a branch.
        if result.returncode != 0 and "Remote branch" in result.stderr and "not found" in result.stderr:
            import shutil
            shutil.rmtree(dest, ignore_errors=True)
            print(f"  Branch '{branch}' not found on remote — cloning without branch ...")
            result = run(["git", "clone", url, str(dest)], WORKSPACE)

        if result.returncode != 0:
            error_msg = result.stderr.strip()
            print(f"  ❌ FAILED to clone: {error_msg}", file=sys.stderr)
            import shutil
            shutil.rmtree(dest, ignore_errors=True)
            return False
        print("  ✓ Done.")
        return True

    print(f"  Default branch: {branch}")

    before_stash = stash_count(dest)
    run(["git", "stash", "push", "--include-untracked"], dest)

    original_branch = current_branch(dest)

    if original_branch != branch:
        print(f"  Switching from '{original_branch}' to '{branch}' ...")
        result = run(["git", "switch", branch], dest)
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            print(f"  ❌ FAILED to switch branch: {error_msg}", file=sys.stderr)
            print(f"     Your current branch '{original_branch}' may have diverged.", file=sys.stderr)
            print(f"     Check the repository manually: cd {dest}", file=sys.stderr)
            _restore_stash(dest, before_stash)
            return False

    print("  Pulling (rebase) ...")
    result = run(["git", "pull", "--rebase"], dest)
    if result.returncode != 0:
        error_msg = result.stderr.strip()
        print(f"  ❌ FAILED to pull: {error_msg}", file=sys.stderr)
        print(f"     Possible causes: network error, merge conflicts, or diverged branch.", file=sys.stderr)
        print(f"     Check the repository manually: cd {dest}", file=sys.stderr)
        _restore_stash(dest, before_stash)
        return False

    print("  ✓ Up to date.")

    if original_branch != branch:
        print(f"  Switching back to '{original_branch}' ...")
        result = run(["git", "switch", original_branch], dest)
        if result.returncode != 0:
            print(f"  ⚠️  Warning: Could not switch back to '{original_branch}'.", file=sys.stderr)

    _restore_stash(dest, before_stash)
    return True


def _restore_stash(repo_dir: Path, before: int) -> None:
    if stash_count(repo_dir) != before:
        result = run(["git", "stash", "pop"], repo_dir)
        if result.returncode != 0:
            print(f"  ⚠️  Warning: Stash pop failed. Stashed changes may need manual recovery.", file=sys.stderr)


def main() -> int:
    # Ensure repos directory exists
    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST) as f:
        config = yaml.safe_load(f)

    repos = config.get("repos", [])
    ok = 0
    failed = 0

    for repo in repos:
        success = sync_repo(
            name=repo["name"],
            url=repo["url"],
            branch=repo["branch"],
            dest=REPOS_DIR / repo["name"],
        )
        if success:
            ok += 1
        else:
            failed += 1

    print(SEP)
    print(f"Synced: {ok}  |  Failed: {failed}")

    if failed > 0:
        print(f"\n⚠️  {failed} repository/repositories failed to sync.", file=sys.stderr)
        print("    Run the script again to retry — successful syncs are skipped.", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
