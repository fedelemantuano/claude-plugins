#!/usr/bin/env python3
"""Bump the shared semver `version` field in every plugin manifest.

Usage: bump_version.py {major|minor|patch}

All plugins under plugins/ share one version. Rewrites each
plugins/*/.claude-plugin/plugin.json in place, and writes
`previous_version` / `new_version` to $GITHUB_OUTPUT when running in Actions.
The marketplace manifest carries no version — plugin.json is the single source.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PLUGINS_DIR = Path("plugins")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def plugin_manifests() -> list[Path]:
    manifests = sorted(PLUGINS_DIR.glob("*/.claude-plugin/plugin.json"))
    if not manifests:
        sys.exit(f"error: no plugin manifests found under {PLUGINS_DIR}/")
    return manifests


def current_version(manifests: list[Path]) -> str:
    versions = {path: json.loads(path.read_text())["version"] for path in manifests}
    unique = set(versions.values())
    if len(unique) != 1:
        details = ", ".join(f"{path}={version}" for path, version in versions.items())
        sys.exit(f"error: plugin versions diverge — {details}")
    return unique.pop()


def bump(version: str, release_type: str) -> str:
    match = SEMVER.match(version)
    if not match:
        sys.exit(f"error: version {version!r} is not MAJOR.MINOR.PATCH")

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

    manifests = plugin_manifests()
    previous = current_version(manifests)
    new = bump(previous, sys.argv[1])

    for manifest in manifests:
        rewrite_version(manifest, previous, new)

    print(f"{previous} -> {new}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as handle:
            handle.write(f"previous_version={previous}\n")
            handle.write(f"new_version={new}\n")


if __name__ == "__main__":
    main()
