# Local AI Agent Architecture Plan

## Goal

Isolate a local coding agent (Pi) from host system and user-level filesystem, while supporting a mix of local and cloud models.

---

## Fixed Components

These are constant across all four options.

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

## The Four Options

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

### Option D — Pi in Its Own Container, MCP Server as Mediator

Pi runs in a dedicated container and has no direct filesystem access or exec access to any project. Instead, a containerised MCP server sits between Pi and each devcontainer, exposing a structured, operation-scoped API over the project filesystem. Pi calls MCP tools (`read_file`, `write_file`, `list_directory`, `run_command`, etc.); the MCP server enforces what is permitted.

Pi does not include MCP support by default, so this option requires adding an MCP client extension to Pi.

```
Docker network: agent-net
│
├── pi-container
│   ├── Pi process + MCP client extension
│   ├── /home/pi              ← Pi config + session history (named volume)
│   └── (no project mounts, no docker.sock)
│       ↓ MCP protocol (HTTP/SSE or stdio)
│
├── mcp-server-container
│   ├── MCP server process
│   ├── /projects/proj-a      ← shared named volume (scoped read/write)
│   ├── /projects/proj-b      ← shared named volume (scoped read/write)
│   └── enforces: path allowlist, operation allowlist, per-project permissions
│
├── project-a devcontainer
│   └── /workspace            ← same named volume as /projects/proj-a above
│
└── project-b devcontainer
    └── /workspace            ← same named volume as /projects/proj-b above
```

The MCP server is the only component with filesystem access to project volumes. It enforces a path allowlist (e.g. no access above `/projects/proj-a`), an operation allowlist (e.g. no `rm -rf`, no access to `.env` files), and can log every read and write for auditability.

**Pros**
- Strongest filesystem isolation of all four options — Pi has zero direct filesystem access
- MCP server is an explicit, auditable policy enforcement point: every file operation is a named tool call with defined parameters
- All filesystem access is logged by default (MCP tool calls are observable)
- Permission boundaries are expressed in code (the MCP server), not just in Docker config
- Pi can be swapped for any other MCP-compatible agent without changing the isolation layer
- No `docker.sock` required

**Cons**
- Pi does not support MCP natively — requires building or installing an MCP client extension
- Highest setup complexity of all options
- MCP server must be kept up to date and correctly configured — it becomes a security-critical component
- Pi still lacks access to the project's runtime environment for executing code (same limitation as Option B); would need to be combined with Option C's exec approach for full fidelity
- Adds a network hop (Pi → MCP server → filesystem) with associated latency

**Mitigating the runtime environment gap:** If Pi needs to run project code (tests, builds), the MCP server can expose a `run_command` tool that executes inside the devcontainer via a restricted exec interface. This gives the structured mediation of Option D with the environment fidelity of Option C, at the cost of additional complexity.

**Best for:** Scenarios requiring explicit, auditable, policy-enforced filesystem access — e.g. shared or team environments, regulated codebases, or where the agent's filesystem permissions need to be inspectable and version-controlled.

---

## Comparison Summary

| | Option A | Option B | Option C | Option D |
|---|---|---|---|---|
| **Pi location** | Inside devcontainer | Own container | Own container | Own container |
| **File access method** | Direct (co-located) | Shared named volume | `docker exec` / SSH | MCP server |
| **Project env available to Pi** | ✅ Full | ❌ Pi's own env only | ✅ Full | ❌ (unless MCP exposes exec) |
| **Pi config persistence** | ⚠️ Per container | ✅ Centralised | ✅ Centralised | ✅ Centralised |
| **Multi-project in one session** | ❌ | ✅ | ✅ | ✅ |
| **Docker socket required** | ❌ | ❌ | ⚠️ Yes (or proxy) | ❌ |
| **Setup complexity** | Low | Medium | High | Highest |
| **Filesystem isolation (Pi↔host)** | ✅ | ✅ | ✅ | ✅ |
| **Filesystem isolation (Pi↔project)** | ❌ By design | ❌ By design | ✅ Mediated | ✅ Strongly mediated |
| **Access auditability** | ❌ | ❌ | ⚠️ Shell logs only | ✅ Every tool call logged |
| **MCP extension required** | ❌ | ❌ | ❌ | ✅ |

---

## Key Tradeoffs

**Simplicity vs. separation.** Option A is the easiest to reason about and operate. Each subsequent option adds inter-container coordination in exchange for stronger or more explicit isolation.

**Project environment fidelity.** If Pi needs to run code — tests, builds, formatters — it needs the project's runtimes. Options A and C provide this natively. Options B and D do not, unless the MCP server (Option D) or a volume-accessible runner (Option B) is added to bridge the gap.

**Centralised vs. per-project Pi.** Options B, C, and D give you a single Pi instance with stable config, extensions, and history. Option A gives each project its own isolated Pi, which may be preferable for divergent project requirements or strong session isolation.

**The docker.sock decision.** Option C requires `docker.sock` access or a proxy. Options A, B, and D avoid this entirely. If `docker.sock` is used, a restrictive proxy (e.g. [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy)) allowlisted to `exec`-only on named containers is strongly recommended.

**Implicit vs. explicit access control.** Options A, B, and C rely on Docker volume scoping and mount configuration for access control — correct but implicit. Option D makes access control explicit in the MCP server's tool definitions and allowlists, which are inspectable, testable, and version-controllable. This is the meaningful architectural distinction of Option D.

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

## What All Four Options Protect Against

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

- **MCP:** Pi does not include MCP by default. Option D is built around a containerised MCP server; if MCP is added to other options, each MCP server should run in its own container with explicit volume scoping.
- **Egress filtering:** Recommended for sensitive projects; not part of the baseline architecture here.
- **Permission gating:** Pi has no built-in permission popups. If per-action approval is needed, use Pi's `permission-gate.ts` extension example as a starting point.
- **gVisor / VM-based isolation:** Not required for local dev; consider if running untrusted agent extensions or in a multi-user environment.
