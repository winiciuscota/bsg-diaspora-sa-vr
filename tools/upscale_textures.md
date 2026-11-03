# AI texture upscale (Theseus / Sobek battlestar + Viper Mk7/Mk7e and Raptor cockpits)

Result: `overlay/diaspora_fixes/data/maps/*.dds` (38 files, ~340 MB, gitignored: derived from the game's own art).

1. Extract the diffuse + glow maps from the VPs (`tools/vpx.py extract data/<vp> OUT Col_BS_Sobek` ... for Col_BS_Sobek,
   Col_Viper_Mk7_CP, Col_Viper_Mk7e_CP, Col_Raptor_CP; later VPs override earlier ones). Skipped: normal/shine maps,
   animated `_Scr` frames, uncompressed files (`Main-glow`, `Things`).
2. `magick FILE.dds[0] -alpha on in/NAME.png`
3. On CT 144 (RX 9070 XT) inside `yanwk/comfyui-boot:rocm` (torch + spandrel there):
   `python3 tools/upscale_textures.py in out` (Real-ESRGAN x2plus/x4plus .pth files in $MODEL_DIR, 384 px tiles,
   alpha resized with Lanczos). ~2 min for all 38.
4. Back to DDS with the ORIGINAL compression and a full mip chain:
   `magick out/NAME.png -define dds:compression=dxt1|dxt5 -define dds:mipmaps=<log2(max side)> overlay/.../maps/NAME.dds`
5. Copy to `~/Projects/Homelab/ansible/files/diaspora/diaspora_fixes/data/maps/` and deploy with `--tags overlay`.
To undo: delete `data/diaspora_fixes/data/maps` on Wolf (the original textures in the VPs take over again).

## Full run (2026-11-03)
`tools/upscale_all.py WORKDIR` batches everything: 214 maps (2.3 GB, 233 files with the first 38+Sobek set). Cockpit maps (`_CP`)
use RealESRGAN_x4plus (2048 -> 8192), the rest x2plus. Skipped: normal/shine maps, animated `_NNNN` frames, `_Scr`,
uncompressed DDS, textures over 2048 or under 128 px. ~75 min, the GPU was only 7-15% busy (CPU-side tile copies, fp32,
single-threaded PIL); a faster version would keep tiles on the GPU, use fp16 and bigger tiles.
