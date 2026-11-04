#!/usr/bin/env python3
"""Queues the second batch of wreck/derelict concepts in the assetgen queue: text-to-image (FLUX.3 Klein), then Hunyuan3D-2.1
with texture + UltraShape refine as soon as each image is done. Writes tools/wreck_batch2.json (key -> job ids).
Runs the API calls inside CT 140 (the queue port is firewalled from the LAN)."""
import json, os, subprocess, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wreck_batch2.json")
P = {
 # colonial warships
 "bs_bow": "wrecked bow section of a massive military space battlestar, torn off at the middle, jagged armored hull, exposed decks and girders, scorched dark gray metal",
 "bs_stern": "wrecked stern section of a massive military space battlestar with three huge engine nacelles, one nacelle broken off, scorched, derelict",
 "bs_midship": "midsection of a military space battlestar with its flight pods ripped open, hangar bays exposed, hull plates peeled back, derelict",
 "bs_pod": "detached landing pod of a battlestar, long open flight deck with a damaged hull, scorched, drifting wreck",
 "bs_tower": "command tower and spine fragment of a military space battlestar, antennas bent, hull torn, scorched, derelict",
 "bs_dome": "battlestar hull section with a collapsed pressure dome, armor plates buckled, exposed interior, derelict wreck",
 "frigate_half": "military space frigate snapped in half, long armored hull, gun turrets gutted, derelict wreck",
 "frigate_bow": "bow of a military space frigate only, torn off behind the bridge, scorched armor, turrets hanging, derelict",
 "cruiser": "heavy military space cruiser wreck, turrets destroyed, hull riddled with holes, long angular hull, derelict",
 "corvette": "small military space corvette wreck with missile launchers, hull split open, scorched, derelict",
 # cylon
 "basestar_whole": "wrecked alien robotic warship, three long broken arms radiating from a central hub, dark metal, red damage glow, derelict",
 "basestar_arm": "single long arm section of a robotic alien warship, torn off, dark metal, exposed machinery, derelict",
 "basestar_hub": "central hub of a robotic alien warship, round and ribbed, torn arms stubs, dark metal, derelict",
 "heavy_raider": "large wrecked robotic alien gunship, angular black hull, broken wing, scorched, derelict",
 "scout_wreck": "wrecked small robotic alien scout craft, black and silver, crumpled nose, derelict",
 # small craft
 "fighter_a": "single seat delta wing spacefighter wreck, one wing sheared off, cockpit shattered, scorched gray hull, top three quarter view",
 "fighter_b": "single seat spacefighter wreck, tail section missing, fuselage split, scorched gray hull, three quarter view",
 "transport": "twin engine military space transport wreck, cargo ramp open, hull cracked, derelict",
 "shuttle": "wrecked civilian space shuttle, white hull blackened, one engine missing, derelict",
 "pods": "cluster of three escape pods joined by torn cables, small round capsules, scorched, drifting",
 # civilian
 "liner_whole": "wrecked luxury space passenger liner, long smooth hull broken in the middle, windows dark, derelict",
 "liner_stern": "stern section of a space passenger liner with big engines, torn hull, windows dark, derelict",
 "yacht": "wrecked sleek private space yacht, hull breached, dark windows, derelict",
 "freighter": "wrecked bulk space freighter, boxy hull with cargo bays open, hull plates missing, derelict",
 "container_ship": "wrecked container space freighter with a frame carrying many cargo containers, some torn loose, derelict",
 "tanker": "wrecked space tanker with big cylindrical fuel tanks, one tank burst open, scorched, derelict",
 "refinery_wreck": "wrecked space refinery ship with three large round discs, one disc broken off, struts bent, derelict",
 "miner": "wrecked asteroid mining ship with a big drilling arm and ore hold, hull cracked, derelict",
 "ore_hauler": "wrecked ore hauler with a long truss frame and big cargo bucket, partly crushed, derelict",
 "tug": "wrecked space tug with large engines and grappling arms, scorched, derelict",
 "colony_ship": "wrecked huge round colony ship, ring-shaped habitat torn open, derelict",
 "research_ship": "wrecked research vessel with a large radio dish and sensor masts bent, hull cracked, derelict",
 "hospital_ship": "wrecked white hospital space ship with red cross markings, hull torn, derelict",
 "prison_barge": "wrecked prison transport barge, blocky dark hull with cell blocks, hull torn open, derelict",
 "fuel_depot": "wrecked orbital fuel depot with spherical tanks and a docking spine, tanks burst, derelict",
 # stations / structures
 "ring_segment": "broken segment of a rotating space station ring, spokes snapped, panels torn, derelict",
 "docking_arm": "bent docking arm structure of a space station with docking clamps, girders twisted, derelict",
 "solar_platform": "orbital platform with huge shredded solar panels and a central module, derelict",
 "relay_sat": "wrecked communications relay satellite with bent antenna array, derelict",
 "gantry": "wrecked shipyard construction gantry, big lattice frame partly collapsed, derelict",
 "hangar_module": "detached hangar module with a big open bay door, hull scorched and cracked, derelict",
 # debris
 "armor_slab": "large drifting slab of armor plating with girders and pipes sticking out, scrap debris chunk, dark gray metal",
 "nacelle": "detached engine nacelle, big nozzle at one end, scorched and torn, drifting wreckage",
 "turret_cluster": "cluster of destroyed gun turrets on a broken base plate, barrels bent, wreckage",
 "container_stack": "stack of cargo containers welded by damage into a clump, dented and torn, drifting debris",
 "bridge_section": "ship bridge section with a tall viewing window frame, torn off hull, derelict debris",
 "solar_array": "twisted solar array wreckage, folded panels on a bent mast, debris",
 "reactor_core": "exposed spherical reactor core with torn support struts and broken pipes, dark scorched, debris",
 "asteroid_wreck": "rocky asteroid with the wreck of a spaceship embedded in it, hull sticking out, derelict",
 "girder_tangle": "tangle of hull girders, pipes and cables forming a big floating scrap knot, debris",
 "hull_ring": "large circular hull ring section with ribs, torn edges, scorched, derelict debris",
}

def api(method, path, body=None):
    cmd = "curl -s -m 60 -X %s -H 'X-Remote-User: winicius' -H 'Content-Type: application/json' %s 'http://127.0.0.1:8000%s'" % (
        method, ("-d '%s'" % json.dumps(body)) if body is not None else "", path)
    r = subprocess.run(["/usr/bin/ssh", "root@proxmox.lan", "pct exec 140 -- " + cmd], capture_output=True, text=True)
    return json.loads(r.stdout)

done = json.load(open(OUT)) if os.path.exists(OUT) else {}
for key, prompt in P.items():
    if key in done:
        continue
    img = api("POST", "/api/jobs/text-to-image", {"model": "flux3-klein", "prompt": prompt, "image_type": "prop"})
    q = api("POST", "/api/jobs/%s/queue-3d" % img["id"], {"model_id": "hunyuan3d21", "texture": True, "refine": "ultrashape"})
    done[key] = {"image": img["id"], "scheduled": q.get("scheduled", False), "prompt": prompt}
    json.dump(done, open(OUT, "w"), indent=1)
    print(key, img["id"], "3d scheduled" if q.get("scheduled") else q, flush=True)
print(len(done), "concepts queued")
