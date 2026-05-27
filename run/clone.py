#!/usr/bin/env python3
"""Clone repositories listed in repos.yaml that are not yet present locally.

Requires: pip install pyyaml
Usage:    python run/clone.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(__file__).resolve().parent.parent
MANIFEST = WORKSPACE / "repos.yaml"
REPOS_DIR = WORKSPACE / "repos"

SEP = "─" * 60


def maybe_install_pre_commit(dest: Path) -> None:
    if not (dest / ".pre-commit-config.yaml").exists():
        return
    if shutil.which("pre-commit") is None:
        return
    print("  Installing pre-commit hooks ...")
    result = subprocess.run(["pre-commit", "install"], cwd=dest, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  pre-commit install failed: {result.stderr.strip()}", file=sys.stderr)
    else:
        print("  ✓ pre-commit hooks installed.")


def main() -> int:
    # Ensure repos directory exists
    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST) as f:
        config = yaml.safe_load(f)

    repos = config.get("repos", [])
    cloned = 0
    skipped = 0
    failed = 0

    for repo in repos:
        name = repo["name"]
        url = repo["url"]
        branch = repo["branch"]
        dest = REPOS_DIR / name

        print(SEP)
        print(name)

        if dest.exists():
            print("  Already present, skipping.")
            skipped += 1
            continue

        print(f"  Cloning from {url} (branch: {branch}) ...")
        result = subprocess.run(
            ["git", "clone", "--branch", branch, url, str(dest)],
            capture_output=True,
            text=True,
        )

        # Branch may not exist yet (e.g., repo has no commits, or only its default branch).
        # Fall back to cloning without specifying a branch.
        if result.returncode != 0 and "Remote branch" in result.stderr and "not found" in result.stderr:
            shutil.rmtree(dest, ignore_errors=True)
            print(f"  Branch '{branch}' not found on remote — cloning without branch ...")
            result = subprocess.run(
                ["git", "clone", url, str(dest)],
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            print("  Done.")
            maybe_install_pre_commit(dest)
            cloned += 1
        else:
            error_msg = result.stderr.strip()
            print(f"  FAILED: {error_msg}", file=sys.stderr)
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
                print(f"  Cleaned up partial clone.", file=sys.stderr)
            failed += 1

    print(SEP)
    print(f"Cloned: {cloned}  |  Skipped (already present): {skipped}  |  Failed: {failed}")

    if failed > 0:
        print(f"\n⚠️  {failed} repository/repositories failed to clone.", file=sys.stderr)
        print("    Run the script again to retry failed clones.", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
