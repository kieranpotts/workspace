# Personal workspace

This file describes my personal development workspace as a whole. It's a tree
of independent Git repositories checked out as siblings under
`~/dev/personal/<owner>/<name>/<worktree>`.

This file is symlinked at the root of that tree (`~/dev/personal/AGENTS.md`),
so any agent working inside any one of these projects can see this file in a
parent directory and understand the wider context — what the other sibling
projects are, and how they relate.

This file does not describe any single repository's internals. Each repository
has its own `AGENTS.md` and/or `README.md` for that.

The capitalized words REQUIRED, MUST, MUST NOT, RECOMMENDED, SHOULD,
SHOULD NOT, OPTIONAL, and MAY are to be interpreted as described in
[IETF RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Workspace projects

These are all the projects in this workspace:

- **`__TODO__`**: \
  Personal task/TODO tracking.

- **`.github`**: \
  Workspace-wide default GitHub community health files and workflows.

- **`actions`**: \
  Custom reusable GitHub Actions for CI/CD pipelines.

- **`asciibook`**: \
  Toolchain for authoring technical books from AsciiDoc source.

- **`avatar`**: \
  Source and distributable files for my online profile icon.

- **`blueprints`**: \
  System design studies for fictional application software.

- **`bookmarks`**: \
  Curated list of interesting destinations on the web.

- **`bootstrap`**: \
  Provisioning scripts for my standard local dev environment.

- **`cheats`**: \
  Cheat sheets for various dev and ops tools.

- **`cover-letter`**: \
  Source content and build scripts for job application cover letters.

- **`design`**: \
  Template for maintaining a system's architectural artifacts via version control.

- **`devboxes`**: \
  Vagrant configs for dev VMs. No longer maintained.

- **`devtools`**: \
  Dev tool configs, programming fonts, and Windows ports of Unix tools.

- **`dictionary`**: \
  Custom spelling dictionaries for the Code Spell Checker VS Code extension.

- **`docker-devcontainer`**: \
  Builds the Docker image for my personal projects' dev environment.

- **`docker-latex`**: \
  Builds a Docker image for LaTeX compilation.

- **`dotfiles`**: \
  Personal Unix dotfiles.

- **`eslint-config`**: \
  Shared ESLint configuration package.

- **`garden`**: \
  Source content for my digital garden.

- **`genies`**: \
  Self-hosted open source AI models via Ollama running in Docker.

- **`gitex`**: \
  Git extensions suite – `git sync`, `git amend`, `git squash`, `git undo`, etc.

- **`interviews`**: \
  Behavioral interview Q&A prep for software roles.

- **`json-schema`**: \
  Collection of common JSON Schema type definitions.

- **`kieranpotts`**: \
  GitHub profile page.

- **`lumex`**: \
  VS Code theme.

- **`makebook`**: \
  VM and starter kit for making books with Pandoc. Archived.

- **`modelfiles`**: \
  Custom Ollama model definitions.

- **`ocean`**: \
  VS Code theme. Archived; superseded by `lumex`.

- **`papers`**: \
  Academic papers and research in software engineering / computer science.

- **`pi`**: \
  AI agent harness infrastructure, built around the Pi coding agent.

- **`plans`**: \
  Template for planning implementation of changes via version control.

- **`playbook`**: \
  Software development methods and tools.

- **`popos`**: \
  Pop!_OS configuration backup.

- **`pre-commit-hooks`**: \
  Reusable hook configs for the `pre-commit` framework.

- **`prototypes`**: \
  Archived prototypes for web UI components. No longer maintained.

- **`resume`**: \
  Source content and build scripts for CV, compiled from LaTeX.

- **`rfc`**: \
  Template for managing technical decisions via version control.

- **`sh`**: \
  Archived shell scripts.

- **`skills`**: \
  Reusable agent skills.

- **`specs`**: \
  Template for managing the lifecycle of software requirements via version control.

- **`standards`**: \
  Coding/process standards.

- **`template`**: \
  Generic template for new code repositories.

- **`tests`**: \
  Take-home tests for technical IT roles.

- **`the-timeless-way`**: \
  Software development playbook/methodology in book form.

- **`thoughts`**: \
  Source content for my blog.

- **`website`**: \
  kieranpotts.com static site, built with Antora from AsciiDoc.

- **`website-ui`**: \
  Archived; portable Antora UI theme reference, now maintained in `website`.

- **`workspace`**: \
  Root workspace repository.

- **`srcflow/srcflow`**: \
  Srcflow project (separate GitHub org).

- **`srcflow/sh`**: \
  Srcflow shell scripts (separate GitHub org).

- **`nirvarnia/brand`**: \
  Nirvarnia brand assets (separate GitHub org).

## Project structure

Every project lives at `~/dev/personal/<owner>/<name>/<worktree>`, using a
bare-clone-plus-worktrees layout:

- `<owner>/<name>/.bare`: Bare clone (Git internals only).

- `<owner>/<name>/.git`: Pointer file (`gitdir: ./.bare`) so Git commands
  work from the project root.

- `<owner>/<name>/<worktree>`: A working tree checked out at a specific branch.
  There's always a `default` worktree, which is used to check out the branch
  that's configured as the default in the upstream reference repository.

## Rules

- MUST treat each project directory as its own repository with its own
  conventions. Defer to that project's own `AGENTS.md`/`README.md` when
  working inside it.

- MUST NOT make changes that span multiple sibling project directories as a
  single unit of work. Each is an independently versioned repository.
  Commit/PR within one project at a time, unless the user explicitly asks
  for a cross-repo change.
