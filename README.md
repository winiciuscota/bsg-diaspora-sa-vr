# Diaspora VR — Battlestar Galactica: Diaspora on modern FreeSpace Open, in VR

A port of [Diaspora](https://www.hard-light.net/forums/index.php?board=211.0) (Hard Light Productions' Battlestar Galactica
total conversion) to a current FreeSpace 2 Open engine with a **Vulkan renderer and native OpenXR VR**, plus new
missions, HUD fixes and optional HD texture / voice packs.

The engine changes live in a separate fork: **[winiciuscota/fs2open-diaspora-vr](https://github.com/winiciuscota/fs2open-diaspora-vr)**
(branch `diaspora`). This repository holds the mod files, tools and notes.

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
- 14 extra missions in the *Thunderlords Patrol Log* campaign (also in the Mission Simulator): Vigil, Tylium Run, Hollow
  Rock, Iron Shepherd, Station Keeping, Dead Reckoning, Deep Look (Raptor), Firebreak, Hunter's Moon, Hammer and Anvil,
  Picket Line, Long Tow, Ghost Light, and Fleet Anchorage (a peaceful free flight to test your controls).
- HUD layout tweaks for VR (smaller ship outline, stores and target box placement).
- Saitek X52 default bindings.

**Release downloads** (see [Releases](https://github.com/winiciuscota/diaspora-vr-port/releases))
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

## Installing by hand

1. Install Diaspora R1 and its patches as usual.
2. Copy `mod/diaspora_fixes` into the Diaspora folder (next to the `.vp` files).
3. Optional: unzip the HD texture and voice packs from the release into the same folder (they add
   `diaspora_fixes/data/maps` and `diaspora_fixes/data/voice`).
4. Run the engine from the Diaspora folder: `fs2_open -mod diaspora_fixes` for flat screen, or
   `fs2_open -mod diaspora_fixes -vr -vulkan -res 2000x2100 -no_unfocused_pause` for VR with an OpenXR runtime active.
   `tools/launch-example.sh` is the launcher the author uses (resolution handling, X52 selection, VR runtime).

## VR settings

Environment variables (put them in `vr.env` next to `launch-example.sh`, one `VAR=value` per line):

| Variable | Default | What it does |
|---|---|---|
| `DIASPORA_VR_RES` | 1600x1800 | Window / render size in VR |
| `FSO_VR_HUD_DISTANCE`, `FSO_VR_HUD_ZOOM` | 10, 0.9 | HUD layer distance (m) and size |
| `FSO_VR_HUD_STORES_DX/DY`, `FSO_VR_HUD_LEFT_DX/DY` | 0/-150, 60/-150 | Move the lower-right / lower-left gauge groups (1024-wide HUD units) |
| `FSO_VR_HUD_SHIP_DX`, `FSO_VR_HUD_WEAPONS_DX` | 0, 25 | Nudge the ship outline / the weapon stores text |
| `FSO_VR_HUD_HEIGHT` | 1 | <1 squeezes the HUD panels vertically towards the middle |
| `FSO_VR_SUNGLARE` | 0.3 | Sun glare strength in VR |
| `FSO_VR_SHAFTS` | 0 | 1 turns light shafts back on in VR |
| `FSO_VR_SHAKE`, `FSO_VR_FLASH` | off, 0.35 | View shake, flash strength |
| `FSO_VR_PADLOCK`, `FSO_VR_GAZE_TARGET` | on | Hat-switch targeting, head-gaze targeting |
| `FSO_VR_MENU_SCALE`, `FSO_VR_EYE_FORWARD` | 1.35, 0.2 | Menu quad scale, eye offset into the cockpit (m) |
| `FSO_VR_HUD_HIDE`, `FSO_VR_HUD_SKIP` | — | Debugging: hide the HUD layer / skip HUD gauge types (comma list) |

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
