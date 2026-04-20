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


def sync_repo(name: str, url: str, branch: str, dest: Path) -> bool:
    print(SEP)
    print(name)

    if not dest.exists():
        print(f"  Not cloned yet — cloning from {url} (branch: {branch}) ...")
        result = run(["git", "clone", "--branch", branch, url, str(dest)], WORKSPACE)
        if result.returncode != 0:
            print(f"  FAILED to clone: {result.stderr.strip()}", file=sys.stderr)
            return False
        print("  Done.")
        return True

    print(f"  Default branch: {branch}")

    before_stash = stash_count(dest)
    run(["git", "stash", "push", "--include-untracked"], dest)

    original_branch = current_branch(dest)

    if original_branch != branch:
        print(f"  Switching from '{original_branch}' to '{branch}' ...")
        result = run(["git", "switch", branch], dest)
        if result.returncode != 0:
            print(f"  FAILED to switch branch: {result.stderr.strip()}", file=sys.stderr)
            _restore_stash(dest, before_stash)
            return False

    print("  Pulling (rebase) ...")
    result = run(["git", "pull", "--rebase"], dest)
    if result.returncode != 0:
        print(f"  FAILED to pull: {result.stderr.strip()}", file=sys.stderr)
        _restore_stash(dest, before_stash)
        return False

    print("  Up to date.")

    if original_branch != branch:
        print(f"  Switching back to '{original_branch}' ...")
        run(["git", "switch", original_branch], dest)

    _restore_stash(dest, before_stash)
    return True


def _restore_stash(repo_dir: Path, before: int) -> None:
    if stash_count(repo_dir) != before:
        run(["git", "stash", "pop"], repo_dir)


def main() -> int:
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

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
