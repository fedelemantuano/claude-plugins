#!/usr/bin/env python3
"""Validate the marketplace + plugin manifests before a release can ship.

Checks that both manifests parse, that every marketplace plugin source exists
and carries a manifest with a semver `version`, that all plugins share the
same version, that marketplace entries carry no `version` field (plugin.json
is the single source), and that the referenced skills/hooks directories are
present.
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


def validate_plugin(entry: dict, source: Path, versions: dict[Path, str]) -> None:
    manifest_path = source / ".claude-plugin" / "plugin.json"
    manifest = load(manifest_path)
    if manifest is None:
        return

    for field in ("name", "description", "version"):
        check(field in manifest, f"{manifest_path}: missing required field '{field}'")

    version = manifest.get("version", "")
    if check(
        bool(SEMVER.match(version)),
        f"{manifest_path}: version {version!r} is not MAJOR.MINOR.PATCH",
    ):
        versions[manifest_path] = version

    check(
        "version" not in entry,
        f"{MARKETPLACE}: entry {entry.get('name')!r} must not carry a 'version' "
        f"field — {manifest_path} is the single source",
    )

    for subdir in ("skills", "hooks"):
        check((source / subdir).is_dir(), f"{source / subdir}: missing directory")


def main() -> None:
    marketplace = load(MARKETPLACE)
    if marketplace is None:
        sys.exit("\n".join(errors))

    plugins = marketplace.get("plugins", [])
    check(bool(plugins), f"{MARKETPLACE}: no plugins listed")

    versions: dict[Path, str] = {}
    for entry in plugins:
        source = Path(entry["source"])
        if check(source.is_dir(), f"{MARKETPLACE}: source {source} does not exist"):
            validate_plugin(entry, source, versions)

    if len(set(versions.values())) > 1:
        details = ", ".join(f"{path}={version}" for path, version in versions.items())
        errors.append(f"plugin versions diverge — all plugins share one: {details}")

    if errors:
        sys.exit("\n".join(f"error: {error}" for error in errors))

    print(f"OK — {len(plugins)} plugin(s) validated")


if __name__ == "__main__":
    main()
