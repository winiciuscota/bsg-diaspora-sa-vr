#!/usr/bin/env python3
"""Crack stars for the canopy glass (cockpit_glass.cpp): a 2x2 atlas of four impact cracks, drawn additively on black.
  gen_canopy_cracks.py out.png [--seed 3] [--size 2048]"""
import argparse
import numpy as np
import cv2


def crack(img, cx, cy, R, rng, S):
    # chip at the impact
    cv2.circle(img, (int(cx), int(cy)), int(R * 0.02), 1.0, -1, cv2.LINE_AA)

    def branch(x, y, ang, length, w, v, depth):
        px, py = x, y
        steps = max(int(length / (R * 0.035)), 3)
        for i in range(steps):
            ang += rng.normal(0, 0.14)
            qx, qy = px + np.cos(ang) * R * 0.035, py + np.sin(ang) * R * 0.035
            f = 1.0 - i / steps
            cv2.line(img, (int(px), int(py)), (int(qx), int(qy)), float(v * (0.3 + 0.7 * f)), max(int(round(w * (0.4 + 0.6 * f))), 1), cv2.LINE_AA)
            px, py = qx, qy
            if depth < 2 and rng.random() < 0.10:
                branch(px, py, ang + rng.choice([-1, 1]) * rng.uniform(0.35, 0.9), length * rng.uniform(0.2, 0.5) * f, max(w - 1, 1), v * 0.7, depth + 1)
    n = int(rng.integers(6, 11))
    base = rng.uniform(0, 2 * np.pi)
    for k in range(n):
        ang = base + 2 * np.pi * k / n + rng.normal(0, 0.18)
        branch(cx, cy, ang, R * rng.uniform(0.5, 0.95), 3 * S, rng.uniform(0.7, 1.0), 0)
    # the web: broken concentric arcs
    for ring in range(int(rng.integers(2, 5))):
        r = R * (0.12 + 0.17 * ring + rng.uniform(-0.02, 0.03)); a0 = rng.uniform(0, 2 * np.pi)
        pts = []
        for t in np.linspace(0, 2 * np.pi, 48):
            rr = r * (1 + rng.normal(0, 0.03))
            pts.append((cx + np.cos(a0 + t) * rr, cy + np.sin(a0 + t) * rr))
        for i in range(len(pts) - 1):
            if rng.random() < 0.7:
                cv2.line(img, (int(pts[i][0]), int(pts[i][1])), (int(pts[i + 1][0]), int(pts[i + 1][1])), float(rng.uniform(0.25, 0.55)), 1, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--seed", type=int, default=3); ap.add_argument("--size", type=int, default=2048)
    a = ap.parse_args(); rng = np.random.default_rng(a.seed)
    S = 3; N = a.size; cell = N // 2
    img = np.zeros((N * S, N * S), np.float32)
    for q in range(4):
        ox, oy = (q % 2) * cell * S, (q // 2) * cell * S
        crack(img[oy:oy + cell * S, ox:ox + cell * S], cell * S * 0.5 + rng.normal(0, cell * S * 0.03), cell * S * 0.5 + rng.normal(0, cell * S * 0.03), cell * S * 0.46, rng, S)
    img = cv2.resize(img, (N, N), interpolation=cv2.INTER_AREA)
    # fade at the cell edges so neighbouring cracks do not bleed into each other
    yy, xx = np.mgrid[0:N, 0:N]; lu = (xx % cell) / cell; lv = (yy % cell) / cell
    win = np.clip(np.minimum(np.minimum(lu, 1 - lu), np.minimum(lv, 1 - lv)) / 0.05, 0, 1)
    out = (np.clip(img, 0, 1) * win * 255).astype(np.uint8)
    cv2.imwrite(a.out, cv2.merge([out, out, out]))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
