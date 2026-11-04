#!/bin/bash
# Builds bsg-diaspora-sa-vr-<version>-linux-x86_64.tar.zst: the relocatable engine bundle + launcher + first-start
# installer. Extract it anywhere and run ./bsg-diaspora-sa-vr (add --install-menu for application menu entries).
# Usage: make-tarball.sh <engine-bundle-dir> <sources.txt> <icon.png> [out-dir]
set -euo pipefail
BUNDLE=${1:?engine bundle dir}; SOURCES=${2:?sources.txt}; ICON=${3:?icon png}; OUT=${4:-.}
HERE=$(cd "$(dirname "$0")" && pwd)
VERSION=$(sed -n 's/^# version //p' "$SOURCES")
[ -x "$BUNDLE/fs2_open" ] || { echo "$BUNDLE/fs2_open not found: is that the engine bundle?" >&2; exit 1; }
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
N=bsg-diaspora-sa-vr; A="$W/$N"
install -d "$A/usr/engine" "$A/usr/share/$N"
cp -a "$BUNDLE"/. "$A/usr/engine/"
install -m755 "$HERE/AppRun" "$A/AppRun"
ln -s AppRun "$A/$N"
install -m755 "$HERE/install-data" "$A/usr/share/$N/install-data"
install -m644 "$SOURCES" "$A/usr/share/$N/sources.txt"
install -m644 "$HERE/$N.desktop" "$A/$N.desktop"
install -m644 "$ICON" "$A/$N.png"
tar -C "$W" --zstd -cf "$OUT/$N-$VERSION-linux-x86_64.tar.zst" "$N"
echo "$OUT/$N-$VERSION-linux-x86_64.tar.zst"
