#!/usr/bin/env python3
"""Batch driver: upscale the game's colour/glow maps on the GPU container and write DXT DDS files into the overlay.
usage: upscale_all.py WORKDIR   (needs WORKDIR/raw = extracted data/maps, list.tsv = path name w h fmt; see upscale_textures.md)
Cockpit maps (_CP) go through RealESRGAN_x4plus (4x), everything else x2plus (2x)."""
import math, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
W = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mod', 'diaspora_fixes', 'data', 'maps')
# GPU host reached over ssh + 'pct exec <CT>' (the author's Proxmox container); set GPU_SSH and GPU_CT
PX = ['ssh', '-o', 'ConnectTimeout=10', os.environ.get('GPU_SSH', 'root@gpu-host')]
CT = os.environ.get('GPU_CT', '144')
MODELS = os.environ.get('GPU_MODEL_DIR', '/opt/models/upscale')
LOG = open(W + '/log.txt', 'a')
def log(*a):
    print(time.strftime('%H:%M:%S'), *a, file=LOG, flush=True)
def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)
def sh144(script):
    return subprocess.run(PX + ['pct exec %s -- ' % CT + 'bash -c ' + "'" + script.replace("'", "'\\''") + "'"], capture_output=True, text=True)

rows = [l.rstrip('\n').split('\t') for l in open(W + '/list.tsv') if l.strip()]
cock = [r for r in rows if re.search(r'_CP', r[1], re.I)]
rest = [r for r in rows if r not in cock]
os.makedirs(OUT, exist_ok=True)
os.makedirs(W + '/in', exist_ok=True)

def batch(items, model, sc):
    for d in ('in', 'out'):
        shutil.rmtree(W + '/' + d, ignore_errors=True); os.makedirs(W + '/' + d)
    def topng(r):
        run(['magick', r[0] + '[0]', '-alpha', 'on', '%s/in/%s.png' % (W, r[1])])
    with ThreadPoolExecutor(6) as ex: list(ex.map(topng, items))
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upscale_textures.py'), W + '/in/../upscale.py')
    sh144('rm -rf /opt/tex && mkdir -p /opt/tex/out')
    tar = subprocess.Popen(['tar', 'c', '-C', W, 'in', 'upscale.py'], stdout=subprocess.PIPE)
    run(PX + ['pct exec %s -- ' % CT + 'tar x -C /opt/tex'], stdin=tar.stdout); tar.wait()
    r = sh144('docker rm -f tex-up >/dev/null 2>&1; docker run --rm --name tex-up --memory 16g --device /dev/kfd --device /dev/dri --group-add video '
              '--security-opt seccomp=unconfined -v /opt/tex:/tex -v ' + MODELS + ':/models:ro -e MODEL_DIR=/models --entrypoint bash '
              'yanwk/comfyui-boot:rocm -c "python3 /tex/upscale.py /tex/in /tex/out %s %d" 2>&1 | tail -3' % (model, sc))
    if 'UPSCALE_DONE' not in r.stdout:
        raise RuntimeError('upscale failed: ' + r.stdout[-300:] + r.stderr[-200:])
    pull = subprocess.Popen(PX + ['pct exec %s -- ' % CT + 'tar c -C /opt/tex out'], stdout=subprocess.PIPE)
    run(['tar', 'x', '-C', W], stdin=pull.stdout); pull.wait()
    def todds(r):
        n, w, h, fmt = r[1], int(r[2]) * sc, int(r[3]) * sc, r[4]
        run(['magick', '%s/out/%s.png' % (W, n), '-define', 'dds:compression=' + fmt,
             '-define', 'dds:mipmaps=%d' % int(math.log2(max(w, h))), '%s/%s.dds' % (OUT, n)])
    with ThreadPoolExecutor(6) as ex: list(ex.map(todds, items))

for name, items, model, sc, size in (('cockpits x4', cock, 'RealESRGAN_x4plus', 4, 8), ('everything else x2', rest, 'RealESRGAN_x2plus', 2, 40)):
    log('phase', name, len(items), 'textures')
    for i in range(0, len(items), size):
        t0 = time.time()
        batch(items[i:i + size], model, sc)
        log('  %s: %d/%d done (%.0fs)' % (name, min(i + size, len(items)), len(items), time.time() - t0))
log('ALL_DONE')
