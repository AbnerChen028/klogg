#!/usr/bin/env python3
"""Check that a macOS app bundle does not depend on Homebrew libraries."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


EXTERNAL_PREFIXES = ("/opt/homebrew/", "/usr/local/")


def is_macho(path: Path) -> bool:
    result = subprocess.run(
        ["file", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return "Mach-O" in result.stdout


def dependencies(path: Path) -> list[str]:
    result = subprocess.run(
        ["otool", "-L", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        line.strip().split(" ", 1)[0]
        for line in result.stdout.splitlines()[1:]
        if line.strip()
    ]


def rpaths(path: Path) -> list[str]:
    result = subprocess.run(
        ["otool", "-l", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[str] = []
    in_rpath = False
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped == "cmd LC_RPATH":
            in_rpath = True
            continue
        if in_rpath and stripped.startswith("path "):
            paths.append(stripped.split(" ", 2)[1])
            in_rpath = False
    return paths


def iter_files(app: Path):
    for path in app.rglob("*"):
        if path.is_file() and not path.is_symlink():
            yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    args = parser.parse_args()

    offenders: list[tuple[Path, str]] = []
    for path in iter_files(args.app):
        if not is_macho(path):
            continue
        for rpath in rpaths(path):
            if rpath.startswith(EXTERNAL_PREFIXES):
                offenders.append((path, rpath))
        for dependency in dependencies(path):
            if dependency.startswith(EXTERNAL_PREFIXES):
                offenders.append((path, dependency))

    if offenders:
        for path, dependency in offenders:
            print(f"{path}: {dependency}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
