#!/usr/bin/env python3
"""Clone repositories listed in repos.yaml that are not yet present locally.

Requires: pip install pyyaml
Usage:    python run/clone.py
"""

import subprocess
import sys
from pathlib import Path

import yaml

WORKSPACE = Path(__file__).resolve().parent.parent
MANIFEST = WORKSPACE / "repos.yaml"
REPOS_DIR = WORKSPACE / "repos"

SEP = "─" * 60


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

        if result.returncode == 0:
            print("  Done.")
            cloned += 1
        else:
            error_msg = result.stderr.strip()
            print(f"  FAILED: {error_msg}", file=sys.stderr)
            # Clean up partial clone on failure
            if dest.exists():
                import shutil
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
