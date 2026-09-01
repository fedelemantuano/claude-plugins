# claude-plugins

Marketplace of Claude Code plugins: one repo shipping several plugins under a single shared version.

## Language

### Marketplace

**Marketplace manifest**:
The single `.claude-plugin/marketplace.json` at the repo root listing every plugin entry.
_Avoid_: Registry, catalog

**Plugin manifest**:
A plugin's `.claude-plugin/plugin.json` — the single source of its name, description, and version.

**Shared version**:
The one semver all plugin manifests carry in lockstep; marketplace entries carry none.

**Container plugin**:
A plugin that groups several skills under one theme (e.g. `spec-driven`), instead of one plugin per skill.

### Spec-driven skills

**Authority**:
The set of written documents that decide whether a change is right: the feature's spec and issues, the ADRs they
cite, the glossary, and the standing rules.
_Avoid_: Guidelines, best practices

**Standing rules**:
The always-applicable rules a repository states in `AGENTS.md` or `CLAUDE.md`, as opposed to per-feature specs.

**Change set**:
The uncommitted work under review: staged, unstaged, and untracked files.
_Avoid_: Diff (the change set includes untracked files a diff omits)

**Conformance review**:
A review that compares the change set against the authority, with every finding citing the written rule it
violates.
_Avoid_: Code review (the generic, taste-based kind)

**Degraded review**:
A conformance review run where no spec governs the change: standing rules and glossary only, declared as such in
the verdict.
