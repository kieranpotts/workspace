FROM kieranpotts/devcontainer:latest

ENV DEBIAN_FRONTEND=noninteractive

USER code

# Installs the pre-commit program `~/.local/bin`, which is on the base image's
# `PATH`. Used by the `postStartCommand` in `devcontainer.json` to install
# Git hooks.
RUN pipx install pre-commit
