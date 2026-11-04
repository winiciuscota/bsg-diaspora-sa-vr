#!/bin/bash
# Builds bsg-diaspora-sa-vr-<version>-x86_64.AppImage from the relocatable engine bundle (the output of pkg/PKGBUILD,
# /opt/fs2open-diaspora: fs2_open wrapper + fs2_open.bin + lib/ with its own glibc) and a sources.txt for that release.
# Usage: make-appimage.sh <engine-bundle-dir> <sources.txt> <icon.png> [out-dir]
set -euo pipefail
BUNDLE=${1:?engine bundle dir}; SOURCES=${2:?sources.txt}; ICON=${3:?icon png}; OUT=${4:-.}
HERE=$(cd "$(dirname "$0")" && pwd)
VERSION=$(sed -n 's/^# version //p' "$SOURCES")
[ -x "$BUNDLE/fs2_open" ] || { echo "$BUNDLE/fs2_open not found: is that the engine bundle?" >&2; exit 1; }

W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
A="$W/AppDir"
install -d "$A/usr/engine" "$A/usr/share/bsg-diaspora-sa-vr"
cp -a "$BUNDLE"/. "$A/usr/engine/"
install -m755 "$HERE/AppRun" "$A/AppRun"
install -m755 "$HERE/install-data" "$A/usr/share/bsg-diaspora-sa-vr/install-data"
install -m644 "$SOURCES" "$A/usr/share/bsg-diaspora-sa-vr/sources.txt"
install -m644 "$HERE/bsg-diaspora-sa-vr.desktop" "$A/bsg-diaspora-sa-vr.desktop"
install -m644 "$ICON" "$A/bsg-diaspora-sa-vr.png"

# appimagetool is not downloaded here: install it from your distribution or point APPIMAGETOOL at a copy you trust
TOOL=${APPIMAGETOOL:-$(command -v appimagetool || true)}
[ -n "$TOOL" ] || { echo "appimagetool not found: install it, or set APPIMAGETOOL=/path/to/appimagetool" >&2; exit 1; }
ARCH=x86_64 "$TOOL" --appimage-extract-and-run --no-appstream "$A" "$OUT/bsg-diaspora-sa-vr-$VERSION-x86_64.AppImage"
