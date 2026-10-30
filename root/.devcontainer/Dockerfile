#
# Image for the workspace-level devcontainer, which loads every repository in
# the workspace into one container. Referenced from `devcontainer.json`.
#
# The base image provides the common toolchain for all of my personal
# projects, including pre-commit and mise, so there is nothing to add here
# yet. This file is kept, rather than referencing the base image directly from
# `devcontainer.json`, so later workspace-wide tooling has a place to go.
#
# There is deliberately no Docker CLI or daemon. See `devcontainer.json`.
#

# Builds on my standard devcontainer base image.
FROM kieranpotts/devcontainer:latest

# Stops `apt` and `dpkg` from waiting on interactive prompts, which would
# otherwise hang the build.
ENV DEBIAN_FRONTEND=noninteractive

# Runs the rest of the build, and the container itself, as the base image's
# non-root `code` user.
USER code
