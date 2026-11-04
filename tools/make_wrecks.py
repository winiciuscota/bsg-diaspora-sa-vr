#!/usr/bin/env python3
"""Turns the wreck meshes generated in the assetgen queue into game models.

For every entry of WRECKS: decimate the job's mesh inside the assetgen-queue container (trimesh + quadric decimation),
fetch it as OBJ, convert it with mesh2pof.py, and write the modular ship table (wrecks-shp.tbm) plus the hull textures into
the overlay. The mission generator uses the ship classes below.

usage: make_wrecks.py            (needs ssh access to the Proxmox host; see PROXMOX / CT)
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "overlay", "diaspora_fixes", "data")
PROXMOX, CT = "root@proxmox.lan", "140"

# key: assetgen 3D job id, ship class name, short name, length in metres, polygons, texture repeat in metres
WRECKS = {
    "wreck_battlestar": dict(job="job-1793768605526", cls="Wreck Battlestar", short="Wreck_BS", length=760.0, faces=7000, tile=45.0),
    "wreck_hauler":     dict(job="job-1793768620742", cls="Wreck Hauler",     short="Wreck_Haul", length=240.0, faces=5000, tile=18.0),
    "wreck_station":    dict(job="job-1793768666744", cls="Wreck Station",    short="Wreck_Stn", length=320.0, faces=6000, tile=24.0),
    "hull_plate":       dict(job="job-1793768655379", cls="Hull Plate",       short="Hull_Plate", length=70.0, faces=1800, tile=9.0),
}

TBM_HEAD = "#Ship Classes\n\n"
TBM_SHIP = """$Name:\t\t\t\t\t{cls}
$Short name:\t\t\t\t{short}
$Species:\t\t\t\tCivilian
$POF file:\t\t\t\t{pof}
$Detail distance:\t\t\t(0)
$Show damage:\t\t\t\tNO
$Density:\t\t\t\t1
$Damp:\t\t\t\t\t8.0
$Rotdamp:\t\t\t\t8.0
$Max Velocity:\t\t\t\t0.0, 0.0, 0.0
$Rotation time:\t\t\t\t60.0, 60.0, 60.0
$Rear Velocity:\t\t\t\t0.0
$Forward accel:\t\t\t\t0.0
$Forward decel:\t\t\t\t0.0
$Slide accel:\t\t\t\t0.0
$Slide decel:\t\t\t\t0.0
$Expl inner rad:\t\t\t{rad:.1f}
$Expl outer rad:\t\t\t{rad2:.1f}
$Expl damage:\t\t\t\t0.0
$Expl blast:\t\t\t\t0.0
$Default PBanks:\t\t\t()
$Default SBanks:\t\t\t()
$SBank Capacity:\t\t\t()
$Shields:\t\t\t\t0
$Power Output:\t\t\t\t1.0
$Max Oclk Speed:\t\t\t0.0
$Max Weapon Eng:\t\t\t0.0
$Hitpoints:\t\t\t\t{hp}
$Flags:\t\t\t\t\t( "dont collide invisible" )
$AI Class:\t\t\t\tCaptain
$Afterburner:\t\t\t\tNO
$Countermeasures:\t\t\t0
$Scan time:\t\t\t\t5000
$Closeup_pos:\t\t\t\t0.0, 0.0, -{close:.0f}
$Closeup_zoom:\t\t\t\t0.5
$Score:\t\t\t\t\t0

"""


def in_container(cmd):
    return subprocess.run(["/usr/bin/ssh", PROXMOX, "pct exec %s -- docker exec -i assetgen-queue %s" % (CT, cmd)],
                          capture_output=True, text=True)


def main():
    pofs, tbm = [], TBM_HEAD
    for key, w in WRECKS.items():
        d = "/data/jobs/" + w["job"]
        src = in_container("sh -c 'ls %s'" % d).stdout.split()
        mesh = next((f for f in ("result.obj", "result.glb", "mesh.glb", "model.glb") if f in src), None)
        if not mesh:
            print(key, "no mesh yet in", d, src)
            continue
        script = ("import trimesh;m=trimesh.load('%s/%s',force='mesh');m=m.simplify_quadric_decimation(face_count=%d);"
                  "m.export('%s/wreck.obj');print(len(m.faces))" % (d, mesh, w["faces"], d))
        r = in_container("python3 -c \"%s\"" % script)
        print(key, "decimated to", r.stdout.strip(), r.stderr.strip()[-200:])
        obj = subprocess.run(["/usr/bin/ssh", PROXMOX, "pct exec %s -- docker exec assetgen-queue cat %s/wreck.obj" % (CT, d)],
                             capture_output=True).stdout
        tmp = "/tmp/%s.obj" % key
        open(tmp, "wb").write(obj)
        pof = os.path.join(DATA, "models", key + ".pof")
        os.makedirs(os.path.dirname(pof), exist_ok=True)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "mesh2pof.py"), tmp, pof, "--texture", "wreck_hull",
                        "--length", str(w["length"]), "--tile", str(w["tile"])], check=True)
        rad = w["length"] / 2
        tbm += TBM_SHIP.format(cls=w["cls"], short=w["short"], pof=key + ".pof", rad=rad * 0.5, rad2=rad, hp=1000000,
                               close=w["length"] * 1.6)
    tbm += "#End\n"
    os.makedirs(os.path.join(DATA, "tables"), exist_ok=True)
    open(os.path.join(DATA, "tables", "wrecks-shp.tbm"), "w").write(tbm)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_wreck_textures.py"), os.path.join(DATA, "maps"), "1024"],
                   check=True)


if __name__ == "__main__":
    main()
