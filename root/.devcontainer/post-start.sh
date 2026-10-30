#!/usr/bin/env sh

# Prepare the workspace devcontainer on every start. Run by `postStartCommand`
# in `devcontainer.json`, from the root of the workspace (`~/dev/personal`).
#
# 1. Install the pre-commit Git hooks of every repository in the workspace.
# 2. Connect the devcontainer's GnuPG to the host's `gpg-agent`, so Git can
#    sign commits in editors that do not forward the agent themselves, eg.
#    Zed. `devcontainer.json` explains the mounts used here.
#
# Both steps are idempotent. Neither installs any repository's dependencies.
#
# Supports Linux hosts only. The host's agent sockets are mounted from
# `$XDG_RUNTIME_DIR/gnupg`, which does not exist on macOS or Windows hosts.

set -eu

# --- 1. pre-commit hooks ------------------------------------------------------

# The workspace's repositories are the folders listed in the VS Code workspace
# file, so that file stays the single definition of what is in the workspace.
# Its folder paths are relative to the file itself.
WORKSPACE_FILE="$PWD/personal.code-workspace"

if [ ! -f "$WORKSPACE_FILE" ]; then
  echo "post-start: $WORKSPACE_FILE not found; skipped installing pre-commit hooks." >&2
else
  # The file is JSONC (JSON with comments and trailing commas), which `jq`
  # cannot parse, so pick out the `"path"` entries of the `"folders"` array
  # with `sed`. Folder names contain no `]`, so the array ends at the first.
  folders="$(sed -n '/"folders"/,/\]/s/^[[:space:]]*"path":[[:space:]]*"\([^"]*\)".*/\1/p' "$WORKSPACE_FILE")"

  installed=0
  failed=0

  for folder in $folders; do
    repo="$(dirname "$WORKSPACE_FILE")/$folder"

    # Skip folders that are not cloned, or have no hooks to install.
    [ -f "$repo/.pre-commit-config.yaml" ] || continue

    # Hooks are written to the Git common directory, ie. `<repo>/.bare/hooks`
    # for a bare clone, so every worktree of the repository is covered.
    if output="$(cd "$repo" && pre-commit install 2>&1)"; then
      installed=$((installed + 1))
    else
      failed=$((failed + 1))
      echo "post-start: pre-commit install failed in $folder:" >&2
      echo "$output" >&2
    fi
  done

  echo "post-start: installed pre-commit hooks in $installed repositories ($failed failed)."
fi

# --- 2. GnuPG -----------------------------------------------------------------

GNUPG_HOME="$HOME/.gnupg"

# The path where the container's `gpg` looks for the agent.
AGENT_SOCKET="$GNUPG_HOME/S.gpg-agent"

# The host's agent "extra" socket, which is restricted to the operations
# needed to sign with existing keys.
HOST_SOCKET=/run/host-gnupg/S.gpg-agent.extra

# A read-only mount of the host's public keyring.
HOST_PUBRING=/run/host-gnupg-pubring.kbx

mkdir -p "$GNUPG_HOME"
chmod 700 "$GNUPG_HOME"

# If an agent already answers at the container's socket, it is either VS
# Code's forwarded agent or a redirect left by a previous start, so leave it
# alone. No container-local agent can be running this early, so any socket
# that does not answer is stale. `gpg-connect-agent` exits zero even when no
# agent answers, so check for a data line in its output instead.
if gpg-connect-agent --no-autostart 'getinfo version' /bye 2>/dev/null | grep -q '^D '; then
  echo "post-start: gpg-agent is already reachable."
  exit 0
fi

if [ ! -S "$HOST_SOCKET" ]; then
  echo "post-start: host gpg-agent socket not found; commit signing is unavailable." >&2
  exit 0
fi

# Point the container's `gpg` at the host's agent, using a GnuPG socket
# redirect file in place of a socket.
rm -f "$AGENT_SOCKET"
printf '%%Assuan%%\nsocket=%s\n' "$HOST_SOCKET" > "$AGENT_SOCKET"

# `gpg` needs the public half of the signing key to find its secret half in
# the agent. Export from a copy, because `gpg` wants to lock the keyring and
# the mount is read-only.
if [ -s "$HOST_PUBRING" ]; then
  TMP_PUBRING="$(mktemp)"
  cp "$HOST_PUBRING" "$TMP_PUBRING"
  gpg --batch --quiet --no-default-keyring --keyring "$TMP_PUBRING" --export \
    | gpg --batch --quiet --import
  rm -f "$TMP_PUBRING" "$TMP_PUBRING~"
fi

echo "post-start: connected gpg to the host's gpg-agent."
