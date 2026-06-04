# Local AI Agent Architecture Plan

## Goal

Isolate a local coding agent (Pi) from host system and user-level filesystem, while supporting a mix of local and cloud models.

---

## Fixed Components

These are constant across all three options.

### Ollama (host)
- Runs on the host for GPU access and inference speed
- Bound to the Docker bridge gateway IP only (e.g. `172.17.0.1:11434`) — not `0.0.0.0`
- Not exposed to the wider network
- Reachable from containers via the `host-gateway` alias

### Cloud model API keys (host)
- Stored in host environment or keychain only
- Injected into containers at runtime via `remoteEnv` or `--env`
- Never baked into container images or mounted config files

### Devcontainer hardening (all options)
- `workspaceMount` scoped to `${localWorkspaceFolder}` only — not `~` or any parent directory
- No mount of `~/.ssh`, `~/.config`, `~/.gitconfig`, or similar host dotfiles
- No `/var/run/docker.sock` mount unless explicitly required (see Option C)
- Non-root user inside the container
- `--cap-drop ALL` with only necessary capabilities restored
- `--security-opt no-new-privileges:true`
- Resource limits: `--memory`, `--cpus`, `--pids-limit`

---

## The Three Options

---

### Option A — Pi Inside the Devcontainer

Pi runs as a process within each project's devcontainer. The container boundary is both the project boundary and the agent boundary.

```
Host Machine
│
├── Ollama :11434 (bridge gateway only)
├── API keys (injected at container start)
│
└── Docker
    ├── project-a devcontainer
    │   ├── Pi process
    │   └── /workspace/project-a  ← bind mount, scoped to project
    │
    └── project-b devcontainer
        ├── Pi process
        └── /workspace/project-b  ← bind mount, scoped to project
```

**Pros**
- Simplest setup — no inter-container networking required
- Pi runs in the project's own environment, with the correct language runtimes, tools, and dependencies already present
- No Docker socket or exec access needed
- Fully compatible with standard devcontainer tooling (VS Code, JetBrains, etc.)
- Each project gets its own isolated Pi instance with independent session history

**Cons**
- Pi is re-installed or re-configured per devcontainer image
- Cannot work across multiple projects in a single session
- Pi's own config and session history are ephemeral unless explicitly persisted to a named volume
- Agent tooling is coupled to the project environment

**Best for:** Single-project workflows, simplicity, teams already using devcontainers as their primary dev environment.

---

### Option B — Pi in Its Own Container, Shared Named Volumes

Pi runs in a dedicated container. Project files live in named Docker volumes, shared between Pi and the relevant devcontainer.

```
Docker network: agent-net
│
├── pi-container
│   ├── Pi process
│   ├── /home/pi          ← Pi config + session history (named volume)
│   ├── /projects/proj-a  ← shared named volume (read/write)
│   └── /projects/proj-b  ← shared named volume (read/write)
│
├── project-a devcontainer
│   └── /workspace        ← same named volume as /projects/proj-a above
│
└── project-b devcontainer
    └── /workspace        ← same named volume as /projects/proj-b above
```

Pi mounts project volumes directly and operates on files natively, just as it would in Option A. The devcontainer mounts the same volume as its workspace.

**Pros**
- Pi is a single, persistent, well-configured instance across all projects
- Pi config, extensions, and session history are stable and centralised
- No Docker socket required — Pi has direct file access via shared volumes
- Pi and the devcontainer can work on the same files simultaneously

**Cons**
- Pi does not run in the project's environment — it may lack project-specific runtimes, compilers, or tools needed to run or test code
- Named volumes are opaque on the host (harder to browse/backup than bind mounts)
- Simultaneous writes from Pi and the developer could cause conflicts
- Cross-project access is controlled only by which volumes are mounted — requires discipline in configuration

**Best for:** Multi-project workflows where Pi's own environment is sufficient, and project-specific tooling is not required for the agent to operate.

---

### Option C — Pi in Its Own Container, Exec-Based Access

Pi runs in a dedicated container but does not mount project filesystems. Instead, it executes commands inside target devcontainers via `docker exec` (or SSH), reading and writing files through the project container's own shell.

```
Docker network: agent-net
│
├── pi-container
│   ├── Pi process + SSH/exec extension
│   ├── /home/pi          ← Pi config + session history (named volume)
│   └── docker.sock (or restricted exec proxy)
│       ↓ exec / SSH
│
├── project-a devcontainer
│   └── /workspace/project-a  ← Pi never mounts this directly
│
└── project-b devcontainer
    └── /workspace/project-b  ← Pi never mounts this directly
```

Pi issues shell commands that run *inside* the target container and observes stdout/stderr. This is how tools like Claude Code and Cursor's remote mode operate.

**Pros**
- Pi executes in the correct project environment — runtimes, compilers, and tools are exactly as the developer configured them
- Cleanest separation: Pi has no direct filesystem access to any project
- Commands run with the devcontainer's user and permissions, not Pi's
- Pi can target multiple containers in sequence without remounting volumes

**Cons**
- Requires either mounting `docker.sock` into the Pi container (broad host Docker privilege) or building/running a restricted exec proxy
- More complex to set up and debug
- `docker.sock` access is a significant privilege — a compromised Pi container could control all containers on the host
- Latency per operation is higher (exec overhead vs. direct file I/O)

**Mitigating the docker.sock risk:** Rather than mounting the full socket, run a small proxy (e.g. [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy)) that allowlists only the `exec` API endpoint for specific container names. Pi talks to the proxy, not the real socket.

**Best for:** Scenarios where running commands in the correct project environment is important (e.g. tests, builds, linters), or where stricter filesystem isolation is desired.

---

## Comparison Summary

| | Option A | Option B | Option C |
|---|---|---|---|
| **Pi location** | Inside devcontainer | Own container | Own container |
| **File access method** | Direct (co-located) | Shared named volume | `docker exec` / SSH |
| **Project env available to Pi** | ✅ Full | ❌ Pi's own env only | ✅ Full |
| **Pi config persistence** | ⚠️ Per container | ✅ Centralised | ✅ Centralised |
| **Multi-project in one session** | ❌ | ✅ | ✅ |
| **Docker socket required** | ❌ | ❌ | ⚠️ Yes (or proxy) |
| **Setup complexity** | Low | Medium | High |
| **Filesystem isolation (Pi↔host)** | ✅ | ✅ | ✅ |
| **Filesystem isolation (Pi↔project)** | ❌ By design | ❌ By design | ✅ Mediated |

---

## Key Tradeoffs

**Simplicity vs. separation.** Option A is the easiest to reason about and operate. Options B and C introduce inter-container coordination, which adds operational complexity in exchange for better separation of Pi from project environments.

**Project environment fidelity.** If Pi needs to run code — tests, builds, formatters — it needs the project's runtimes. Option A and C provide this; Option B does not unless project tooling is duplicated in the Pi image.

**Centralised vs. per-project Pi.** Options B and C give you a single Pi instance with stable config, extensions, and history. Option A gives each project its own isolated Pi, which may be preferable if projects have divergent requirements or if you want strong session isolation.

**The docker.sock decision.** Option C's exec-based approach is architecturally the cleanest, but `docker.sock` access is a real privilege escalation risk. If you choose Option C, using a socket proxy that restricts access to `exec`-only on named containers is strongly recommended over mounting the raw socket.

---

## Model Routing (all options)

Pi supports multiple providers natively. Configure per-container via environment variables:

```jsonc
// devcontainer.json (Option A) or pi-container config (Options B/C)
{
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY":    "${localEnv:OPENAI_API_KEY}",
    "OLLAMA_HOST":       "http://host-gateway:11434"
  }
}
```

- **Local models** via Ollama — fast, private, data never leaves the machine
- **Cloud models** — for higher-capability tasks; keys held on host, injected at runtime

Switch models mid-session with Pi's `/model` command or `Ctrl+L`. No proxy layer required.

---

## What All Three Options Protect Against

| Concern | Protected? | Notes |
|---|---|---|
| Pi reading host dotfiles | ✅ | Not mounted in any option |
| Pi reading SSH keys | ✅ | `~/.ssh` not mounted |
| Pi writing to host filesystem | ✅ | No host paths mounted beyond workspace |
| Pi reading sibling projects | ✅ | Volume scoping enforces this |
| Pi exhausting host resources | ✅ | Memory, CPU, PID limits on all containers |
| Pi exfiltrating data via network | ⚠️ | Network open by default; add egress filtering if needed |
| Pi escaping via kernel exploit | ❌ | Shared kernel — accepted risk for local dev |
| Malicious Pi extension | ❌ | Pi has workspace access by design; audit extensions before installing |

---

## Out of Scope

- **MCP:** Pi does not include MCP by default. If added, each MCP server should run in its own container with explicit volume scoping.
- **Egress filtering:** Recommended for sensitive projects; not part of the baseline architecture here.
- **Permission gating:** Pi has no built-in permission popups. If per-action approval is needed, use Pi's `permission-gate.ts` extension example as a starting point.
- **gVisor / VM-based isolation:** Not required for local dev; consider if running untrusted agent extensions or in a multi-user environment.
