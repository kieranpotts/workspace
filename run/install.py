#!/usr/bin/env python3
"""Install all repositories listed in repos.yaml.

Each repo is stored as a bare clone with a single worktree checked out at the
configured branch, rooted under REPOS_DIR (default: ~/dev):

  ~/dev/<name>            — bare clone (no working tree)
  ~/dev/<name>/<branch>   — worktree checked out at <branch>

For each repo:
  - If not yet cloned, does `git clone --bare` then `git worktree add`.
  - If already cloned, fetches into the bare repo then fast-forwards the worktree.

Requires: pip install pyyaml
Usage:    python run/install.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(__file__).resolve().parent.parent
MANIFEST = WORKSPACE / "repos.yaml"

# Base directory under which all repositories are cloned.
# Bare clones land at <REPOS_DIR>/<name>.git; working trees at <REPOS_DIR>/<name>.
REPOS_DIR = Path.home() / "dev"

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


def run(args: list[str], cwd: Path, *, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)


def sync_repo(name: str, url: str, branch: str, bare: Path, worktree: Path) -> bool:
    print(SEP)
    print(name)

    if not bare.exists():
        print(f"  Not cloned yet — bare-cloning from {url} ...")
        bare.parent.mkdir(parents=True, exist_ok=True)
        result = run(["git", "clone", "--bare", url, str(bare)], WORKSPACE)
        if result.returncode != 0:
            print(f"  ❌ FAILED to clone: {result.stderr.strip()}", file=sys.stderr)
            shutil.rmtree(bare, ignore_errors=True)
            return False

        # git clone --bare sets remote fetch refs to refs/heads/* → refs/heads/* but
        # does not configure a remote tracking namespace. Fix that so `git fetch` works.
        run(["git", "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*"], bare)

        print(f"  Adding worktree for branch '{branch}' ...")
        result = run(["git", "worktree", "add", str(worktree), branch], bare)

        if result.returncode != 0 and "invalid reference" in result.stderr:
            # Branch doesn't exist on remote yet — check out whatever HEAD is.
            print(f"  Branch '{branch}' not found — adding worktree at HEAD ...")
            result = run(["git", "worktree", "add", str(worktree)], bare)

        if result.returncode != 0:
            print(f"  ❌ FAILED to add worktree: {result.stderr.strip()}", file=sys.stderr)
            shutil.rmtree(bare, ignore_errors=True)
            return False

        print("  ✓ Done.")
        maybe_install_pre_commit(worktree)
        return True

    print(f"  Fetching ...")
    result = run(["git", "fetch", "--prune", "origin"], bare)
    if result.returncode != 0:
        print(f"  ❌ FAILED to fetch: {result.stderr.strip()}", file=sys.stderr)
        return False

    if not worktree.exists():
        print(f"  Worktree missing — re-adding for branch '{branch}' ...")
        worktree.parent.mkdir(parents=True, exist_ok=True)
        result = run(["git", "worktree", "add", str(worktree), branch], bare)
        if result.returncode != 0:
            print(f"  ❌ FAILED to add worktree: {result.stderr.strip()}", file=sys.stderr)
            return False
        maybe_install_pre_commit(worktree)
        return True

    # Fast-forward the worktree branch to match origin.
    print(f"  Merging origin/{branch} (fast-forward only) ...")
    result = run(["git", "merge", "--ff-only", f"origin/{branch}"], worktree)
    if result.returncode != 0:
        print(f"  ❌ FAILED to fast-forward: {result.stderr.strip()}", file=sys.stderr)
        print(f"     The worktree may have local commits. Check manually: cd {worktree}", file=sys.stderr)
        return False

    print("  ✓ Up to date.")
    maybe_install_pre_commit(worktree)
    return True


def main() -> int:
    with open(MANIFEST) as f:
        config = yaml.safe_load(f)

    repos = config.get("repos", [])
    ok = 0
    failed = 0

    for repo in repos:
        name = repo["name"]
        success = sync_repo(
            name=name,
            url=repo["url"],
            branch=repo["branch"],
            bare=REPOS_DIR / name,
            worktree=REPOS_DIR / name / repo["branch"],
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
