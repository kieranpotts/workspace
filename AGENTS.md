# Personal Workspace

## Project overview

This is the root workspace for my personal code repositories. It is not itself an application — it provides scripts to clone/sync all the personal repositories listed in `repos.yaml` into a consistent directory layout (`~/dev/personal/<owner>/<repo>/<worktree>`), a VS Code multi-root workspace configuration, and a devcontainer for running the whole workspace in an isolated environment. Agents operating here are typically working across multiple sibling repositories, not just this one.

## Tech stack

- Python 3 (`run/install.py` and other workspace scripts).
- Git, using the bare-clone-plus-worktrees pattern (see `repos.yaml` header comment).
- VS Code multi-root workspace (`personal.code-workspace`).
- Docker / devcontainer for an isolated environment.

## Repository structure

- `run/`: Installation and sync scripts (e.g. `install.py`), which read `repos.yaml` and set up bare clones + worktrees for every project, plus linked assets like `.devcontainer` and the VS Code workspace file.

- `docs/`: Requirements, installation, and usage documentation for this workspace.

- `repos.yaml`: The manifest of all managed repositories — name, URL, and worktrees (branch checkouts).

- `personal.code-workspace`: VS Code multi-root workspace definition, linked into each project per `LINKED_ASSETS` in `run/install.py`.

- `.devcontainer`: Devcontainer config, also linked into each project.

## Tools

- `python run/install.py` to clone/update all repositories in `repos.yaml` and link shared assets (`.devcontainer`, `personal.code-workspace`) into each one.

## Projects in this workspace

Each project below is checked out as a sibling directory at `~/dev/personal/<owner>/<name>/<worktree>` (worktree is usually `default`). Most have their own `AGENTS.md` or `README.md` with project-specific detail — consult those when working inside a given project.

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
  This repository.

- **`srcflow/srcflow`**: \
  Srcflow project (separate GitHub org).

- **`srcflow/sh`**: \
  Srcflow shell scripts (separate GitHub org).

- **`nirvarnia/brand`**: \
  Nirvarnia brand assets (separate GitHub org).

## Rules

The capitalized words REQUIRED, MUST, MUST NOT, RECOMMENDED, SHOULD, SHOULD NOT, OPTIONAL, and MAY, in the context of this document and agent skills/instructions/rules, are to be interpreted as described in [IETF RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

- MUST NOT modify `repos.yaml` worktree branches without confirming with the user, since this changes what gets checked out on next install.

- SHOULD treat each sibling project directory as its own repository with its own conventions — defer to a project's own `AGENTS.md`/`README.md` when working inside it.

- SHOULD keep this file's project list in sync with `repos.yaml` when repositories are added or removed.

## Skills

No project-specific skills are currently installed for this workspace.
