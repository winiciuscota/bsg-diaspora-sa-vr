#!/bin/bash
# Writes sources.txt (sha256, local name, url) for a release: the files published at
# https://github.com/winiciuscota/bsg-diaspora-sa-vr/releases/tag/v<version> plus the original Diaspora downloads.
# Usage: make-sources.sh <version> <folder with the release files and the three Diaspora archives>
set -euo pipefail
V=${1:?version}; D=${2:?folder}
REL="https://github.com/winiciuscota/bsg-diaspora-sa-vr/releases/download/v$V"
DIA=http://diaspora.fs2downloads.com
echo "# version $V"
line() { printf '%s %s %s\n' "$(sha256sum "$D/$1" | cut -d' ' -f1)" "$2" "$3"; }
line "diaspora-vr-mod-$V.tar.gz" diaspora-vr-mod.tar.gz "$REL/diaspora-vr-mod-$V.tar.gz"
for z in diaspora-vr-hd-textures-2x.zip diaspora-vr-hd-cockpits-4x.zip diaspora-vr-voices.zip; do line "$z" "$z" "$REL/$z"; done
for f in Diaspora_R1_Linux Diaspora_R1_Patch_1.1 Diaspora_R1_Patch_1.1.1; do line "$f.tar.lzma" "$f.tar.lzma" "$DIA/$f.tar.lzma"; done
