#!/usr/bin/env bash
# UserPromptSubmit hook: nudge to use the wiki before grepping source.
# Emits one line only when the wiki exists. Never blocks (always exit 0).

if [ -f "code-docs/README.md" ]; then
    echo "[llm-wiki-for-code] Wiki at code-docs/README.md exists — read it (and the relevant code-docs/modules/*.md) before grepping or opening source files."
fi

exit 0
