# Personal Workspace

## Project overview

This file describes my personal development workspace as a whole: a tree of independent Git repositories checked out as siblings under `~/dev/personal/<owner>/<name>/<worktree>`. It is installed at the root of that tree (`~/dev/personal/AGENTS.md`), so any agent working inside any one of these projects can see this file in a parent directory and understand the wider context — what the other sibling projects are, and how they relate. This file does not describe any single repository's internals; each project has its own `AGENTS.md` and/or `README.md` for that.

## Repository structure

Every project lives at `~/dev/personal/<owner>/<name>/<worktree>`, using a bare-clone-plus-worktrees layout:

- `<owner>/<name>/.bare`: Bare clone (Git internals only).
- `<owner>/<name>/.git`: Pointer file (`gitdir: ./.bare`) so Git commands work from the project root.
- `<owner>/<name>/<worktree>`: A working tree checked out at a specific branch (usually named `default`).

## Projects in this workspace

- **`__TODO__`**: \
  Personal task/TODO tracking.

- **`.github`**: \
  Org-wide default GitHub community health files and workflows.

- **`actions`**: \
  Custom reusable GitHub Actions for CI/CD pipelines.

- **`asciibook`**: \
  Template toolchain for authoring technical books from AsciiDoc source.

- **`avatar`**: \
  Source/distributable files for the online profile icon.

- **`blueprints`**: \
  System design studies for fictional application software.

- **`bookmarks`**: \
  Curated list of interesting destinations on the web.

- **`bootstrap`**: \
  Provisioning scripts for the standard local dev environment.

- **`cheats`**: \
  Cheat sheets (under reconstruction).

- **`cover-letter`**: \
  Source content and build scripts for job application cover letters.

- **`design`**: \
  Template for maintaining a system's architectural artifacts via version control.

- **`devboxes`**: \
  Archived; no longer maintained.

- **`devtools`**: \
  Dev tool configs, programming fonts, and Windows ports of Unix tools.

- **`dictionary`**: \
  Custom spelling dictionaries for the Code Spell Checker VS Code extension.

- **`docker-devcontainer`**: \
  Builds the Docker image for the personal-projects dev environment.

- **`docker-latex`**: \
  Builds a Docker image for LaTeX compilation.

- **`dotfiles`**: \
  Personal Unix dotfiles.

- **`eslint-config`**: \
  Shared ESLint configuration package.

- **`garden`**: \
  Source content for the digital garden (kieranpotts.com/garden).

- **`genies`**: \
  Self-hosted open source AI models (DeepSeek, Llama, Qwen) via Ollama in Docker.

- **`gitex`**: \
  Git extensions suite (`git sync`, `git amend`, `git squash`, `git fixup`, `git undo`).

- **`interviews`**: \
  Behavioral interview Q&A prep for software roles.

- **`json-schema`**: \
  Collection of common JSON Schema type definitions.

- **`kieranpotts`**: \
  Personal/profile repository.

- **`lumex`**: \
  Template for new code repositories.

- **`makebook`**: \
  Archived.

- **`modelfiles`**: \
  Custom Ollama model definitions.

- **`ocean`**: \
  Archived; superseded by `lumex`.

- **`papers`**: \
  Academic papers and research in software engineering / computer science.

- **`pi`**: \
  AI agent harness infrastructure, built around the Pi coding agent (under construction).

- **`plans`**: \
  Template for planning implementation of changes via version control.

- **`playbook`**: \
  Template for new code repositories.

- **`popos`**: \
  Pop!_OS configuration backup.

- **`pre-commit-hooks`**: \
  Reusable hook configs for the `pre-commit` framework.

- **`prototypes`**: \
  Archived prototypes.

- **`resume`**: \
  Source content and build scripts for CV, compiled from LaTeX.

- **`rfc`**: \
  Template for managing technical decisions via version control.

- **`sh`**: \
  Archived shell scripts.

- **`skills`**: \
  Reusable agent skills (under construction).

- **`specs`**: \
  Template for managing the lifecycle of software requirements via version control.

- **`standards`**: \
  Coding/process standards (under reconstruction).

- **`template`**: \
  Generic template for new code repositories (source of templates like this `AGENTS.md`).

- **`tests`**: \
  Take-home tests for technical IT roles.

- **`the-timeless-way`**: \
  Software development playbook/methodology.

- **`thoughts`**: \
  Source content for the blog (kieranpotts.com/thoughts).

- **`website`**: \
  kieranpotts.com static site, built with Antora from AsciiDoc, aggregating `garden`, `thoughts`, and `bookmarks` at build time.

- **`website-ui`**: \
  Archived; portable Antora UI theme reference, now maintained in `website`.

- **`workspace`**: \
  Root workspace repository — provides the scripts and manifest (`repos.yaml`, `run/install.py`) that clone/sync all the repositories listed above into this directory layout, plus shared assets (VS Code multi-root workspace, devcontainer, this file) symlinked into `~/dev/personal`.

- **`srcflow/srcflow`**: \
  Srcflow project (separate GitHub org).

- **`srcflow/sh`**: \
  Srcflow shell scripts (separate GitHub org).

- **`nirvarnia/brand`**: \
  Nirvarnia brand assets (separate GitHub org).

## Rules

The capitalized words REQUIRED, MUST, MUST NOT, RECOMMENDED, SHOULD, SHOULD NOT, OPTIONAL, and MAY, in the context of this document and agent skills/instructions/rules, are to be interpreted as described in [IETF RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

- MUST treat each project directory as its own repository with its own conventions — defer to that project's own `AGENTS.md`/`README.md` when working inside it.

- MUST NOT make changes that span multiple sibling project directories as a single unit of work — each is an independently versioned repository; commit/PR within one project at a time unless the user explicitly asks for a cross-repo change.

- SHOULD consult the `workspace` repository (`repos.yaml`, `run/install.py`) for how this directory layout is maintained, if asked to add, remove, or resync a project.
