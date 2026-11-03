import sys, glob, os, time, torch, numpy as np
from PIL import Image
from spandrel import ModelLoader
dev = torch.device("cuda")
src, dst = sys.argv[1], sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else "RealESRGAN_x2plus"
SC = int(sys.argv[4]) if len(sys.argv) > 4 else 2
model = ModelLoader().load_from_file(os.path.join(os.environ.get("MODEL_DIR", "models"), "%s.pth" % name)).to(dev).eval()
os.makedirs(dst, exist_ok=True)
TILE, PAD = (384, 24) if SC == 2 else (256, 16)

def up_rgb(img):
    a = torch.from_numpy(np.asarray(img, dtype=np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0)
    _, _, H, W = a.shape
    out = torch.zeros(1, 3, H * SC, W * SC)
    for y in range(0, H, TILE):
        for x in range(0, W, TILE):
            y0, x0 = max(0, y - PAD), max(0, x - PAD)
            y1, x1 = min(H, y + TILE + PAD), min(W, x + TILE + PAD)
            with torch.no_grad():
                t = model(a[:, :, y0:y1, x0:x1].to(dev)).clamp(0, 1).cpu()
            oy, ox = (y - y0) * SC, (x - x0) * SC
            h, w = min(TILE, H - y) * SC, min(TILE, W - x) * SC
            out[:, :, y * SC:y * SC + h, x * SC:x * SC + w] = t[:, :, oy:oy + h, ox:ox + w]
    return Image.fromarray((out[0].permute(1, 2, 0).numpy() * 255.0 + 0.5).astype(np.uint8))

for f in sorted(glob.glob(src + "/*.png")):
    t0 = time.time()
    im = Image.open(f).convert("RGBA")
    rgb = up_rgb(im.convert("RGB"))
    alpha = im.getchannel("A").resize((im.width * SC, im.height * SC), Image.LANCZOS)
    rgb.putalpha(alpha)
    rgb.save(os.path.join(dst, os.path.basename(f)))
    print("%s %dx%d -> %dx%d %.1fs" % (os.path.basename(f), im.width, im.height, rgb.width, rgb.height, time.time() - t0), flush=True)
print("UPSCALE_DONE", flush=True)
