# Wiki Structure Reference

Defines the exact format for module docs and the index.

## Module doc format — `code-docs/modules/<module-name>.md`

```markdown
# module-name

Brief purpose — what this module does and why it exists (2-3 lines max).

## Key files
- `path/to/main.py` — entry point, contains X
- `path/to/models.py` — data models for X

## Public API
- `ClassName(arg: Type)` — creates X, call when Y
- `function_name(arg: Type) -> ReturnType` — does X, returns Y

## Dependencies
- `module-a` — used for X
- `external-lib` — version constraint if relevant

## Gotchas
- Non-obvious behavior or constraint (omit section if nothing notable)
```

Rules:

- Max 400 words.
- Real signatures only — never invent them.
- Start with `# module-name`.
- Must pass markdownlint (`.markdownlint-cli2.yaml`): one top-level `#` heading, blank line around every heading and list, a language on every fenced code block (MD040), no trailing whitespace, single trailing newline. `code-docs/` is no longer ignored by the linter, so generated docs are checked like any other markdown.

## Index format — `code-docs/README.md`

```markdown
# Codebase Wiki

Auto-maintained by llm-wiki-for-code plugin. Read before exploring source files.
Last updated: <ISO datetime>

## Modules

- [`module-a`](modules/module-a.md) — brief purpose (one line)
- [`module-b`](modules/module-b.md) — brief purpose (one line)
```

## Language glob patterns

| Language   | Pattern                              |
|------------|--------------------------------------|
| Python     | `**/*.py`                            |
| TypeScript | `**/*.{ts,tsx}` (exclude node_modules) |
| JavaScript | `**/*.{js,jsx}` (exclude node_modules) |
| Go         | `**/*.go`                            |
| Rust       | `**/*.rs` (exclude target/)          |
| Java       | `**/*.java`                          |

Skip test files (`*_test.*`, `test_*`, `*.spec.*`), build artifacts, and vendored code.
