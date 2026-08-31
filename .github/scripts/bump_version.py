#!/usr/bin/env python3
"""Bump the semver `version` field in the plugin and marketplace manifests.

Usage: bump_version.py {major|minor|patch}

Rewrites plugins/llm-wiki-for-code/.claude-plugin/plugin.json and the matching
entry in .claude-plugin/marketplace.json in place, and writes
`previous_version` / `new_version` to $GITHUB_OUTPUT when running in Actions.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

MANIFEST = Path("plugins/llm-wiki-for-code/.claude-plugin/plugin.json")
MARKETPLACE = Path(".claude-plugin/marketplace.json")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def bump(version: str, release_type: str) -> str:
    match = SEMVER.match(version)
    if not match:
        sys.exit(f"error: version {version!r} in {MANIFEST} is not MAJOR.MINOR.PATCH")

    major, minor, patch = (int(part) for part in match.groups())
    if release_type == "major":
        return f"{major + 1}.0.0"
    if release_type == "minor":
        return f"{major}.{minor + 1}.0"
    if release_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    sys.exit(f"error: unknown release type {release_type!r}")


def rewrite_version(path: Path, previous: str, new: str) -> None:
    # Line-level substitution keeps the manifest's hand-written formatting.
    raw = path.read_text()
    updated, count = re.subn(
        rf'"version":\s*"{re.escape(previous)}"', f'"version": "{new}"', raw, count=1
    )
    if count != 1:
        sys.exit(f"error: could not rewrite the version field in {path}")
    path.write_text(updated)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    previous = json.loads(MANIFEST.read_text())["version"]
    new = bump(previous, sys.argv[1])

    rewrite_version(MANIFEST, previous, new)
    rewrite_version(MARKETPLACE, previous, new)

    print(f"{previous} -> {new}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as handle:
            handle.write(f"previous_version={previous}\n")
            handle.write(f"new_version={new}\n")


if __name__ == "__main__":
    main()
