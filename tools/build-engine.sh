#!/bin/bash
# Build the engine package on a remote Arch build host (the author's setup: an LXC running pm-build).
# Set BUILDER (ssh target) and BUILDER_DIR; for a local build see README.md ("Building the engine").
# Usage: tools/build-engine.sh [--no-bump]   (commit your engine changes in fs2open/ first)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE=${BUILDER:?set BUILDER=user@host of your build machine}
DIR=${BUILDER_DIR:-/var/lib/aur-builder/local/fs2open-diaspora}
SSH="/usr/bin/ssh -o StrictHostKeyChecking=accept-new"
export GIT_SSH_COMMAND=$SSH

git -C "$ROOT/fs2open" diff --quiet HEAD || { echo "fs2open/ has uncommitted changes - commit them first" >&2; exit 1; }
[ "$(git -C "$ROOT/fs2open" branch --show-current)" = diaspora ] || { echo "fs2open/ is not on branch diaspora" >&2; exit 1; }

if [ "${1:-}" != --no-bump ]; then
  PKG="$ROOT/pkg/fs2open-diaspora/PKGBUILD"
  rel=$(sed -n 's/^pkgrel=//p' "$PKG"); sed -i "s/^pkgrel=.*/pkgrel=$((rel + 1))/" "$PKG"
fi
git -C "$ROOT/fs2open" push -q --force "$REMOTE:$DIR/diaspora.git" diaspora:diaspora
/usr/bin/scp -o StrictHostKeyChecking=accept-new -q "$ROOT/pkg/fs2open-diaspora/PKGBUILD" "$REMOTE:$DIR/"
$SSH $REMOTE "chown -R 1000:1000 $DIR/diaspora.git $DIR/PKGBUILD"
J=$($SSH $REMOTE "pm-build submit build --force --local $DIR" 2>&1 | tail -1)
until $SSH $REMOTE "pm-build status 2>&1 | grep $J | grep -qE 'done|failed'"; do sleep 10; done
$SSH $REMOTE "pm-build status 2>&1 | grep $J | tail -1"
