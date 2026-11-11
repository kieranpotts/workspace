# 📜 Architecture decision records

This is a permanent, append-only archive of every significant technical decision
made about this project, including ideas that were ultimately rejected.

An ADR covers a technical decision — _how_ the system is built. Product
decisions — _what_ the system should do — belong in the
[requirements](../requirements.md).

## Structure

One file per decision, numbered in the order the decisions were made.

```
decisions/
├── TEMPLATE.md         # The starting point for a new record.
└── 0001-<slug>/        # One decision.
    ├── README.md       # The decision record itself.
    └── …               # Diagrams and other materials referenced from the README.
```

An ADR's index number is unique and permanent.

## Lifecycle

```
PROPOSED ──> ACCEPTED ──> SUPERSEDED
    │
    └──────> REJECTED
```

A record is written as `PROPOSED`, reviewed via a pull request, and merged once
it is `ACCEPTED` or `REJECTED`.

Once merged, the document is immutable. Only the value of a merged report's
`Status` field may later be changed to `SUPERSEDED`, with a pointer added to
the newer decision record that overrides it.

To revisit a past decision, write a new record. Do not edit an old one.

## Index

- [0001 One devcontainer for the whole workspace](./0001-workspace-devcontainer/README.md)
- [0002 Native builds for applyto, website, and resume](./0002-native-builds/README.md)
- [0003 No Docker in the workspace devcontainer](./0003-no-docker-in-devcontainer/README.md)
- [0004 Agent skills installed on devcontainer start](./0004-agent-skills-in-devcontainer/README.md)
