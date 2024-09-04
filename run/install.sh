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
  remote_url=${remote_urls["${repo}"]}
  main_branch=${main_branches["${repo}"]}

  echo "Making directory ${local_path}"
  mkdir -p ${local_path}

  # Suppress output, but exit code will be 0 if the command succeeds
  # (which means the directory is already a Git repository).
  (cd ${local_path}; git rev-parse 2> /dev/null)
  if [ $? == 0 ]; then
    echo "Already a Git repository, skipping..."
    continue
  fi

  if find "${local_path}" -mindepth 1 -print -quit 2> /dev/null | grep -q .; then
    echo "Directory is not empty, initializing as a Git repo"
    (cd ${local_path}; git init)
    continue
  fi

  echo "Cloning ${remote_url}"
  (cd ${local_path}; git clone ${remote_url} .)

  echo "Switching to ${main_branch}"
  (cd ${local_path}; git switch ${main_branch})

  echo "Setting Git user name and email for repo"
  (cd ${local_path}; git config user.name "Kieran Potts"; git config user.email "hello@kieranpotts.com")

done

echo $(for i in $(seq 1 80); do printf "-"; done)

echo "NOTE: The devtools repo should be cloned in Windows."
