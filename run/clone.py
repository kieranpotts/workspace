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
            print(f"  FAILED: {result.stderr.strip()}", file=sys.stderr)
            failed += 1

    print(SEP)
    print(f"Cloned: {cloned}  |  Skipped (already present): {skipped}  |  Failed: {failed}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
