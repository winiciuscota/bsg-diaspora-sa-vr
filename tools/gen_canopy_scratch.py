#!/usr/bin/env python3
"""Canopy scratch map for the glass dome (fs2open/code/graphics/cockpit_glass.cpp), drawn additively on black.
u runs over azimuth -112.5..112.5, v over elevation 90..-6 degrees. Everything is high frequency (no soft blobs: the dome is drawn in
cells whose brightness differs, and a soft field would show the cell edges). What is in it:
  worn zones   a low-frequency wear field decides where scratches pile up (the rest of the glass stays nearly clean)
  bundles      groups of near-parallel scratches (cleaning swirls) around a wipe centre
  scratches    tapered, slightly curved, heavy-tailed brightness: a few deep bright ones, many faint hairlines
  long arcs    wiper-style sweeps
  chips        small bright impact stars with radial micro-cracks
  fibres       curly hairs, dust with a faint halo, and a fine grain
  gen_canopy_scratch.py out.png [--seed 7] [--w 4096]"""
import argparse
import numpy as np
import cv2

S = 4   # supersampling


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--seed", type=int, default=7); ap.add_argument("--w", type=int, default=4096)
    a = ap.parse_args(); rng = np.random.default_rng(a.seed)
    W = a.w; H = W * 96 // 225
    img = np.zeros((H * S, W * S), np.float32)
    HS, WS = H * S, W * S

    wear = cv2.resize(rng.random((7, 15)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    wear = np.clip((wear - 0.2) / 0.6, 0.0, 1.0) ** 1.4 * 0.8 + 0.2                  # 0.2 .. 1, patchy
    wear_s = cv2.resize(wear, (WS, HS), interpolation=cv2.INTER_LINEAR)
    cx, cy = WS * rng.uniform(0.35, 0.65), HS * 1.6                                          # wipe centre below the dome

    def pick():
        for _ in range(200):
            x, y = rng.uniform(0, WS), rng.uniform(0, HS)
            if rng.random() < wear_s[int(y), int(x)]:
                return x, y
        return x, y

    def bright(lo=0.0):
        return float(np.clip(lo + rng.lognormal(-1.5, 0.75), 0.04, 1.0))

    def stroke(x, y, th, L, curv, v, wd):
        """tapered polyline: thin and dim at the ends"""
        n = max(int(L / (4 * S)), 3); px, py, t = x, y, th
        for i in range(n):
            f = np.sin(np.pi * (i + 0.5) / n) ** 0.6
            qx, qy = px + np.cos(t) * 4 * S, py + np.sin(t) * 4 * S
            cv2.line(img, (int(px), int(py)), (int(qx), int(qy)), float(v * (0.25 + 0.75 * f)), max(int(round(wd * (0.4 + 0.6 * f))), 1), cv2.LINE_AA)
            px, py, t = qx, qy, t + curv * 4 * S

    def wipe_dir(x, y):
        return np.arctan2(y - cy, x - cx) + np.pi / 2

    for _ in range(3800):                                                                      # single scratches
        x, y = pick()
        th = wipe_dir(x, y) + rng.normal(0, 0.45) if rng.random() < 0.6 else rng.uniform(0, np.pi)
        stroke(x, y, th, rng.lognormal(np.log(16 * S), 0.7), rng.normal(0, 0.0004), bright(), int(rng.choice([1, 1, 2, 2, 3])))
    for _ in range(160):                                                                       # bundles of parallel scratches
        x, y = pick(); th = wipe_dir(x, y) + rng.normal(0, 0.25); L0 = rng.lognormal(np.log(60 * S), 0.5); curv = rng.normal(0, 0.0005)
        for _ in range(int(rng.integers(4, 22))):
            off = rng.normal(0, 7 * S); dx, dy = -np.sin(th) * off, np.cos(th) * off
            stroke(x + dx + rng.normal(0, 8 * S), y + dy, th + rng.normal(0, 0.02), L0 * rng.uniform(0.5, 1.2), curv, bright() * 0.8, int(rng.choice([1, 1, 2])))
    for _ in range(60):                                                                        # long wipe arcs
        x, y = rng.uniform(0, WS), rng.uniform(0, HS)
        stroke(x, y, wipe_dir(x, y) + rng.normal(0, 0.12), rng.uniform(140, 560) * S, rng.normal(0, 0.0005), rng.uniform(0.2, 0.55), 1)
    for _ in range(14):                                                                        # a few deep scratches
        x, y = pick(); stroke(x, y, wipe_dir(x, y) + rng.normal(0, 0.6), rng.uniform(60, 240) * S, rng.normal(0, 0.0006), rng.uniform(0.7, 1.0), 3)
    for _ in range(55):                                                                        # chips: impact stars
        x, y = pick(); r = rng.uniform(1.0, 3.0) * S
        cv2.circle(img, (int(x), int(y)), int(r), float(rng.uniform(0.3, 0.7)), -1, cv2.LINE_AA)
        for k in range(int(rng.integers(5, 11))):
            ang = rng.uniform(0, 2 * np.pi); ln = r * rng.uniform(2.5, 9)
            cv2.line(img, (int(x), int(y)), (int(x + np.cos(ang) * ln), int(y + np.sin(ang) * ln)), float(rng.uniform(0.25, 0.7)), 1, cv2.LINE_AA)
    for _ in range(70):                                                                        # curly fibres
        x, y = rng.uniform(0, WS), rng.uniform(0, HS); t = rng.uniform(0, 2 * np.pi); px, py = x, y
        for _ in range(int(rng.integers(12, 30))):
            t += rng.normal(0, 0.55); qx, qy = px + np.cos(t) * 3.5 * S, py + np.sin(t) * 3.5 * S
            cv2.line(img, (int(px), int(py)), (int(qx), int(qy)), 0.35, 1, cv2.LINE_AA); px, py = qx, qy
    for _ in range(2200):                                                                      # dust with a faint halo
        x, y = pick(); r = rng.choice([1, 1, 2, 2, 3, 5])
        cv2.circle(img, (int(x), int(y)), int(r * 2.6), float(rng.uniform(0.03, 0.08)), -1, cv2.LINE_AA)
        cv2.circle(img, (int(x), int(y)), int(r), float(rng.uniform(0.15, 0.6)), -1, cv2.LINE_AA)

    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    grain = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 1.1)             # fine grain, very faint
    grain = np.clip((grain - 0.5) * 6.0, 0, 1) * 0.045 * wear
    mod = 0.6 + 0.8 * cv2.resize(rng.random((6, 12)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img = np.clip(img * mod + grain, 0, 1)
    yy, xx = np.mgrid[0:H, 0:W]; u = xx / W; v = yy / H
    win = np.clip(np.minimum(np.minimum(u, 1 - u) / 0.04, np.minimum(v, 1 - v) / 0.06), 0, 1)   # fade at the dome rim
    out = (img * win * 255).astype(np.uint8)
    cv2.imwrite(a.out, cv2.merge([out, out, out]))
    print("wrote", a.out, W, H)


if __name__ == "__main__":
    main()
