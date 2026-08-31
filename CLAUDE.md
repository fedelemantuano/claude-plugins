# claude-plugins

Marketplace of Claude Code plugins. Manifest: `.claude-plugin/marketplace.json`; each plugin lives under `plugins/<name>/` with its own `.claude-plugin/plugin.json`. All plugins share one version; `plugin.json` is the single version source (marketplace entries carry none).

## Workflow

- After changing code or docs, run `pre-commit run --files <changed files>` and fix failures before committing.
- When adding a new plugin under `plugins/`, update `README.md`: add a row to the "Plugins in this marketplace" table and a section documenting the plugin (what it does, install, usage).

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
