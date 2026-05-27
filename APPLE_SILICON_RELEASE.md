# Apple Silicon Local Release Notes

This fork publishes an experimental Apple Silicon build for M-series Macs.

## Build

- Version: `24.11.0`
- Architecture: `arm64`
- macOS deployment target: `14.0`
- Qt: Homebrew Qt `6.11.1`
- Package: `klogg-24.11.0-arm64-local.dmg`
- SHA256: `cd30b260c07c11c3f46f1efaf9caa19745c3a981ad608ed340f85e015c00cf41`

## Changes

- Added Apple Silicon build instructions for native arm64 Qt 6 builds.
- Added a local DMG packaging flow using `macdeployqt`, bundled dependency path fixing, ad-hoc signing, and `hdiutil`.
- Added a bundle dependency check to prevent packaged apps from loading Homebrew Qt libraries at runtime.
- Fixed a startup crash caused by mixing Homebrew Qt frameworks with bundled Qt plugins in the packaged app.
- Patched vendored KArchive during CMake configuration so Qt 6.11 can compile `QIODevice::OpenMode` error messages.
- Explicitly ignored the return value from one `QFile::open` call to satisfy Qt 6.11 `nodiscard` annotations.
- Ignored the local `build_arm64/` build directory.

## Notes

The DMG is ad-hoc signed for local testing. It is not notarized with an Apple Developer ID.
If macOS blocks the app on first launch, open it with right-click > Open or allow it in System Settings.
