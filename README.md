# Diaspora VR — Battlestar Galactica: Diaspora on modern FreeSpace Open, in VR

A port of [Diaspora](https://www.hard-light.net/forums/index.php?board=211.0) (Hard Light Productions' Battlestar Galactica
total conversion) to a current FreeSpace 2 Open engine with a **Vulkan renderer and native OpenXR VR**, plus new
missions, HUD fixes and optional HD texture / voice packs.

The engine changes live in a separate fork: **[winiciuscota/fs2open-diaspora-vr](https://github.com/winiciuscota/fs2open-diaspora-vr)**
(branch `diaspora`). This repository holds the mod files, tools and notes.

[![Gameplay video](https://img.youtube.com/vi/1w9ybdsAaO0/maxresdefault.jpg)](https://www.youtube.com/watch?v=1w9ybdsAaO0)

*Watch it in action: https://www.youtube.com/watch?v=1w9ybdsAaO0*

> You need your own copy of **Diaspora R1 (with the 1.1 / 1.1.1 patches)**. Nothing here replaces it.

## What's in it

**Engine (fork)**
- OpenXR VR on the Vulkan renderer (tested with WiVRn + Quest 3, and Monado).
- The HUD is an OpenXR quad layer fixed in the cockpit (ported from SgtBilko76's FreeSpace2-VR idea), lower gauges lifted
  out of the cockpit panel, menus on a scaled quad with a controller laser pointer.
- VR comfort: no view shake, softer flashes and sun glare, look-to-target with head gaze, hat-switch padlock targeting.
- Mission Simulator reachable from the Campaign Room (S), death popup on the fixed HUD layer.
- Vulkan fix: the immediate vertex buffer is no longer reset between the two eyes of a stereo frame (that corrupted the
  HUD with long green streaks, worst with the sun in view).

**Mod (`mod/diaspora_fixes`)**
- 19 extra missions in the *Thunderlords Patrol Log* campaign (also in the Mission Simulator, which shows the estimated
  duration and difficulty of each): Vigil, Tylium Run, Hollow Rock, Iron Shepherd, Station Keeping, Dead Reckoning, Deep
  Look (Raptor), Firebreak, Hunter's Moon, Hammer and Anvil, Picket Line, Long Tow, Ghost Light, **five long missions of
  25 to 30 minutes** (The Long Watch, Cold Convoy, Dead Hulks, Hammerfall, Last Stand at Armistice), and Fleet Anchorage
  (a peaceful free flight to test your controls).
- HUD layout tweaks for VR (smaller ship outline, stores and target box placement).
- Saitek X52 default bindings.

**Release downloads** (see [Releases](https://github.com/winiciuscota/bsg-diaspora-sa-vr/releases))
- **HD textures**: Real-ESRGAN upscales of the ship, weapon and cockpit textures (cockpits 4x, everything else 2x).
  Derived from Diaspora's own art; `tools/upscale_all.py` regenerates them.
- **Voices for the extra missions**: AI-generated with F5-TTS zero-shot cloning **from the original Diaspora voice
  acting**, plus a radio filter. All credit for the voices belongs to the Diaspora voice cast. If you are one of the actors
  and want your voice removed, open an issue and it will be taken down.
- An Arch Linux engine package built from the fork.

## Install on Arch Linux (one command)

```sh
yay -S bsg-diaspora-sa-vr        # or paru, or: git clone https://aur.archlinux.org/bsg-diaspora-sa-vr.git && cd bsg-diaspora-sa-vr && makepkg -si
```

This downloads Diaspora R1 and its patches, builds the engine, adds the mod, HD textures and voices, and installs a
launcher and menu entries ("Battlestar Galactica: Diaspora" and "... (VR)"). It needs about 25 GB of free disk during the
build (5 GB installed) and takes 10 to 30 minutes depending on your CPU. Run `bsg-diaspora-sa-vr` for a window
(`DIASPORA_RES=1920x1080`, `DIASPORA_FULLSCREEN=1` to change it) or `bsg-diaspora-sa-vr --vr` with an OpenXR runtime
active. Tested on a clean Arch + KDE Plasma (Wayland) install.

## Install on any other Linux distribution

Download `bsg-diaspora-sa-vr-<version>-linux-x86_64.tar.zst` from the releases, extract it anywhere and run it:

```sh
tar --zstd -xf bsg-diaspora-sa-vr-*-linux-x86_64.tar.zst && cd bsg-diaspora-sa-vr
./bsg-diaspora-sa-vr --install-menu   # optional: adds the menu entries (flat screen and VR)
./bsg-diaspora-sa-vr                  # first start downloads Diaspora R1, the patches and the mod (about 4 GB)
./bsg-diaspora-sa-vr --vr             # VR with the active OpenXR runtime
```

The engine ships with its own C library, so it runs on distributions with an older glibc; the graphics stack (Mesa or the
NVIDIA driver, the Vulkan loader) comes from your system. The first start needs `curl`, `tar`, `xz`, `sha256sum` and one of
`unzip` / `bsdtar` / `python3`, and about 9 GB of free disk while it installs. The game goes to
`~/.local/share/bsg-diaspora-sa-vr` (`BSG_DIASPORA_DATA` moves it). `pkg/generic/` holds the scripts that build the tarball
(`make-tarball.sh`) and an AppImage (`make-appimage.sh`, needs `appimagetool`).

## Installing by hand

1. Install Diaspora R1 and its patches as usual.
2. Copy `mod/diaspora_fixes` into the Diaspora folder (next to the `.vp` files).
3. Optional: unzip the HD texture and voice packs from the release into the same folder (they add
   `diaspora_fixes/data/maps` and `diaspora_fixes/data/voice`).
4. Run the engine from the Diaspora folder: `fs2_open -mod diaspora_fixes` for flat screen, or
   `fs2_open -mod diaspora_fixes -vr -vulkan -res 2000x2100 -no_unfocused_pause` for VR with an OpenXR runtime active.
   `tools/launch-example.sh` is the launcher the author uses (resolution handling, X52 selection, VR runtime).

## VR settings

Press **F9** in the main hall or in the Options screen for the in-game VR settings: a **graphics preset**, the **render
scale**, HUD distance, size, height and placement, menu size, flash and glare strength, sun light shafts, camera shake,
padlock and look-to-target. The preset and the render scale apply at the next start.

- **Graphics preset**: *Low* (no shadows, no anti-aliasing, no bloom), *Default* (the engine's own settings, what you set in
  the Options screen), *High* (SMAA, bloom, soft particles) and *Ultra* (High plus shadow maps and cockpit lighting). Ray-traced
  shadows are never used by a preset. A preset overrides the matching options while it is active; pick *Default* to hand them
  back to the Options screen.
- **Render scale** (0.5 to 1.5): multiplies the VR render resolution (`DIASPORA_VR_RES`). Lower it if your GPU can't keep up,
  raise it for a sharper picture. Changes are saved in
`diaspora_vr_settings.ini` in your profile data folder. The same options can be forced with environment variables
(put them in `vr.env` next to `launch-example.sh`, one `VAR=value` per line); what you save in the menu wins:

Environment variables (put them in `vr.env` next to `launch-example.sh`, one `VAR=value` per line):

| Variable | Default | What it does |
|---|---|---|
| `DIASPORA_VR_RES` | 1600x1800 | Window / render size in VR (the render scale of the F9 screen multiplies it) |
| `FSO_VR_GFX_PRESET`, `FSO_VR_RENDER_SCALE` | 1 (Default), 1.0 | Graphics preset (0 Low, 1 Default, 2 High, 3 Ultra) and render scale; apply at start |
| `FSO_VR_HUD_DISTANCE`, `FSO_VR_HUD_ZOOM` | 10, 0.9 | HUD layer distance (m) and size |
| `FSO_VR_HUD_STORES_DX/DY`, `FSO_VR_HUD_LEFT_DX/DY` | 0/-150, 60/-150 | Move the lower-right / lower-left gauge groups (1024-wide HUD units) |
| `FSO_VR_HUD_SHIP_DX`, `FSO_VR_HUD_WEAPONS_DX` | 0, 25 | Nudge the ship outline / the weapon stores text |
| `FSO_VR_HUD_HEIGHT` | 1 | <1 squeezes the HUD panels vertically towards the middle |
| `FSO_VR_SUNGLARE` | 0.3 | Sun glare strength in VR |
| `FSO_VR_SHAFTS` | 0 | 1 turns light shafts back on in VR |
| `FSO_VR_SHAKE`, `FSO_VR_FLASH` | off, 0.35 | View shake, flash strength |
| `FSO_VR_PADLOCK`, `FSO_VR_GAZE_TARGET` | on | Hat-switch targeting, head-gaze targeting |
| `FSO_VR_MENU_SCALE`, `FSO_VR_EYE_FORWARD` | 1.35, 0.2 | Menu quad scale, eye offset into the cockpit (m) |

## Building the engine

```sh
git clone -b diaspora https://github.com/winiciuscota/fs2open-diaspora-vr.git fs2open
cmake -S fs2open -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFSO_BUILD_WITH_OPENXR=ON -DFSO_BUILD_WITH_VULKAN=ON
cmake --build build -j 16
```

`pkg/PKGBUILD` is the Arch package recipe (relocatable bundle in `/opt/fs2open-diaspora`, used inside containers with an
older glibc). `tools/build-engine.sh` is the author's remote-build helper (set `BUILDER`).

## Tools

| Tool | Purpose |
|---|---|
| `tools/fsmission.py`, `tools/make_extra_missions.py` | Mission generator (writes the `XM-*.fs2` missions and the campaign) |
| `tools/check_missions.py` | Static mission check: SEXP operators/arity, names, ship classes |
| `tools/make_voices.py` | Voice job preparation and radio post-processing (synthesis runs F5-TTS on a GPU) |
| `tools/upscale_textures.py`, `tools/upscale_all.py`, `tools/upscale_textures.md` | Real-ESRGAN texture upscale pipeline |
| `tools/vpx.py` | VP archive lister/extractor |

## Credits

- **Diaspora**: the Diaspora team at Hard Light Productions (ships, art, tables, music and the voice cast).
- **FreeSpace 2 Open**: the Source Code Project ([scp-fs2open](https://github.com/scp-fs2open/fs2open.github.com)).
- VR HUD layer approach after **SgtBilko76/FreeSpace2-VR**.
- Battlestar Galactica is © NBCUniversal; this is a non-commercial fan project.

Port and new content by Winícius Cota, built with Claude.
