#!/bin/bash
# Launcher for the "Diaspora (FSO)" non-Steam shortcut (see startup-app-steam.sh).
# Layout (library: /mnt/steam-library/GameLibrary/Diaspora):
#   engine/   fs2open bundle from the aur-builder package `fs2open-diaspora` (/opt/fs2open-diaspora)
#   data/     Diaspora R1 VP archives (the FSO "root" folder, working directory of the engine)
#   logs/     one log per launch (engine stdout/stderr + exit code)
# The stream resolution is whatever Moonlight asked for, so the engine is started borderless at the
# X display's size (override with DIASPORA_RES=WxH).
D="$(cd "$(dirname "$0")" && pwd)"
# Optional per-install overrides (e.g. FSO_VR_HUD_ZOOM=1.1, FSO_VR_HUD_DISTANCE=10, DIASPORA_VR_RES=2000x2096), one VAR=value per line
[ -f "$D/vr.env" ] && { set -a; . "$D/vr.env"; set +a; }
mkdir -p "$D/logs"
LOG="$D/logs/launch-$(date +%Y%m%d-%H%M%S).log"

screen_res() {
  python3 - <<'PY' 2>/dev/null
import ctypes, ctypes.util
x = ctypes.CDLL(ctypes.util.find_library("X11") or "libX11.so.6")
x.XOpenDisplay.restype = ctypes.c_void_p
x.XDisplayWidth.argtypes = x.XDisplayHeight.argtypes = [ctypes.c_void_p, ctypes.c_int]
d = x.XOpenDisplay(None)
if d:
    print(f"{x.XDisplayWidth(d, 0)}x{x.XDisplayHeight(d, 0)}")
PY
}
RES="${DIASPORA_RES:-$(screen_res)}"
ARGS=()
case " $* " in
  *" -vr "*)
    # The engine shrinks the window width to the headset's aspect; below 1024 px it falls back to
    # low-res menu art that Diaspora doesn't ship, so ask for a tall window. 1600x1800 (rendered 1718x1800) gave a good stream; WiVRn encodes each eye at about half the headset size anyway, so rendering at the full 2476x2594 most likely only cost GPU time (the stream got worse after that change). Keep running unfocused.
    ARGS+=(-res "${DIASPORA_VR_RES:-1600x1800}" -no_unfocused_pause)
    # Native OpenXR needs a runtime: use SteamVR's (Steam Link / Quest) unless one is already chosen.
    if [ -z "${XR_RUNTIME_JSON:-}" ] && [ ! -e "$HOME/.config/openxr/1/active_runtime.json" ] &&
       [ -f "$HOME/.steam/steam/steamapps/common/SteamVR/steamxr_linux64.json" ]; then
      export XR_RUNTIME_JSON="$HOME/.steam/steam/steamapps/common/SteamVR/steamxr_linux64.json"
    fi
    # Touch a file named xr-debug next to launch.sh to log the VR controller state (FSO_XR_INPUT_DEBUG).
    [ -e "$D/xr-debug" ] && export FSO_XR_INPUT_DEBUG=1
    # The Vulkan backend gives a correctly lit VR picture on Monado (OpenGL looked dark); DIASPORA_VR_RENDERER=opengl opts out.
    [ "${DIASPORA_VR_RENDERER:-vulkan}" = vulkan ] && ARGS+=(-vulkan) ;;
  *) [ -n "$RES" ] && ARGS+=(-res "$RES" -fullscreen_window)
     # Ultrawide stream: keep the HUD and menus in a 16:9 centre region (override with DIASPORA_CENTER_RES=WxH,
     # DIASPORA_STRETCH_MENU=0 keeps the 4:3 menus unstretched).
     W=${RES%x*}; H=${RES#*x}
     if [ -n "${DIASPORA_CENTER_RES:-}" ]; then
       ARGS+=(-center_res "$DIASPORA_CENTER_RES")
     elif [ -n "$W" ] && [ -n "$H" ] && [ $((W * 9)) -gt $((H * 16 * 21 / 20)) ]; then
       ARGS+=(-center_res "$((H * 16 / 9 / 2 * 2))x$H")
     fi
     if [ "${DIASPORA_STRETCH_MENU:-1}" != 0 ] && [[ " ${ARGS[*]} " == *" -center_res "* ]]; then
       ARGS+=(-stretch_menu)
     fi ;;
esac

[ -d "$D/data/diaspora_fixes" ] && ARGS+=(-mod diaspora_fixes)
# First run: select the Saitek X52 as joystick 0 (the engine does not pick a stick by itself; GUID is
# SDL's for vendor 06a3 / product 075c). Per-mod settings file, only seeded when it does not exist yet.
SETTINGS="$HOME/.local/share/HardLightProductions/FreeSpaceOpen/data/diaspora_fixes_settings.ini"
if [ ! -s "$SETTINGS" ] && [ -d "$D/data/diaspora_fixes" ] && ls /dev/input/by-id/*X52*joystick >/dev/null 2>&1; then
  mkdir -p "$(dirname "$SETTINGS")"
  printf '[Input]\nJoystick={"guid":"0300EA18A30600005C07000011010000","id":-1}\n' > "$SETTINGS"
fi

# Share one OpenGL shader cache between all tiles/profiles (same GPU and driver), so a profile that never ran the
# game starts with the shaders already compiled. Existing per-profile caches are merged in, the old dir is kept.
SHARED_CACHE="$D/shader-cache"
mkdir -p "$SHARED_CACHE"
for sub in data diaspora_fixes/data; do
  CACHE="$HOME/.local/share/HardLightProductions/FreeSpaceOpen/$sub/cache"
  if [ -d "$CACHE" ] && [ ! -L "$CACHE" ]; then
    cp -n "$CACHE"/* "$SHARED_CACHE"/ 2>/dev/null
    mv "$CACHE" "$CACHE.local-$(date +%Y%m%d)"
  fi
  if [ ! -e "$CACHE" ]; then
    mkdir -p "$(dirname "$CACHE")"
    ln -s "$SHARED_CACHE" "$CACHE"
  fi
done

cd "$D/data" || exit 1
{ echo "res: ${RES:-unknown}"; echo "args: ${ARGS[*]} $*"; } > "$LOG"
"$D/engine/fs2_open" "${ARGS[@]}" "$@" >> "$LOG" 2>&1
rc=$?
echo "engine exit code: $rc" >> "$LOG"
exit $rc
