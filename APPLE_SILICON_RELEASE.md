# Apple Silicon Local Release Notes

This fork publishes an experimental Apple Silicon build for M-series Macs.

## Build

- Version: `24.11.0`
- Architecture: `arm64`
- macOS deployment target: `14.0`
- Qt: Homebrew Qt `6.11.1`
- Package: `klogg-24.11.0-arm64-local.dmg`
- SHA256: `baff3d338a1750a5fe2fc194b2a4ffb817b8873ae7bd112dd9dfe94dd9d65292`

## Changes

- Added Apple Silicon build instructions for native arm64 Qt 6 builds.
- Added a local DMG packaging flow using `macdeployqt`, bundled dependency path fixing, ad-hoc signing, and `hdiutil`.
- Added a bundle dependency check to prevent packaged apps from loading Homebrew Qt libraries at runtime.
- Fixed a startup crash caused by mixing Homebrew Qt frameworks with bundled Qt plugins in the packaged app.
- Replaced the app icon with a modern log-viewer design across macOS, Windows, and bundled hicolor assets.
- Patched vendored KArchive during CMake configuration so Qt 6.11 can compile `QIODevice::OpenMode` error messages.
- Explicitly ignored the return value from one `QFile::open` call to satisfy Qt 6.11 `nodiscard` annotations.
- Ignored the local `build_arm64/` build directory.

## Notes

The DMG is ad-hoc signed for local testing. It is not notarized with an Apple Developer ID.
If macOS blocks the app on first launch, open it with right-click > Open or allow it in System Settings.
