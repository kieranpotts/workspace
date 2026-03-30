#!/bin/bash

#
# Synchronize all submodules: pull the tracked branch with rebase,
# then push any local commits. Maintain any staged and working changes.
#
# Make all paths relative to the root of this repository, so
# this script can be run from any filesystem location.
#

# Absolute path to this script,
# eg `/path/to/workspace/run/sync.sh`.
file_path=$(readlink -f "$0")

# Absolute path to this script's parent directory,
# eg `/path/to/workspace/run`.
run_path=$(dirname "${file_path}")

# Absolute path this repo's root directory,
# eg `/path/to/workspace`.
repo_path=$(dirname "${run_path}")

# Change to the repository root directory.
cd "${repo_path}" || exit 1

# Read all submodule names from .gitmodules.
submodules=$(git config -f .gitmodules --get-regexp '^submodule\..*\.path$' | awk '{print $2}')

for submodule_path in ${submodules}; do

  # shellcheck disable=SC2046
  # shellcheck disable=SC2005
  echo $(for i in $(seq 1 80); do printf "-"; done)

  cd "${repo_path}/${submodule_path}" || exit 1

  # Extract the submodule name from its path (eg "repos/blog" -> "blog").
  name=$(basename "${submodule_path}")

  echo "Syncing ${name}..."

  branch=$(git config -f "${repo_path}/.gitmodules" --get "submodule.${submodule_path}.branch")
  echo "Default branch is ${branch}"

  if [ -z "${branch}" ]; then
    echo "No branch configured for ${name}, skipping..."
    continue
  fi

  # Stash anything dirty in the working tree.
  initial_stash_count=$(git rev-list --walk-reflogs --count refs/stash 2> /dev/null)
  git stash push --include-untracked

  initial_branch=$(git branch --show-current)

  if [ "${initial_branch}" != "${branch}" ]; then
    echo "Switching to ${branch}"
    git switch "${branch}"
  fi

  upstream_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null)

  if [ -n "${upstream_branch}" ]; then
    git pull --rebase --prune
    git push --follow-tags
  else
    git push --set-upstream origin HEAD --follow-tags
  fi

  if [ "${initial_branch}" != "${branch}" ]; then
    git switch "${initial_branch}"
  fi

  # Restore previous stash.
  new_stash_count=$(git rev-list --walk-reflogs --count refs/stash 2> /dev/null)
  if [ "${new_stash_count:-0}" != "${initial_stash_count:-0}" ]; then
    git stash pop
  fi

  cd "${repo_path}" || exit

done

# shellcheck disable=SC2046
# shellcheck disable=SC2005
# shellcheck disable=SC2034
echo $(for i in $(seq 1 80); do printf "-"; done)
