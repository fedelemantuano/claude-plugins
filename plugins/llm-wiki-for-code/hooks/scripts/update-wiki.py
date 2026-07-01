#!/usr/bin/env python3
"""PostToolUse hook: regenerate the wiki module doc for an edited source file.

Uses the `claude -p` CLI (no API key, no third-party deps). Never blocks and
emits no output — the edit proceeds even if the wiki update fails.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".rb",
    ".php",
    ".kt",
    ".swift",
    ".scala",
    ".ex",
    ".exs",
}

SKIP_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    "target",
    "dist",
    "build",
    ".venv",
    "venv",
    "vendor",
    "code-docs",  # never recurse into the wiki itself
}

GENERIC_WRAPPERS = {"src", "lib", "app", "pkg", "cmd"}


def get_file_path(tool_input: dict) -> str | None:
    """Extract the edited file path from the tool input."""
    return tool_input.get("path") or tool_input.get("file_path")


def should_update_wiki(file_path: str) -> bool:
    """Return True only for real source files worth documenting."""
    path = Path(file_path)

    if path.suffix not in CODE_EXTENSIONS:
        return False

    if any(part in SKIP_DIRS for part in path.parts):
        return False

    stem = path.stem
    if stem.startswith("test_") or stem.endswith("_test") or stem.endswith(".spec"):
        return False

    return True


def derive_module_name(file_path: str) -> str:
    """Derive a module name from the file path."""
    path = Path(file_path)
    parts = [p for p in path.parts[:-1] if p not in SKIP_DIRS and p not in (".", "..")]

    if not parts:
        # Single file with no meaningful directory — use the stem.
        name = path.stem
    elif parts[0] in GENERIC_WRAPPERS and len(parts) > 1:
        name = parts[1]
    else:
        name = parts[0]

    return name.replace(".", "_").replace("-", "_")


def read_file_safe(path: str, max_chars: int = 5000) -> str:
    """Read a file defensively, truncating at max_chars. Return '' on error."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            content = fh.read(max_chars + 1)
    except OSError:
        return ""

    if len(content) > max_chars:
        return content[:max_chars] + "\n... [truncated]"
    return content


def call_claude(prompt: str) -> str | None:
    """Call the claude CLI in non-interactive mode. Return stdout or None."""
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "claude-haiku-4-5-20251001", prompt],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def update_module_wiki(file_path: str, module_name: str, wiki_dir: Path) -> bool:
    """Regenerate the wiki doc for module_name from the edited source file."""
    file_content = read_file_safe(file_path)

    wiki_file = wiki_dir / f"{module_name}.md"
    if wiki_file.exists():
        existing_wiki = read_file_safe(str(wiki_file), max_chars=2000)
        wiki_context = f"Current wiki section for this module:\n\n{existing_wiki}"
    else:
        wiki_context = "No wiki section exists yet."

    prompt = f"""You are maintaining a concise code wiki for AI coding assistants.

A source file was just edited: `{file_path}`

Current file content (may be truncated):

{file_content}

{wiki_context}

Update or create the wiki section for the module `{module_name}`.

The wiki section must contain:
1. A 2-3 line purpose statement (what the module does and why)
2. **Key files** — list of important files with their paths and one-line descriptions
3. **Public API** — main classes/functions with real signatures from the code
4. **Dependencies** — what the module depends on and why
5. **Gotchas** — non-obvious behavior (omit section if nothing notable)

Rules:
- Max 400 words total
- Use only real signatures from the code above — do not invent them
- Start the response with `# {module_name}` and nothing else before it
- Return ONLY the markdown content, no preamble or commentary

Markdown formatting (must pass markdownlint):
- Exactly one top-level `#` heading; use `##` for every section
- Surround headings and lists with one blank line above and below
- Every fenced code block must declare a language (e.g. ```python)
- No trailing whitespace; end with a single newline"""

    result = call_claude(prompt)
    if result is None:
        return False

    wiki_dir.mkdir(parents=True, exist_ok=True)
    wiki_file.write_text(result + "\n", encoding="utf-8")
    return True


def rebuild_index(docs_dir: Path) -> None:
    """Rewrite code-docs/README.md from the current set of module docs."""
    modules_dir = docs_dir / "modules"

    lines = [
        "# Codebase Wiki",
        "",
        "Auto-maintained by llm-wiki-for-code plugin. Read before exploring source files.",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Modules",
        "",
    ]

    for module_file in sorted(modules_dir.glob("*.md")):
        purpose = ""
        try:
            with open(module_file, encoding="utf-8", errors="replace") as fh:
                for line in (fh.readline() for _ in range(4)):
                    if not line:
                        break
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        purpose = stripped
                        break
        except OSError:
            purpose = ""

        if len(purpose) > 90:
            purpose = purpose[:90] + "…"

        name = module_file.stem
        suffix = f" — {purpose}" if purpose else ""
        lines.append(f"- [`{name}`](modules/{module_file.name}){suffix}")

    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    # Claude Code passes the hook payload as JSON on stdin, not via env vars.
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    tool_input = payload.get("tool_input", {})

    file_path = get_file_path(tool_input)
    if not file_path or not should_update_wiki(file_path):
        return

    module_name = derive_module_name(file_path)
    docs_dir = Path("code-docs")
    wiki_dir = docs_dir / "modules"

    updated = update_module_wiki(file_path, module_name, wiki_dir)
    if updated:
        rebuild_index(docs_dir)


if __name__ == "__main__":
    main()
