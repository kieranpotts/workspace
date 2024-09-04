#!/bin/bash

# Make all paths relative to the root of this repository, so
# this script can be run from any filesystem location.

# Absolute path to this script,
# eg `/path/to/workspace/run/install.sh`.
file_path=$(readlink -f "$0")

# Absolute path to this script's parent directory,
# eg `/path/to/workspace/run`.
run_path=$(dirname "${file_path}")

# Absolute path this repo's root directory,
# eg `/path/to/workspace`.
repo_path=$(dirname "${run_path}")

# Absolute path to the root directory for all personal projects, which is
# expected to be one level above the `workspace` repo root.
dev_path=$(readlink -f "${repo_path}/../")

source "${run_path}/_/repos.sh"

for repo in ${repos[@]}; do

  echo $(for i in $(seq 1 80); do printf "-"; done)

  local_path=${dev_path}/${repo}
  main_branch=${main_branches["${repo}"]}

  # Suppress output, but exit code will be 0 if the command succeeds
  # (which means the directory is a Git repository).
  echo ${local_path}
  (cd ${local_path}; git rev-parse 2> /dev/null)
  if [ $? != 0 ]; then
    echo "Not a Git repository, skipping..."
    continue
  fi

  (
    cd ${local_path}

    # Stash anything dirty in the working tree.
    initial_stash_count=$(git rev-list --walk-reflogs --count refs/stash 2> /dev/null)
    git stash push --include-untracked

    initial_branch=$(git branch --show-current)

    if [ "$initial_branch" != "${main_branch}" ]; then
      echo "Switching to ${main_branch}"
      git switch ${main_branch}
    fi

    upstream_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{upstream})

    if [ ! -z "$upstream_branch" ]; then
      git pull --rebase --prune
      git push --follow-tags
    else
      git push --set-upstream origin HEAD --follow-tags
    fi

    git switch ${initial_branch}

    new_stash_count=$(git rev-list --walk-reflogs --count refs/stash 2> /dev/null)
    if [ "${new_stash_count:-0}" != "${initial_stash_count:-0}" ]; then
      git stash pop
    fi

  )

done

echo $(for i in $(seq 1 80); do printf "-"; done)
