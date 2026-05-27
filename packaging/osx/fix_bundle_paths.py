#!/usr/bin/env python3
"""Rewrite Homebrew install names in a deployed macOS app bundle."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


EXTERNAL_PREFIXES = ("/opt/homebrew/", "/usr/local/")
QT_FRAMEWORK_RE = re.compile(r".*/(Qt[^/]+)\.framework/Versions/[^/]+/\1$")


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, capture_output=True, text=True)


def is_macho(path: Path) -> bool:
    return "Mach-O" in run(["file", str(path)]).stdout


def dependencies(path: Path) -> list[str]:
    output = run(["otool", "-L", str(path)]).stdout
    return [
        line.strip().split(" ", 1)[0]
        for line in output.splitlines()[1:]
        if line.strip()
    ]


def rpaths(path: Path) -> list[str]:
    output = run(["otool", "-l", str(path)]).stdout
    paths: list[str] = []
    in_rpath = False
    for line in output.splitlines():
        stripped = line.strip()
        if stripped == "cmd LC_RPATH":
            in_rpath = True
            continue
        if in_rpath and stripped.startswith("path "):
            paths.append(stripped.split(" ", 2)[1])
            in_rpath = False
    return paths


def install_id(path: Path) -> str | None:
    output = run(["otool", "-D", str(path)]).stdout
    ids = [line.strip() for line in output.splitlines()[1:] if line.strip()]
    if not ids:
        return None
    return ids[0]


def iter_macho_files(app: Path):
    for path in app.rglob("*"):
        if path.is_file() and not path.is_symlink() and is_macho(path):
            yield path


def bundled_path(app: Path, dependency: str) -> str | None:
    framework_match = QT_FRAMEWORK_RE.match(dependency)
    if framework_match:
        qt_name = framework_match.group(1)
        local = app / "Contents" / "Frameworks" / f"{qt_name}.framework" / "Versions" / "A" / qt_name
        if local.exists():
            return f"@executable_path/../Frameworks/{qt_name}.framework/Versions/A/{qt_name}"

    basename = Path(dependency).name
    local = app / "Contents" / "Frameworks" / basename
    if local.exists():
        return f"@executable_path/../Frameworks/{basename}"

    return None


def bundled_id(app: Path, path: Path) -> str | None:
    frameworks = app / "Contents" / "Frameworks"
    try:
        relative = path.relative_to(frameworks)
    except ValueError:
        return None

    if any(part.endswith(".framework") for part in relative.parts):
        framework = next(part for part in relative.parts if part.endswith(".framework"))
        name = framework.removesuffix(".framework")
        if path.name == name:
            return f"@executable_path/../Frameworks/{framework}/Versions/A/{name}"
        return None

    if path.suffix == ".dylib":
        return f"@executable_path/../Frameworks/{path.name}"

    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    args = parser.parse_args()

    app = args.app.resolve()
    for path in iter_macho_files(app):
        for rpath in rpaths(path):
            if rpath.startswith(EXTERNAL_PREFIXES):
                subprocess.run(
                    ["install_name_tool", "-delete_rpath", rpath, str(path)],
                    check=True,
                )

        current_id = install_id(path)
        replacement_id = bundled_id(app, path)
        if current_id and replacement_id and current_id.startswith(EXTERNAL_PREFIXES):
            subprocess.run(
                ["install_name_tool", "-id", replacement_id, str(path)],
                check=True,
            )

        for dependency in dependencies(path):
            if not dependency.startswith(EXTERNAL_PREFIXES):
                continue
            replacement = bundled_path(app, dependency)
            if replacement is None:
                raise RuntimeError(f"No bundled copy for {dependency} referenced by {path}")
            subprocess.run(
                ["install_name_tool", "-change", dependency, replacement, str(path)],
                check=True,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
