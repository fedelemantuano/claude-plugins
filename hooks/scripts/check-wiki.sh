#!/usr/bin/env bash
# SessionStart hook: announce wiki status.

WIKI_INDEX="code-docs/README.md"
MODULES_DIR="code-docs/modules"

if [ -f "$WIKI_INDEX" ]; then
    if [ -d "$MODULES_DIR" ]; then
        MODULE_COUNT=$(find "$MODULES_DIR" -maxdepth 1 -name '*.md' -type f | wc -l | tr -d ' ')
    else
        MODULE_COUNT=0
    fi

    LAST_MODIFIED=$(date -r "$WIKI_INDEX" "+%Y-%m-%d %H:%M" 2>/dev/null || \
                    stat -c "%y" "$WIKI_INDEX" 2>/dev/null | cut -d'.' -f1)

    echo "[llm-wiki-for-code] Wiki available: ${MODULE_COUNT} module(s) in code-docs/modules/. Last updated: ${LAST_MODIFIED}"
    echo "[llm-wiki-for-code] Read code-docs/README.md before exploring source files to reduce token usage."
else
    echo "[llm-wiki-for-code] Wiki not initialized. Ask the user to run 'initialize wiki' to generate code-docs/ from the codebase."
fi
