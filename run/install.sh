#!/bin/bash

#
# Initialize and clone all Git submodules, then check out each one's
# tracked branch (submodules default to detached HEAD).
#
# Make all paths relative to the root of this repository, so
# this script can be run from any filesystem location.
#

# Absolute path to this script,
# eg `/path/to/workspace/run/install.sh`.
file_path=$(readlink -f "$0")

# Absolute path to this script's parent directory,
# eg `/path/to/workspace/run`.
run_path=$(dirname "${file_path}")

# Absolute path this repo's root directory,
# eg `/path/to/workspace`.
repo_path=$(dirname "${run_path}")

# Change directory to the repository root directory.
cd "${repo_path}"

# Read all submodule names from .gitmodules.
submodules=$(git config -f .gitmodules --get-regexp '^submodule\..*\.path$' | awk '{print $2}')

for submodule_path in ${submodules}; do

  echo $(for i in $(seq 1 80); do printf "-"; done)

  # Extract the submodule name from its path (eg "repos/blog" -> "blog").
  name=$(basename "${submodule_path}")

  echo "Installing ${name}..."

  # Initialize and clone this submodule. These commands must be run
  # from the parent repository root, passing the submodule path.
  # Recursively checkout any further nested submodules.
  git submodule init "${submodule_path}"
  git submodule update --recursive "${submodule_path}"

done

echo $(for i in $(seq 1 80); do printf "-"; done)
