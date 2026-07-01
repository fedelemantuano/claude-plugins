---
name: llm-wiki-for-code
description: Use this skill when the user asks "how does X work", "where is X implemented", "find the module for X", "show me the X code", "I need to change X", or says "initialize wiki", "rebuild wiki", "update wiki", "generate wiki docs". Maintains a structured markdown wiki in code-docs/ that caches codebase knowledge to reduce token usage. Always check code-docs/README.md first.
metadata:
  version: "0.1.0"
---

# LLM Wiki for Code

A pre-built knowledge cache lives in `code-docs/`. Use it instead of exploring source files one by one.

## Navigation Protocol

Before opening any source file:

1. Read `code-docs/README.md` to load the module index.
2. Read only the relevant `code-docs/modules/<name>.md` for the area in question.
3. Only then open source files, limited to what needs editing.
4. If `code-docs/README.md` does not exist, tell the user the wiki is not initialized and offer to initialize it.

## Wiki Initialization

When the user says "initialize wiki" or "rebuild wiki":

1. Scan the codebase with Glob `**/*.{py,js,ts,go,rs,java}` — adapt the pattern to the project's language (see `references/wiki-structure.md`).
2. Group files by top-level module or directory.
3. Create `code-docs/modules/<module-name>.md` per module, following the format in `references/wiki-structure.md`.
4. Generate `code-docs/README.md` as the navigation index.
5. Run `markdownlint-cli2 --fix "code-docs/**/*.md"` so the wiki passes the project's markdown rules. Fix any remaining violations it cannot auto-correct (e.g. MD040 — add a language to every fenced code block).
6. Confirm with the module count.

## Wiki Update After Edits

The PostToolUse hook handles wiki updates automatically after Write, Edit, or MultiEdit.

If a hook update fails silently, regenerate manually: read the edited source file and rewrite the corresponding `code-docs/modules/<module-name>.md`.

## Gotchas

- Never update `code-docs/` files in response to code edits — the hook handles it.
- If the wiki is stale, re-read the source file and update the module doc manually.
- `code-docs/` should be committed to git.
- Skip files under 20 lines — the overhead is not worth it.
