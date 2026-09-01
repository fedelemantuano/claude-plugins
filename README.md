# claude-plugins — Claude Code plugin marketplace

A Claude Code / Cowork plugin **marketplace**. It bundles one or more plugins under
a single install source, described by
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Add the
marketplace once, then install any plugin from it:

```text
/plugin marketplace add fedelemantuano/claude-plugins
/plugin install <plugin-name>@fedelemantuano-claude-plugins
```

Each plugin lives in its own directory under [`plugins/`](plugins/) with its own
`.claude-plugin/plugin.json`. New plugins are added by dropping a directory there
and appending an entry to `marketplace.json`.

## Plugins in this marketplace

| Plugin | What it does |
| ------ | ------------ |
| [`llm-wiki-for-code`](#llm-wiki-for-code--complete-user-guide) | Maintains a structured code wiki in `code-docs/`, auto-updated after every file edit, to cut token usage in coding sessions |
| [`spec-driven`](#spec-driven) | Skills for repositories that write their decisions down; ships `conformance-review` (citation-required review of uncommitted changes against the repo's specs, ADRs, glossary, and standing rules) and `prove-it-works` (evidence-based verification of branch work) |

More plugins will be added here over time.

---

## spec-driven

Skills for repositories where written documents — a spec and issues per feature, ADRs, a `CONTEXT.md` glossary,
standing rules in `AGENTS.md`/`CLAUDE.md` — decide whether code is right.

### conformance-review

Reviews the change you have not committed yet (staged, unstaged, and untracked files) against the repository's
written authority. It discovers where specs and rules live by following the repo's own pointers first
(`CLAUDE.md`/`AGENTS.md` and the docs they cite), then probing common homes (`.scratch/<feature>/`,
`docs/features/<slug>/`, `docs/specs/`, `docs/adr/`).

- Every finding cites the exact written rule it violates; findings without a citation are dropped or reported as
  open questions.
- Report-only: no fixes, no test runs — mandatory gates are named, not executed.
- Without a governing spec it degrades openly to a standards-only review and says so in the verdict.

Trigger it by asking for a review of your changes, a pre-commit check, or whether an issue's work is finished —
or invoke it directly with `/spec-driven:conformance-review`.

### prove-it-works

The running counterpart of `conformance-review`. Diffs `HEAD` against the fork point with the default branch,
discovers how the repository runs and tests itself (workflow rules, CI, build files), executes those gates, and
reports evidence per claim — **verified**, **failed**, or **unverified**, never "should work".

- Report-only on failures: it proves, it does not fix, and it never runs anything with effects beyond the local
  checkout (no deploys, no publishing, no real-data migrations).
- When a gate fails, it chains into `conformance-review` to explain the failure against the written spec, and
  delivers evidence and review together.

Trigger it by asking "does it work", "prove it", "is this done", or for verification before a merge — or invoke it
directly with `/spec-driven:prove-it-works`.

---

## llm-wiki-for-code — Complete User Guide

A Claude Code / Cowork plugin that maintains a structured code wiki in `code-docs/`
and automatically keeps it up to date after every file edit, reducing token usage
in coding sessions by replacing blind file exploration with a pre-built knowledge
cache.

## Table of Contents

1. [How It Works](#1-how-it-works)
2. [Prerequisites](#2-prerequisites)
3. [Installation](#3-installation)
4. [First-Time Setup](#4-first-time-setup)
5. [Daily Usage](#5-daily-usage)
6. [Wiki Structure](#6-wiki-structure)
7. [Commands Reference](#7-commands-reference)
8. [Uninstallation](#8-uninstallation)
9. [Troubleshooting](#9-troubleshooting)
10. [Configuration Reference](#10-configuration-reference)

---

## 1. How It Works

```text
┌─────────────────────────────────────────────────────────────┐
│  WITHOUT llm-wiki-for-code                                  │
│                                                             │
│  Claude explores the codebase blind:                        │
│  ls → Glob → Read file.py → Read utils.py → Read models.py  │
│  → Read config.py → Read api.py → ... → finally edits       │
│                                                             │
│  Cost: 20,000–100,000 tokens per session just to orient     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  WITH llm-wiki-for-code                                     │
│                                                             │
│  SessionStart hook → "Wiki available: 12 modules"           │
│  Claude reads code-docs/README.md →                         │
│  → code-docs/modules/auth.md → opens only auth.py → edits   │
│  PostToolUse hook → regenerates code-docs/modules/auth.md   │
│                                                             │
│  Cost: 1,000–3,000 tokens to orient. 30–55% total savings.  │
└─────────────────────────────────────────────────────────────┘
```

### Components

| Component | Type | What it does |
| --------- | ---- | ------------ |
| `plugins/llm-wiki-for-code/skills/llm-wiki-for-code` | Skill | Teaches Claude to read `code-docs/` before source files |
| `plugins/llm-wiki-for-code/hooks/hooks.json` | Hook config | Registers PostToolUse and SessionStart events |
| `plugins/llm-wiki-for-code/hooks/scripts/update-wiki.py` | PostToolUse hook | Regenerates the wiki section for the edited file |
| `plugins/llm-wiki-for-code/hooks/scripts/check-wiki.sh` | SessionStart hook | Reports wiki status (module count, last updated) |

### Token flow per session

```text
Session start
  └─► check-wiki.sh prints wiki status (~50 tokens context)
        └─► Claude reads code-docs/README.md (~300 tokens)
              └─► Claude reads relevant code-docs/modules/*.md (~500 tokens)
                    └─► Claude reads only the target source file (~2,000 tokens)
                          └─► Edit happens
                                └─► update-wiki.py regenerates module doc
                                      └─► code-docs/README.md index rebuilt
```

---

## 2. Prerequisites

- **Claude Code** — any version that supports plugins and hooks
- **Python 3.10+** — available as `python3` in PATH. Required: the hook uses `X | None` type annotations (PEP 604), evaluated at definition time
- **Bash** — for the SessionStart hook script
- **`claude` CLI** — available in PATH (installed automatically with Claude Code)

No API key configuration needed. The hook uses `claude -p`, which inherits
authentication from the running Claude Code session.

---

## 3. Installation

The plugin is distributed as a Claude Code marketplace — this Git repository,
described by [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).
Installation is done with the `/plugin` command inside a Claude Code session.

### Option A — Install from GitHub (recommended)

In a Claude Code session, add the marketplace and install the plugin:

```text
/plugin marketplace add fedelemantuano/claude-plugins
/plugin install llm-wiki-for-code@fedelemantuano-claude-plugins
```

`fedelemantuano-claude-plugins` is the marketplace name defined in `marketplace.json`;
`llm-wiki-for-code` is the plugin name.

### Option B — Install from a local clone

If you have the repository checked out locally:

```text
/plugin marketplace add /path/to/claude-plugins
/plugin install llm-wiki-for-code@fedelemantuano-claude-plugins
```

The path must point at the directory containing `.claude-plugin/marketplace.json`.

### Verifying the installation

In a Claude Code session, run:

```text
/plugin
```

You should see `llm-wiki-for-code` listed as installed. The SessionStart hook also
prints a status message at the beginning of every new session once the plugin is
active.

---

## 4. First-Time Setup

### Step 1 — Open a Claude Code session in your project

```bash
cd /path/to/your/project
claude
```

### Step 2 — Initialize the wiki

Say:

> initialize wiki

Claude will:

1. Scan the project with Glob for source files
2. Group files by module/directory
3. Create `code-docs/modules/<name>.md` for each module
4. Generate `code-docs/README.md` as the navigation index
5. Report how many modules were documented

Initialization is performed by the Claude Code session itself (following the
`llm-wiki-for-code` skill), using whatever model your session runs. It takes
1–5 minutes depending on project size. The `claude -p` Haiku call is used only by
the PostToolUse hook on later edits — not during initialization.

### Step 3 — Commit the wiki

```bash
git add code-docs/
git commit -m "chore: initialize llm-wiki-for-code"
```

The `code-docs/` folder is a project artifact and should be version-controlled.
Teammates with the plugin installed benefit from the cached wiki immediately on
clone.

### Step 4 — (Optional) Add `code-docs/` to `.gitattributes`

To keep wiki diffs clean:

```text
code-docs/modules/*.md linguist-generated=true
```

---

## 5. Daily Usage

### Normal workflow — no action needed

After initialization, the plugin works silently:

- **Every new session** — the SessionStart hook prints wiki availability
- **Every file edit** — the PostToolUse hook regenerates the relevant module doc
- Claude reads `code-docs/README.md` automatically before exploring source files

### What Claude does differently

**Without the plugin:**

```text
You: "Add rate limiting to the auth module"
Claude: [reads 8 files to understand the codebase]
Claude: [finally edits auth.py]
```

**With the plugin:**

```text
You: "Add rate limiting to the auth module"
Claude: [reads code-docs/README.md]
Claude: [reads code-docs/modules/auth.md]
Claude: [reads auth.py]
Claude: [edits auth.py]
PostToolUse hook: [regenerates code-docs/modules/auth.md]
```

### Checking wiki status

> what does the wiki cover?

or

> show me the wiki index

### Forcing a full rebuild

If many files changed outside Claude Code (e.g. after a large merge):

> rebuild wiki

Claude regenerates all module docs from scratch.

### Updating a single module manually

If the hook failed silently for a specific file:

> update the wiki for the auth module

---

## 6. Wiki Structure

After initialization, your project contains:

```text
code-docs/
├── README.md              ← navigation index (auto-generated)
└── modules/
    ├── auth.md
    ├── api.md
    ├── models.md
    └── utils.md
```

### `code-docs/README.md` — the index

```markdown
# Codebase Wiki

Auto-maintained by llm-wiki-for-code plugin. Read before exploring source files.
Last updated: 2026-06-29 14:32

## Modules

- [`auth`](modules/auth.md) — JWT authentication and session management
- [`api`](modules/api.md) — REST endpoint handlers and middleware
- [`models`](modules/models.md) — SQLAlchemy ORM models for all entities
- [`utils`](modules/utils.md) — Shared helpers: logging, validation, formatting
```

### `code-docs/modules/<name>.md` — a module doc

```markdown
# auth

Handles JWT token issuance, validation, and session lifecycle.
Used by all protected API endpoints via the `@require_auth` decorator.

## Key files
- `auth/jwt.py` — token creation and verification logic
- `auth/middleware.py` — Flask decorator for route protection
- `auth/models.py` — User and Session ORM models

## Public API
- `create_token(user_id: int, expires_in: int = 3600) -> str` — issues a signed JWT
- `verify_token(token: str) -> dict | None` — decodes and validates, returns claims or None
- `require_auth(f)` — decorator that extracts token from Authorization header

## Dependencies
- `auth/models.py` — for User lookup during token verification
- `PyJWT` — JWT encoding/decoding library

## Gotchas
- Tokens are not stored server-side; revocation requires a Redis blocklist (not yet implemented)
- `verify_token` returns `None` on expiry — callers must handle this explicitly
```

### What the wiki captures vs. what it does not

| Captured | Not captured |
| -------- | ------------ |
| Module purpose and responsibilities | Runtime behavior |
| Public API signatures | Dynamic dispatch |
| Inter-module dependencies | Test coverage |
| Non-obvious constraints | Inline comments |
| File-level organization | Git history |

For runtime and architectural context not in the AST, add an
`## Architecture Notes` section to `code-docs/README.md` manually.

---

## 7. Commands Reference

These are natural-language phrases you say to Claude:

| Phrase | What happens |
| ------ | ------------ |
| `initialize wiki` | Full scan and wiki generation from scratch |
| `rebuild wiki` | Regenerate all module docs (use after large merges) |
| `update the wiki for <module>` | Regenerate one module doc manually |
| `what does the wiki cover?` | Show the wiki index |
| `show me the wiki for <module>` | Display a specific module doc |
| `how does <feature> work?` | Claude reads the relevant module doc first |
| `where is <thing> implemented?` | Claude checks the wiki index first |

---

## 8. Uninstallation

### Remove the plugin

In a Claude Code session:

```text
/plugin uninstall llm-wiki-for-code@fedelemantuano-claude-plugins
```

To also drop the marketplace entry:

```text
/plugin marketplace remove fedelemantuano-claude-plugins
```

### Remove the wiki from your project

```bash
rm -rf code-docs/
git add -A
git commit -m "chore: remove llm-wiki-for-code docs"
```

### Partial removal — keep docs, remove plugin

To keep the generated `code-docs/` folder as static documentation but stop
auto-updating it, just uninstall the plugin. The docs remain in your repo and
Claude can still read them — the hook just won't update them.

---

## 9. Troubleshooting

### Wiki not updating after edits

**Symptom:** `code-docs/modules/` is not updated after file edits.

**Checks:**

1. Verify `claude` is in PATH from your shell:

   ```bash
   which claude
   ```

2. Check that the plugin is installed and active:

   ```text
   /plugin
   ```

3. Run the hook manually on a test file to see errors. From a clone of this
   repository:

   ```bash
   TOOL_INPUT='{"path":"your_file.py"}' python3 plugins/llm-wiki-for-code/hooks/scripts/update-wiki.py
   ```

   The script reads the tool payload from the `TOOL_INPUT` environment variable
   (see `main()` in `update-wiki.py`).

**Common cause:** `claude` binary not in PATH for the shell Claude Code uses.
**Fix:** Add Claude Code's bin directory to your shell profile (`~/.zshrc` or `~/.bashrc`).

### SessionStart message not appearing

**Symptom:** No `[llm-wiki-for-code]` message at session start.

**Check:** Verify `bash` is available:

```bash
which bash
```

**Fix on non-standard systems:** Edit `plugins/llm-wiki-for-code/hooks/hooks.json` to use `sh` instead of `bash`:

```json
"command": "sh ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/check-wiki.sh"
```

### `claude -p` call times out

**Symptom:** Wiki updates are slow or fail silently on large files.

There are two timeouts, and the shorter one wins:

- The `claude -p` subprocess call in `update-wiki.py` (`call_claude`, `timeout=60`).
  This is the real limiter on slow generations.
- The hook wrapper in `plugins/llm-wiki-for-code/hooks/hooks.json` (`"timeout": 90`), which kills the whole
  hook process.

For very large files, raise **both**. In `update-wiki.py`:

```python
result = subprocess.run(
    ["claude", "-p", "--model", "claude-haiku-4-5-20251001", prompt],
    capture_output=True,
    text=True,
    timeout=120,
)
```

And in `plugins/llm-wiki-for-code/hooks/hooks.json`, set a wrapper timeout above the subprocess one:

```json
{
  "type": "command",
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/update-wiki.py",
  "timeout": 150
}
```

### Wiki becomes stale after a large merge

**Cause:** Files changed outside Claude Code sessions (git merge, rebase, bulk refactor).

**Fix:** Say `rebuild wiki` in a Claude Code session. Claude regenerates all
module docs from the current state of the codebase.

### Module docs are too generic

**Cause:** The source file is very large and was truncated (default: 5000 chars).

**Fix:** Edit `update-wiki.py` and increase `max_chars` in `read_file_safe`:

```python
file_content = read_file_safe(file_path, max_chars=10000)
```

**Note:** larger values increase the token cost of each hook call.

### `code-docs/` is being committed with every edit

**Expected behavior** — this is by design. Each `git status` shows modified wiki
files. Use a `.gitattributes` rule to reduce diff noise:

```text
code-docs/modules/*.md linguist-generated=true
```

Or commit wiki updates separately at the end of a session:

```bash
git add code-docs/ && git commit -m "chore: update wiki"
```

---

## 10. Configuration Reference

All configuration is done by editing the plugin files directly after installation.

### Change the model used for wiki updates

In `plugins/llm-wiki-for-code/hooks/scripts/update-wiki.py`, find the `call_claude` function:

```python
["claude", "-p", "--model", "claude-haiku-4-5-20251001", prompt]
```

Replace with any model available in your Claude Code session:

- `claude-haiku-4-5-20251001` — fastest, cheapest (default)
- `claude-sonnet-4-6` — higher quality, slower

### Skip additional file types

In `update-wiki.py`, add to `CODE_EXTENSIONS` or `SKIP_DIRS`:

```python
# Skip infrastructure files
SKIP_DIRS = {
    ...,
    "migrations",   # database migrations
    "scripts",      # ad-hoc scripts
}
```

### Skip test files with different naming conventions

The default skips `test_*`, `*_test`, and `*.spec`. To add more:

```python
def should_update_wiki(file_path: str) -> bool:
    ...
    if any(pat in name for pat in ("test_", "_test", ".spec", "_spec", "fixture")):
        return False
```

### Change wiki max word count

In the `update_module_wiki` function prompt, change `Max 400 words total` to your
preferred length. Longer docs = more accurate but more tokens per read.

### Disable automatic index rebuild

If index rebuilds are slow, comment out the `rebuild_index` call in `main()`:

```python
updated = update_module_wiki(file_path, module_name, wiki_dir)
if updated:
    pass  # rebuild_index(docs_dir)  # disabled for speed
```

Then run `rebuild wiki` manually when you want the index updated.
