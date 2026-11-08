"""Nightjar Cell: a ten mission guerrilla campaign (ambushes, raids, evacuations) for a squadron cut off from the fleet.
Imported by make_extra_missions.py. Reuses the templates of more_missions.py and adds two of its own: ambush and raid."""
from fsmission import Mission, offset, CYLON_FLAGS
import long_missions as lm
import more_missions as mm

W = "Nightjar"


def _roost(m, cfg):
    """The hideout tanker: far away, never attacked, the voice of the cell commander."""
    if any(w[0] == "Roost" for w in cfg.get("wards", [])):
        return
    m.ship("Roost", "Prometheus", "Friendly", cfg.get("roost_at", (9000.0, 600.0, -4000.0)), (0.0, 0.0, 0.0), arrival="( true )",
           flags='( "cargo-known" "invulnerable" "hidden-from-sensors" "no-shields" "don\'t-collide-invisible" )', flags2='( "immobile" )', shields=0, score=0)


def _marker(m, pos):
    m.ship("Marker", "Gemenon Freight Container 1", "Friendly", pos, (0.0, 0.0, 0.0), arrival="( true )",
           flags='( "cargo-known" "invulnerable" "hidden-from-sensors" "no-shields" "don\'t-collide-invisible" )', flags2='( "immobile" )', shields=0, score=0)


def ambush(cfg, seed):
    m, r, CIVIL, CAPITAL, win_end, fail_end = mm._head(cfg, seed)
    Z = (0.0, 0.0, 4200.0)
    m.player_wing(W, offset(Z, -1700.0, 150.0, -1500.0), Z, ["Shadow", "Flask"], guard="ai-chase-any 50", **mm.elite_wing(cfg))
    _marker(m, Z)
    m.waypoint_list("Lane", [offset(Z, 0.0, 0.0, -900.0), offset(Z, 0.0, 0.0, 400.0), offset(Z, 0.0, 0.0, 6000.0)])
    first = None
    kills = []
    for wname, cls, n, delay in cfg["patrols"]:
        start = offset(Z, 3600.0, 200.0, 4200.0)
        goal = 'ai-chase "Lifeline 1" 70' if cfg.get("bait") else 'ai-waypoints-once "Lane" 55'
        m.cylon_wing(wname, cls, n, start, Z, '( is-event-true-delay "Start" %d )' % delay, goal, spacing=140.0 if "Heavy" in cls else 90.0,
                     score=35 if "Heavy" in cls else 12)
        kills.append('( percent-ships-destroyed 100 "%s" )' % wname)
        first = first or "%s 1" % wname
    for i, (name, cls, delay) in enumerate(cfg.get("convoy", []), start=1):
        m.ship(name, cls, "Hostile", offset(Z, 3600.0, 100.0 * i, 4200.0 + 160.0 * i), Z, arrival='( is-event-true-delay "Start" %d )' % delay,
               ai_goals='ai-waypoints-once "Lane" 45', flags='( "cargo-known" "no-arrival-warp" "don\'t-collide-invisible" )', ai_class="Lieutenant", score=60)
        kills.append('( is-destroyed-delay 0 "%s" )' % name)
        first = first or name
    if cfg.get("bait"):
        m.ship("Lifeline 1", "Raptor", "Friendly", offset(Z, 0.0, 0.0, 200.0), Z, arrival="( true )", ai_class="Lieutenant",
               flags='( "cargo-known" "no-shields" "escort" "don\'t-collide-invisible" )', flags2='( "immobile" )', hull=100, score=0)
    if cfg.get("trap"):
        m.ship(cfg["trap"], "Frigate Bolitho Class", "Friendly", offset(Z, -2200.0, -100.0, 1800.0), Z, arrival='( is-event-true-delay "Spring" 1 )',
               ai_goals="ai-chase-any 90", flags='( "cargo-known" "no-arrival-warp" "don\'t-collide-invisible" )', ai_class="Lieutenant", shields=100, score=0)
    # the strike group waits in the dark until the zone closes
    names = []
    for i, cs in enumerate(["Brick", "Cutter", "Spike", "Pike"][:cfg.get("strike", 3)]):
        n = "Fang %d" % (i + 1)
        m.ship(n, "Viper Mark VIIe", "Friendly", offset(Z, -2500.0 + 60.0 * i, -250.0, 600.0), Z, arrival='( is-event-true-delay "Spring" 2 )',
               flags='( "cargo-known" "no-arrival-warp" "don\'t-collide-invisible" )', callsign=cs, ai_class="Lieutenant",
               primaries=mm.ELITE_GUNS, secondaries=mm.ELITE_MISSILES)
        names.append(n)
    m.wing("Fang", names, '( is-event-true-delay "Spring" 2 )', goals="ai-chase-any 60")
    if cfg.get("relief"):
        wname, cls, n, delay = cfg["relief"]
        m.cylon_wing(wname, cls, n, offset(Z, -3000.0, 300.0, 3800.0), Z, '( is-event-true-delay "Spring" %d )' % delay, "ai-chase-any 60",
                     spacing=140.0 if "Heavy" in cls else 90.0, score=35 if "Heavy" in cls else 12)
    mm._talk(m, cfg)
    m.event("Spring", '( when ( < ( distance "%s" "Marker" ) %d ) ( do-nothing ) )' % (first, cfg.get("trigger", 2400)))
    lm.say(m, "Spring", 1, "Roost", "Spring " + cfg["tag"], cfg["spring"])
    done = "( and %s )" % " ".join(kills) if len(kills) > 1 else kills[0]
    m.event("Cleared", '( when %s ( do-nothing ) )' % done)
    lm.say(m, "Cleared", 2, "Roost", "Clear " + cfg["tag"], cfg.get("clear", "That's all of them. Break contact, Nightjars, back to the rocks before the next one comes looking."))
    m.event("Win Cond", '( when ( and ( is-event-true-delay "Cleared" 0 ) ( > ( distance "%s 1" "Marker" ) 4500 ) ) ( do-nothing ) )' % W)
    fails = [("Lead Lost", '( is-destroyed-delay 1 "%s 1" )' % W), ("Too Late", '( is-event-true-delay "Start" %d )' % cfg["limit"])]
    if cfg.get("bait"):
        fails.insert(1, ("Bait Lost", '( is-destroyed-delay 1 "Lifeline 1" )'))
    mm._finish(m, cfg, win_end, fail_end, fails, (cfg["goal"][0], cfg["goal"][1]))
    return m


def raid(cfg, seed):
    m, r, CIVIL, CAPITAL, win_end, fail_end = mm._head(cfg, seed)
    Z = (0.0, 0.0, 5200.0)
    m.player_wing(W, (-600.0, 250.0, -1500.0), Z, ["Shadow", "Flask"], guard="ai-chase-any 50", **mm.elite_wing(cfg))
    _marker(m, Z)
    flags = '( "cargo-known" "no-arrival-warp" "don\'t-collide-invisible" )'
    names = []
    for name, cls, off in cfg["targets"]:
        m.ship(name, cls, "Hostile", offset(Z, *off), offset(Z, 0.0, 0.0, 3000.0), arrival="( true )", flags=flags, flags2='( "immobile" )', ai_class="Lieutenant", score=100, shields=0)
        names.append(name)
    for wname, cls, n, off in cfg["guards"]:
        m.cylon_wing(wname, cls, n, offset(Z, *off), Z, "( true )", 'ai-guard "%s" 60' % names[0], spacing=130.0 if "Heavy" in cls else 90.0, score=35 if "Heavy" in cls else 12)
    rw, rcls, rn, rdelay = cfg["relief"]
    if "Basestar" in rcls:
        m.ship(rw, rcls, "Hostile", offset(Z, 3500.0, 800.0, 3500.0), Z, arrival='( is-event-true-delay "Alarm" %d )' % rdelay, ai_goals="ai-chase-any 70",
               ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    else:
        m.cylon_wing(rw, rcls, rn, offset(Z, 3500.0, 300.0, 3500.0), Z, '( is-event-true-delay "Alarm" %d )' % rdelay, "ai-chase-any 70", score=20)
    mm._talk(m, cfg)
    m.event("Alarm", '( when ( is-destroyed-delay 0 "%s" ) ( do-nothing ) )' % names[0])
    lm.say(m, "Alarm", 1, "Roost", "Alarm " + cfg["tag"], cfg["alarm"])
    m.event("Cleared", '( when ( is-destroyed-delay 0 %s ) ( do-nothing ) )' % " ".join('"%s"' % n for n in names))
    lm.say(m, "Cleared", 2, "Roost", "Clear " + cfg["tag"], "Targets down. Break contact, Nightjars. Out through the rocks, don't fly the straight line.")
    m.event("Win Cond", '( when ( and ( is-event-true-delay "Cleared" 0 ) ( > ( distance "%s 1" "Marker" ) 6000 ) ) ( do-nothing ) )' % W)
    fails = [("Lead Lost", '( is-destroyed-delay 1 "%s 1" )' % W), ("Too Late", '( is-event-true-delay "Start" %d )' % cfg["limit"])]
    mm._finish(m, cfg, win_end, fail_end, fails, (cfg["goal"][0], cfg["goal"][1]))
    return m


def _cell(cfg):
    cfg.setdefault("wing", W)
    cfg.setdefault("elite", True)
    return cfg


CONFIGS = [
 ("XM-NJ01.fs2", raid, 201, _cell(dict(
    tag="NJ01", title="First Light",
    desc="Nightjar is a black ops cell: no roster, no insignia, assault Vipers that officially do not exist. Day one. A Cylon supply anchorage sits three kilometres from the rocks the cell is hiding in: three Movers and a pair of Raider guards. Hit it fast, hit it hard, and be gone before anyone calls it in.",
    targets=[("Mover A", "Colonial Mover", (0.0, 0.0, 0.0)), ("Mover B", "Colonial Mover", (-380.0, 100.0, -200.0)), ("Mover C", "Colonial Mover", (340.0, -80.0, -350.0))],
    guards=[("Sentry", "Raider", 2, (0.0, 200.0, 500.0))], relief=("Quick", "Raider", 4, 60), alarm="Alarm! They've got a call out. Six Raiders on the way. Finish and leave.",
    limit=840, goal=("Hit the anchorage", "Destroy the three Movers, then break contact"),
    lines=[(3, "Roost", "Nightjars, Roost. You are not on any roster and those assault Vipers are not in any hangar log. The fleet is far away and nobody is coming. We hurt them anyway."),
           (20, "Nightjar 2", "Shadow here. Three Movers, two Raiders. I'll take the Raiders."), (90, "Nightjar 3", "In and out. Don't get greedy, Lead."),
           (260, "Roost", "Lead, they heard that. Wrap it up."), (520, "Nightjar 2", "Break contact, break contact. Back to the rocks.")],
    win="Clean strike, clean exit. The anchorage is burning and nobody knows where we are.", lose="The strike failed and the cell has been seen. Roost is moving.",
    debrief_win="Three Cylon Movers destroyed and the cell is still a ghost. That is how this goes.", debrief_lose="The cell was seen.", tip="Hit hard, leave fast.", bonus=[]))),
 ("XM-NJ02.fs2", ambush, 202, _cell(dict(
    tag="NJ02", title="Dark Lane",
    desc="The Cylons run a patrol down a lane through the rocks every few minutes. The Nightjars sit in the dark, wait for the lead Raider to come within range, and strike. No warning, no quarter.",
    patrols=[("Lamp", "Raider", 6, 90), ("Lantern", "Heavy Raider", 2, 150)], strike=3, limit=840, trigger=2400, relief=None,
    spring="Contact. Weapons free, Nightjars. Make it quick.", goal=("Ambush the patrol", "Destroy every ship of the patrol and break contact"),
    lines=[(3, "Roost", "Nightjars, Roost. A patrol comes down Dark Lane in a few minutes. You wait in the dark. You do not fire until the lead ship is inside the marker."),
           (40, "Nightjar 2", "Engines cold, lights out. I can hear my own pulse."), (88, "Nightjar 3", "DRADIS says here they come. Six Raiders and two Heavies."),
           (230, "Nightjar 2", "Half done. Don't stop."), (400, "Roost", "Good. Now get out of the lane.")],
    win="The lane is clear and the patrol is scrap. The Cylons will be careful now.", lose="The ambush failed. The lane is lost.",
    debrief_win="A patrol that never got to call for help. That is what an ambush is.", debrief_lose="The patrol survived.", tip="Wait for the spring, then kill the Heavies first.", bonus=[]))),
 ("XM-NJ03.fs2", mm.escort, 203, _cell(dict(
    tag="NJ03", title="Cold Camp",
    desc="A Cylon scout has seen the rocks. The cell's hideout, the tanker Roost, has to move before the strike force arrives. The Nightjars escort her nine kilometres to the next hiding place.",
    wards=[("Roost", "Prometheus", (0.0, 0.0, 0.0))], length=9000.0, jump_at=720,
    waves=[("Snoop", "Raider", 4, 90, "Roost"), ("Prowl", "Advanced Raider", 4, 220, "Roost"), ("Claw", "Heavy Raider", 3, 380, "Roost"), ("Snap", "Raider", 6, 540, "any")],
    lines=[(3, "Roost", "Nightjars, we've been seen. I need nine kilometres of quiet and I won't get it. Keep them off my back."),
           (20, "Nightjar 2", "Roost is slow. We'll make her safe."), (95, "Nightjar 3", "Scouts. Four of them, close in."),
           (225, "Nightjar 2", "Advanced Raiders on my left. They're fast."), (390, "Roost", "Heavies! Don't let them launch, I won't survive a torpedo."),
           (560, "Nightjar 3", "More Raiders. They won't let go."), (700, "Roost", "Jump drive spooling. Hold on.")],
    win="Roost is clear and the cell has a new home. It's not much, but it's ours.", lose="Roost is gone, and with her the cell.",
    debrief_win="The hideout moved, the Cylons lost the trail.", debrief_lose="The hideout was lost.", tip="Kill the Heavies before they lock on.", bonus=[]))),
 ("XM-NJ04.fs2", ambush, 204, _cell(dict(
    tag="NJ04", title="Tripwire",
    desc="A powered-down Bolitho frigate, the Lodestar, sits dark in the rocks. A Nightjar flies bait, a Cylon strike group gives chase, and the Lodestar wakes up when they pass.",
    patrols=[("Hound", "Raider", 6, 120), ("Pack", "Advanced Raider", 4, 160), ("Heavy", "Heavy Raider", 3, 210)], strike=3, limit=900, trigger=2600, trap="Lodestar", relief=("Chaser", "Raider", 6, 80),
    spring="Now, Lodestar! Light them up!", goal=("Spring the trap", "Draw the Cylons into the Lodestar's guns and destroy them"),
    lines=[(3, "Roost", "Nightjars, the Lodestar's been dark for a month. She'll wake when the Cylons are on top of her. You are the bait."),
           (25, "Nightjar 2", "I hate being the bait. Fine, I'm good at it."), (125, "Nightjar 3", "Hounds on our six. Keep them chasing."),
           (215, "Nightjar 2", "Heavies. They're behind the rest."), (300, "Roost", "Lodestar's reactor is coming up. Hold on a few more seconds."),
           (420, "Nightjar 3", "That is a beautiful sight.")],
    win="The Lodestar did her part. The trap held. Well done, Nightjars.", lose="The trap failed. The Lodestar is lost.",
    debrief_win="Fourteen Raiders and three Heavies died on the Lodestar's guns.", debrief_lose="The trap collapsed.", tip="Stay ahead of the chasers and lead them past the frigate.", bonus=[]))),
 ("XM-NJ05.fs2", raid, 205, _cell(dict(
    tag="NJ05", title="Burn the Depot",
    desc="A Cylon fuel depot, a captured tanker and two Movers, feeds a dozen raiding wings. The Nightjars burn it. A basestar will jump in minutes after the first kill. Do not be there.",
    targets=[("Depot", "Prometheus", (0.0, 0.0, 0.0)), ("Hauler A", "Colonial Mover", (-420.0, 100.0, -200.0)), ("Hauler B", "Colonial Mover", (400.0, -90.0, -300.0))],
    guards=[("Watch", "Raider", 4, (0.0, 300.0, 700.0)), ("Hammer", "Heavy Raider", 2, (-300.0, -200.0, 500.0))], relief=("Anchor", "Basestar", 1, 140),
    alarm="First kill confirmed. The basestar is jumping in. Two minutes. Finish the targets and run.", limit=900, goal=("Burn the depot", "Destroy the depot and both haulers, then break contact"),
    lines=[(3, "Roost", "Nightjars, that depot fuels twelve wings. We burn it today. They'll send a basestar when it starts to burn, so we can't be slow."),
           (22, "Nightjar 2", "Four Raiders, two Heavies guarding. Standard."), (200, "Nightjar 3", "Depot's venting. Looks like a pyre."),
           (420, "Roost", "Basestar's here! Break contact, break contact!"), (500, "Nightjar 2", "She's launching. Run, run!")],
    win="The depot is a fireball and the cell is unseen. Remarkable work.", lose="The raid failed and the cell is trapped.",
    debrief_win="Twelve Cylon wings will fly dry for a month.", debrief_lose="The raid failed.", tip="Kill the Heavies first, then the depot.", bonus=[]))),
 ("XM-NJ06.fs2", ambush, 206, _cell(dict(
    tag="NJ06", title="Wolf Pack",
    desc="Three separate Cylon patrols come through the same lane, one behind the other. Hit each as it arrives, vanish into the rocks, repeat. Do it right and none of them reports back.",
    patrols=[("Wolf A", "Raider", 4, 100), ("Wolf B", "Raider", 5, 260), ("Wolf C", "Advanced Raider", 4, 420)], strike=2, limit=1000, trigger=2400,
    relief=("Call", "Raider", 4, 120), spring="First blood. Weapons free.", goal=("Kill the three patrols", "Destroy all three patrols and break contact"),
    lines=[(3, "Roost", "Nightjars, three patrols are due, ten minutes between them. Take them one at a time, hide between."),
           (110, "Nightjar 2", "First patrol on DRADIS. Four Raiders."), (265, "Nightjar 3", "Second patrol. They didn't see the wreckage of the first. Good."),
           (430, "Nightjar 2", "Advanced Raiders. They'll turn tight."), (600, "Roost", "Patrol is late back. They'll send someone to look. Move."),
           (720, "Nightjar 3", "A wolf pack hunts best at night.")],
    win="Three patrols, no survivors. The Cylons are blind in this sector tonight.", lose="One of the patrols got away and called it in.",
    debrief_win="Three patrols destroyed and not a call went out.", debrief_lose="A patrol escaped.", tip="Never fight two at once.", bonus=[]))),
 ("XM-NJ07.fs2", ambush, 207, _cell(dict(
    tag="NJ07", title="False Beacon",
    desc="A Raptor broadcasts a distress call from the middle of nowhere. The Cylons answer it. The Nightjars are waiting around the beacon.",
    patrols=[("Answer", "Raider", 8, 120), ("Escort", "Heavy Raider", 3, 200)], strike=3, limit=900, trigger=2600, bait=True, relief=("Late", "Advanced Raider", 4, 100),
    spring="They bit. Weapons free!", goal=("Spring the beacon trap", "Destroy the response force and keep the Raptor alive"),
    lines=[(3, "Roost", "Nightjars, a Raptor on a false beacon. The Cylons love an easy kill. Ambush them when they arrive."),
           (30, "Nightjar 2", "Lifeline is broadcasting. I feel sorry for whoever tries to rescue her."), (125, "Nightjar 3", "Eight Raiders heading for the beacon."),
           (205, "Nightjar 2", "Heavies behind them. Nukes, be careful."), (330, "Roost", "Keep that Raptor alive, I'd like to use her again.")],
    win="The beacon trap worked. The Cylons will think twice about answering a call.", lose="The Raptor is lost.",
    debrief_win="A false beacon cost the Cylons eleven ships.", debrief_lose="The bait was lost.", tip="Strike when the Heavies commit.", bonus=[]))),
 ("XM-NJ08.fs2", mm.rescue, 208, _cell(dict(
    tag="NJ08", title="Quiet Extraction",
    desc="Two captured Colonial pilots are held in a Cylon holding area, guarded by three Heavy Raiders that wake as soon as they see company. The Nightjars cover a Raptor to get them out.",
    pods=2, pod_lines=["First pilot aboard. He says thank you.", "Both pilots aboard. Out, out, out."],
    static=[("Warden", "Heavy Raider", 3, (0.0, 200.0, 4200.0), "ai-guard \"Pod 1\" 70", "( true )")],
    waves=[("Wake", "Raider", 5, 200, "Lifeline 1"), ("Chase", "Advanced Raider", 4, 380, "Lifeline 1")],
    lines=[(3, "Roost", "Nightjars, two of ours are in a Cylon holding pen. Three Heavies are on guard. Raptor in, Raptor out."),
           (25, "Lifeline 1", "Lifeline, creeping in. Quiet as a mouse."), (200, "Nightjar 2", "Raiders on the move. They've seen us."),
           (390, "Nightjar 3", "Advanced Raiders. They're coming in fast."), (520, "Roost", "Get them out, Lifeline!")],
    win="Both pilots are aboard. The cell has grown by two.", lose="We lost the rescue. Roost is silent.",
    debrief_win="Two pilots rescued from the Cylon pen.", debrief_lose="The rescue failed.", tip="Kill the Heavies before the Raptor goes in.", bonus=[]))),
 ("XM-NJ09.fs2", ambush, 209, _cell(dict(
    tag="NJ09", title="Hammer from Nowhere",
    desc="A Cylon convoy of four Movers with a heavy escort passes through the lane. Every Nightjar hits it at once from the dark. The Movers carry the Cylons' next offensive.",
    patrols=[("Guard", "Heavy Raider", 4, 160), ("Screen", "Raider", 6, 180)], convoy=[("Mover 1", "Colonial Mover", 175), ("Mover 2", "Colonial Mover", 185), ("Mover 3", "Colonial Mover", 195), ("Mover 4", "Colonial Mover", 205)],
    strike=4, limit=1020, trigger=2600, relief=("Wake", "Advanced Raider", 6, 120), spring="Now! Everything at once!",
    goal=("Break the convoy", "Destroy the four Movers and their escort, then break contact"),
    lines=[(3, "Roost", "Nightjars, the biggest target we've had. Four Movers and a heavy escort. Everything in the cell hits it at once."),
           (45, "Nightjar 2", "Let it come to us. Sit still."), (170, "Nightjar 3", "Convoy on DRADIS. Biggest I've seen."),
           (290, "Nightjar 2", "Movers first, they carry the payload."), (440, "Roost", "Advanced Raiders from the nearest picket. Move fast."),
           (560, "Nightjar 3", "That's the offensive, gone.")],
    win="The convoy is gone and the Cylon offensive with it. Fine work, Nightjars.", lose="The convoy got through.",
    debrief_win="Four Movers destroyed. The next offensive is delayed for weeks.", debrief_lose="The convoy escaped.", tip="Movers first, escort second.", bonus=[]))),
 ("XM-NJ10.fs2", mm.defend, 210, _cell(dict(
    tag="NJ10", title="Last Light",
    desc="The Cylons find the hideout. Roost needs twenty minutes of quiet to spool her drives, and the Nightjars give it to her. This is the last stand for the cell.",
    wards=[("Roost", "Prometheus", (0.0, 0.0, 0.0))], hold=1200, theseus=False, friends=[("Fang", 6, 0)],
    waves=[("L1", "Raider", 6, 40, "Roost"), ("L2", "Advanced Raider", 6, 150, "Roost"), ("L3", "Heavy Raider", 4, 280, "Roost"), ("L4", "Raider", 10, 420, "any"),
           ("L5", "Heavy Raider", 5, 560, "Roost"), ("L6", "Advanced Raider", 8, 700, "Roost"), ("L7", "Raider", 12, 840, "any"), ("L8", "Heavy Raider", 6, 980, "Roost"),
           ("L9", "Advanced Raider", 8, 1100, "Roost")],
    lines=[(3, "Roost", "Nightjars, this is it. Twenty minutes to spool the drives. I won't ask you to promise anything. Just hold."),
           (45, "Nightjar 2", "Here they come. The whole pack."), (160, "Nightjar 3", "Second wave. Advanced models."),
           (290, "Roost", "Heavies! Don't let them near me!"), (520, "Nightjar 2", "I've lost count. Keep shooting."),
           (790, "Nightjar 3", "Still here. Still shooting."), (1040, "Roost", "Drive's almost there. Hold on!"), (1190, "Roost", "Jump! Now!")],
    objective="Keep Roost alive until her drives spool", win="Roost is gone, the cell is gone, and the Cylons hold an empty rock. Light's out, Nightjars. Thank you.",
    lose="Roost is lost. The cell is finished.", debrief_win="The cell vanished. The Cylons will never find out where it went, or if it still exists.",
    debrief_lose="Roost was destroyed.", tip="Heavies first. They are the only wave that can hurt Roost.", bonus=[]))),
]

META = {
    "XM-NJ01.fs2": ("~9 min", "Easy"), "XM-NJ02.fs2": ("~10 min", "Medium"), "XM-NJ03.fs2": ("~12 min", "Medium"),
    "XM-NJ04.fs2": ("~12 min", "Hard"), "XM-NJ05.fs2": ("~14 min", "Hard"), "XM-NJ06.fs2": ("~15 min", "Medium"),
    "XM-NJ07.fs2": ("~13 min", "Hard"), "XM-NJ08.fs2": ("~11 min", "Medium"), "XM-NJ09.fs2": ("~16 min", "Hard"),
    "XM-NJ10.fs2": ("~22 min", "Very Hard"),
}


def build_all():
    out = []
    for fname, fn, seed, cfg in CONFIGS:
        m = fn(cfg, seed)
        _roost(m, cfg)
        out.append((fname, m))
    return out
