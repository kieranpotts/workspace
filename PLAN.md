# Local AI Agent Architecture Plan

## Goal

Isolate a local coding agent (Pi) from host system and user-level filesystem, while supporting a mix of local and cloud models.

## Guiding Principle

The devcontainer boundary is the security boundary. Pi runs *inside* the devcontainer, not on the host. It can operate freely within the project, but cannot reach host dotfiles, SSH keys, shell history, or any other user/system-level filesystem state.

---

## Component Responsibilities

### Ollama (host)
- Runs on the host for GPU access and inference speed
- Bound to the Docker bridge gateway IP only (e.g. `172.17.0.1:11434`) — not `0.0.0.0`
- Not exposed to the wider network
- Reachable from devcontainers via `host-gateway` alias

### Cloud model APIs (host)
- API keys stored in host environment or keychain only
- Passed into the devcontainer at runtime via `remoteEnv`
- Never baked into the container image or mounted config files

### Pi (inside devcontainer)
- Runs as a terminal process within the devcontainer
- Has full access to `/workspace` (the project) — this is intentional
- Has no access to host filesystem paths beyond what is explicitly mounted
- Reaches Ollama and cloud APIs via network; no other host access needed

### Devcontainer (per project)
- Is the unit of isolation — one per project
- Workspace mount scoped to the project directory only
- No bind mounts to home directory or parent directories
- No Docker socket forwarded unless explicitly required and understood
- Resource limits set (memory, CPU, PIDs) to prevent host exhaustion

---

## Topology

```
Host Machine
│
├── Ollama
│   └── bound to 172.17.0.1:11434 (bridge gateway only)
│
├── Host environment
│   └── API keys (ANTHROPIC_API_KEY, etc.) — injected at container start
│
└── Docker
    └── devcontainer (per project)
        ├── Pi agent process
        ├── /workspace  ← project bind mount (scoped, not parent dir)
        ├── /tmp        ← ephemeral scratch (tmpfs, noexec)
        └── network access
            ├── → 172.17.0.1:11434 (Ollama, local)
            └── → api.anthropic.com, api.openai.com, etc. (cloud)
```

---

## Devcontainer Configuration Constraints

### Mounts
- `workspaceMount` bound to `${localWorkspaceFolder}` only — not `~` or any parent
- No mount of `~/.ssh`, `~/.config`, `~/.gitconfig`, `~/.zshrc`, or similar
- Git identity passed via `remoteEnv` (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`) if needed, not via mounted dotfiles
- No `/var/run/docker.sock` mount unless the project explicitly requires Docker access, in which case this should be a conscious, documented decision

### Credentials
```jsonc
// devcontainer.json
{
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}",
    "OLLAMA_HOST": "http://host-gateway:11434"
  }
}
```

### Resource limits
```jsonc
{
  "runArgs": [
    "--memory=4g",
    "--cpus=2",
    "--pids-limit=512"
  ]
}
```

### Container hardening
- Run as non-root user where possible
- `--cap-drop ALL` with only necessary capabilities added back
- `--security-opt no-new-privileges:true`

---

## Model Routing

Pi supports multiple providers natively. Within the devcontainer, Pi is configured with:

- **Local models:** Ollama at `http://host-gateway:11434` — used for fast, cheap, or privacy-sensitive tasks; data never leaves the machine
- **Cloud models:** Anthropic, OpenAI, etc. — used for higher-capability tasks; credentials injected via `remoteEnv`, not stored in the project

Model selection is per-session or per-task using Pi's `/model` command or `Ctrl+L`. No additional proxy layer is required.

---

## What This Does and Does Not Protect

| Concern | Protected? | Notes |
|---|---|---|
| Pi reading host dotfiles | ✅ | Not mounted |
| Pi reading other projects | ✅ | Each devcontainer scoped to its own workspace |
| Pi reading SSH keys | ✅ | `~/.ssh` not mounted |
| Pi writing to host filesystem | ✅ | No host paths mounted beyond workspace |
| Pi exhausting host resources | ✅ | Memory, CPU, PID limits set |
| Pi exfiltrating data via network | ⚠️ | Network is open by default; add egress filtering if required |
| Pi escaping via kernel exploit | ❌ | Shared kernel — accepted risk for local dev; use gVisor/VM for higher assurance |
| Malicious Pi extension accessing workspace | ❌ | Pi has full workspace access by design — review extensions before installing |

---

## Out of Scope

- **MCP:** Pi does not include MCP by default. If MCP servers are added later, each should run in its own container with explicit volume scoping.
- **Sub-agents:** If Pi spawns sub-agent instances, they should inherit the same container context rather than running on the host.
- **Egress filtering:** Recommended for sensitive projects but not part of the baseline architecture described here.
- **Permission gating:** Pi has no built-in permission popups. If per-action approval is needed, implement via a Pi extension (see Pi's `permission-gate.ts` example).
