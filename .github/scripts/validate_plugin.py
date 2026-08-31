#!/usr/bin/env python3
"""Validate the marketplace + plugin manifests before a release can ship.

Checks that both manifests parse, that every marketplace plugin source exists
and carries a manifest with a semver `version`, that the marketplace entry
version matches the plugin manifest, and that the referenced skills/hooks
directories are present.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

errors: list[str] = []


def check(condition: bool, message: str) -> bool:
    if not condition:
        errors.append(message)
    return condition


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        errors.append(f"{path}: missing")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON — {exc}")
    return None


def validate_plugin(entry: dict, source: Path) -> None:
    manifest_path = source / ".claude-plugin" / "plugin.json"
    manifest = load(manifest_path)
    if manifest is None:
        return

    for field in ("name", "description", "version"):
        check(field in manifest, f"{manifest_path}: missing required field '{field}'")

    version = manifest.get("version", "")
    check(
        bool(SEMVER.match(version)),
        f"{manifest_path}: version {version!r} is not MAJOR.MINOR.PATCH",
    )

    marketplace_version = entry.get("version", "")
    check(
        marketplace_version == version,
        f"{MARKETPLACE}: version {marketplace_version!r} for "
        f"{entry.get('name')!r} does not match {manifest_path} ({version!r})",
    )

    for subdir in ("skills", "hooks"):
        check((source / subdir).is_dir(), f"{source / subdir}: missing directory")


def main() -> None:
    marketplace = load(MARKETPLACE)
    if marketplace is None:
        sys.exit("\n".join(errors))

    plugins = marketplace.get("plugins", [])
    check(bool(plugins), f"{MARKETPLACE}: no plugins listed")

    for entry in plugins:
        source = Path(entry["source"])
        if check(source.is_dir(), f"{MARKETPLACE}: source {source} does not exist"):
            validate_plugin(entry, source)

    if errors:
        sys.exit("\n".join(f"error: {error}" for error in errors))

    print(f"OK — {len(plugins)} plugin(s) validated")


if __name__ == "__main__":
    main()
