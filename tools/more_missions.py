"""Ten more missions for the Thunderlords Patrol Log, built from four small templates (escort, defend, hunt, rescue).
Imported by make_extra_missions.py. Every goal waits for the Win event (a "not destroyed" goal is true from the first second)."""
import random
from fsmission import Mission, offset
import long_missions as lm

# the Nightjar black ops flight: the assault Viper (one gun bank with more punch, three missile banks)
ELITE_GUNS = ["MEC-A6"]
ELITE_MISSILES = ["HD-70 Lightning Javelin", "HD-70 Lightning Javelin", "HD-51 Arbalest"]


def elite_wing(cfg):
    """player_wing keyword arguments for the Viper Mark VIIe flight when the mission asks for it (cfg['elite'])."""
    if not cfg.get("elite"):
        return {}
    return dict(player_class="Viper Mark VIIe", player_primaries=ELITE_GUNS, player_secondaries=ELITE_MISSILES,
                wing_class="Viper Mark VIIe", wing_primaries=ELITE_GUNS, wing_secondaries=ELITE_MISSILES)


LOADS = ["Load_SP-R1-M1.tga", "Load_SP-R1-M2.tga", "Load_SP-R1-M3.tga", "Load_SP-R1-M5.tga"]


def _head(cfg, seed):
    TEST, CIVIL, CAPITAL, win_end, fail_end = lm._setup()
    m = Mission(cfg["title"], cfg["desc"], TEST)
    r = random.Random(seed)
    m.load_screen = LOADS[seed % len(LOADS)]
    m.background["sun_angles"] = "%.6f %.6f %.6f" % (r.uniform(0.5, 6.0), r.uniform(0.5, 6.0), r.uniform(0.3, 1.4))
    return m, r, CIVIL, CAPITAL, win_end, fail_end


def _ring(r, center, rad, y=300.0):
    import math
    a = r.uniform(0, 6.2832)
    return offset(center, rad * math.cos(a), r.uniform(-y, y), rad * math.sin(a))


def _talk(m, cfg):
    _static(m, cfg)
    m.event("Start", '( when ( true ) ( do-nothing ) )')
    for i, (delay, sender, text) in enumerate(cfg["lines"], start=1):
        lm.say(m, "Start", delay, sender, "L%d %s" % (i, cfg["tag"]), text)


def _waves(m, r, cfg, centre, targets, spread=3600.0):
    """cfg['waves']: (wing, class, count, seconds after the start, target ship or 'any')."""
    for wname, cls, n, delay, tgt in cfg["waves"]:
        goal = "ai-chase-any 60" if tgt == "any" else 'ai-chase "%s" 80' % tgt
        score = 35 if "Heavy" in cls else 20 if "Advanced" in cls else 10
        pos = _ring(r, centre, spread)
        m.cylon_wing(wname, cls, n, pos, centre, '( is-event-true-delay "Start" %d )' % delay, goal,
                     spacing=140.0 if "Heavy" in cls else 80.0, score=score)


def _static(m, cfg):
    """cfg['static']: (wing, class, count, centre, goal, arrival condition): hostile groups that wait where the mission puts them."""
    for wname, cls, n, centre, goal, arr in cfg.get("static", []):
        m.cylon_wing(wname, cls, n, centre, (0.0, 0.0, 0.0), arr, goal, spacing=140.0 if "Heavy" in cls else 90.0,
                     score=35 if "Heavy" in cls else 10)


def _wing_friends(m, cfg, centre):
    for wname, n, delay in cfg.get("friends", []):
        names = []
        for i in range(n):
            p = offset(centre, -900.0 + 70.0 * i, 200.0, -1500.0 - 25.0 * i)
            nm = "%s %d" % (wname, i + 1)
            m.ship(nm, "Viper Mark VIIe" if cfg.get("elite") else "Viper Mark VII", "Friendly", p, centre, arrival='( is-event-true-delay "Start" %d )' % delay if delay else "( true )",
                   flags='( "cargo-known" "don\'t-collide-invisible" )', ai_class="Lieutenant", primaries=["MEC-A6", "MEC-A6"],
                   secondaries=["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"], callsign=cfg.get("callsigns", ["Ace", "Moth", "Rook", "Kite", "Ember", "Wren"])[i % 6] + ("" if i < 6 else str(i)))
            names.append(nm)
        m.wing(wname, names, '( is-event-true-delay "Start" %d )' % delay if delay else "( true )", goals="ai-chase-any 60")


def _finish(m, cfg, win_end, fail_end, fail_events, primary):
    m.message("W " + cfg["tag"], cfg["win"])
    m.event("Win Msg", '( when ( is-event-true-delay "Win Cond" 0 ) ( send-message "#Command" "High" "W %s" ) )' % cfg["tag"])
    m.event("Win", '( when ( is-event-true-delay "Win Msg" 3 ) ( do-nothing ) )')
    win_end(m, "Win")
    m.message("F " + cfg["tag"], cfg["lose"])
    for i, (ev, cond) in enumerate(fail_events, start=1):
        m.event(ev, '( when %s ( send-message "#Command" "High" "F %s" ) )' % (cond, cfg["tag"]))
    fail_end(m, [e for e, _ in fail_events])
    m.goal("Primary", primary[0], primary[1], '( is-event-true-delay "Win" 0 )', 100)
    for extra in cfg.get("bonus", []):
        m.goal("Bonus", extra[0], extra[1], '( and ( is-event-true-delay "Win" 0 ) %s )' % extra[2], extra[3])
    m.debrief('( is-event-true-delay "Win" 0 )', cfg["debrief_win"], cfg["tip"])
    m.debrief('( is-event-true-delay "%s" 0 )' % fail_events[0][0], cfg["debrief_lose"], cfg["tip"])


# ---------------------------------------------------------------------------------------------------------------------
def escort(cfg, seed):
    m, r, CIVIL, CAPITAL, win_end, fail_end = _head(cfg, seed)
    END = (r.uniform(-400, 400), r.uniform(0, 300), cfg.get("length", 9000.0))
    m.player_wing(cfg.get("wing", "Red"), (0.0, 300.0, -1800.0), END, ["Shadow", "Flask"], guard='ai-guard "%s" 60' % cfg["wards"][0][0], **elite_wing(cfg))
    m.waypoint_list("Lane", [(END[0] * 0.3, END[1] * 0.3, END[2] * 0.3), (END[0] * 0.7, END[1] * 0.7, END[2] * 0.7), END])
    jump = '( is-event-true-delay "Jump" 12 )'
    for i, (name, cls, off) in enumerate(cfg["wards"]):
        m.ship(name, cls, "Friendly", off, END, arrival="( true )", departure=jump, ai_goals='ai-waypoints-once "Lane" 90',
               flags=CIVIL, hull=100, shields=0, score=300)
    if cfg.get("guard"):
        m.ship(cfg["guard"], "Frigate Bolitho Class", "Friendly", (350.0, -80.0, -600.0), END, arrival="( true )", departure=jump,
               ai_goals='ai-guard "%s" 80' % cfg["wards"][0][0], flags=CAPITAL, shields=0, score=500)
    _wing_friends(m, cfg, (0.0, 0.0, 0.0))
    _waves(m, r, cfg, (END[0] * 0.5, END[1] * 0.5, END[2] * 0.5), None)
    _talk(m, cfg)
    m.event("Jump", '( when ( is-event-true-delay "Start" %d ) ( do-nothing ) )' % cfg["jump_at"])
    m.event("Win Cond", '( when ( has-departed-delay 3 "%s" ) ( do-nothing ) )' % cfg["wards"][0][0])
    fails = [("%s Lost" % w[0], '( is-destroyed-delay 1 "%s" )' % w[0]) for w in cfg["wards"][:1]]
    _finish(m, cfg, win_end, fail_end, fails, (cfg["wards"][0][0] + " arrives", "Get " + cfg["wards"][0][0] + " to the jump point"))
    if len(cfg["wards"]) > 1:
        m.goal("Secondary", "Keep the others", "Bring the rest of the convoy through",
               '( and ( is-event-true-delay "Win" 0 ) ( has-departed-delay 0 %s ) )' % " ".join('"%s"' % w[0] for w in cfg["wards"][1:]), 50)
    return m


def defend(cfg, seed):
    m, r, CIVIL, CAPITAL, win_end, fail_end = _head(cfg, seed)
    C = (0.0, 0.0, 0.0)
    m.player_wing(cfg.get("wing", "Red"), (-800.0, 250.0, -1400.0), C, ["Shadow", "Flask"], guard="ai-chase-any 60", **elite_wing(cfg))
    for name, cls, off in cfg["wards"]:
        m.ship(name, cls, "Friendly", off, offset(off, 0.0, 0.0, 3000.0), arrival="( true )", flags=CIVIL, flags2='( "immobile" )',
               hull=100, shields=0, score=0)
    if cfg.get("guard"):
        m.ship(cfg["guard"], "Frigate Bolitho Class", "Friendly", (600.0, 150.0, 700.0), (600.0, 150.0, 3700.0), arrival="( true )",
               ai_goals='ai-guard "%s" 90' % cfg["wards"][0][0], flags=CAPITAL, shields=100, score=0)
    _wing_friends(m, cfg, C)
    _waves(m, r, cfg, C, None)
    if cfg.get("theseus"):
        m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (400.0, -300.0, -9000.0), (200.0, -300.0, 0.0),
               arrival='( is-event-true-delay "Start" %d )' % cfg["hold"], ai_goals="ai-chase-any 100",
               flags='( "cargo-known" "no-shields" "don\'t-collide-invisible" )', shields=0, score=0)
    _talk(m, cfg)
    m.event("Win Cond", '( when ( and ( is-event-true-delay "Start" %d ) ( not ( is-destroyed-delay 0 "%s" ) ) ) ( do-nothing ) )' % (cfg["hold"] + 20, cfg["wards"][0][0]))
    fails = [("%s Lost" % w[0], '( is-destroyed-delay 1 "%s" )' % w[0]) for w in cfg["wards"]]
    _finish(m, cfg, win_end, fail_end, fails, ("Hold " + cfg["wards"][0][0], cfg["objective"]))
    return m


def hunt(cfg, seed):
    m, r, CIVIL, CAPITAL, win_end, fail_end = _head(cfg, seed)
    C = (0.0, 0.0, 6000.0)
    m.player_wing(cfg.get("wing", "Red"), (-700.0, 250.0, -1500.0), C, ["Shadow", "Flask"], guard="ai-chase-any 60", **elite_wing(cfg))
    m.waypoint_list("Lane", [(0.0, 0.0, 12000.0)])
    hostile_flags = '( "cargo-known" "no-arrival-warp" "don\'t-collide-invisible" )'
    for i, (name, cls, pos, goal) in enumerate(cfg["targets"]):
        dep = ('( is-event-true-delay "Escape" 5 )' if cfg.get("escape") else "( false )")
        m.ship(name, cls, "Hostile", pos, C, arrival="( true )", departure=dep, ai_goals=goal, flags=hostile_flags if "Basestar" not in cls else '( "no-arrival-message" )',
               ai_class="Lieutenant", score=1500 if "Basestar" in cls else 100)
    _wing_friends(m, cfg, (0.0, 0.0, 0.0))
    _waves(m, r, cfg, C, None, spread=2600.0)
    _talk(m, cfg)
    names = " ".join('"%s"' % t[0] for t in cfg["targets"])
    m.event("Win Cond", '( when ( is-destroyed-delay 0 %s ) ( do-nothing ) )' % names)
    fails = []
    if cfg.get("escape"):
        m.event("Escape", '( when ( is-event-true-delay "Start" %d ) ( do-nothing ) )' % cfg["escape"])
        fails.append(("Escaped", '( or ( has-departed-delay 1 %s ) ( has-departed-delay 1 "%s" ) )' % (names, cfg["targets"][0][0]) if len(cfg["targets"]) > 1 else '( has-departed-delay 1 %s )' % names))
    else:
        fails.append(("Out Of Time", '( is-event-true-delay "Start" %d )' % cfg["limit"]))
    fails.append(("Red Lost", '( is-destroyed-delay 1 "%s 1" )' % cfg.get("wing", "Red")))
    _finish(m, cfg, win_end, fail_end, fails, (cfg["goal"][0], cfg["goal"][1]))
    return m


def rescue(cfg, seed):
    m, r, CIVIL, CAPITAL, win_end, fail_end = _head(cfg, seed)
    C = (0.0, 0.0, 0.0)
    m.player_wing(cfg.get("wing", "Red"), (-500.0, 250.0, -1500.0), C, ["Shadow", "Flask"], guard='ai-guard "Lifeline 1" 60', **elite_wing(cfg))
    pods = []
    for i in range(cfg["pods"]):
        pods.append(_ring(r, (0.0, 0.0, 3200.0 + 1500.0 * i), 1100.0))
    legs = [offset(p, 0, 0, -250) for p in pods]
    m.ship("Lifeline 1", "Raptor", "Friendly", (-120.0, 50.0, -450.0), legs[0], arrival="( true )", ai_class="Lieutenant",
           flags='( "cargo-known" "no-shields" "escort" "don\'t-collide-invisible" )', hull=100, score=300, ai_goals='ai-waypoints-once "Leg 1" 60')
    for i, p in enumerate(pods, start=1):
        m.waypoint_list("Leg %d" % i, [offset(p, 0.0, 0.0, -120.0)])
        m.ship("Pod %d" % i, "Viper Pilot", "Friendly", p, (0.0, 0.0, 0.0), arrival="( true )",
               flags='( "cargo-known" "no-shields" "don\'t-collide-invisible" )', hull=100, shields=0, score=0)
    m.waypoint_list("Home", [(0.0, 0.0, -2800.0)])
    _wing_friends(m, cfg, C)
    _waves(m, r, cfg, (0.0, 0.0, 3200.0 + 750.0 * cfg["pods"]), None)
    _talk(m, cfg)
    for i in range(1, cfg["pods"] + 1):
        m.event("Pod %d Near" % i, '( when ( < ( distance "Lifeline 1" "Pod %d" ) 220 ) ( do-nothing ) )' % i)
        m.event("Pod %d Saved" % i, '( when ( is-event-true-delay "Pod %d Near" 12 ) ( ship-vanish "Pod %d" ) )' % (i, i))
        nxt = ('( add-goal "Lifeline 1" ( ai-waypoints-once "Leg %d" 60 ) )' % (i + 1)) if i < cfg["pods"] else '( add-goal "Lifeline 1" ( ai-waypoints-once "Home" 80 ) )'
        m.event("Leg %d Go" % (i + 1), '( when ( is-event-true-delay "Pod %d Saved" 2 ) %s )' % (i, nxt))
        m.message("Saved %d" % i, "Pod %d is aboard! %s" % (i, cfg["pod_lines"][(i - 1) % len(cfg["pod_lines"])]))
        m.event("Saved Msg %d" % i, '( when ( is-event-true-delay "Pod %d Saved" 3 ) ( send-message "Lifeline 1" "High" "Saved %d" ) )' % (i, i))
    m.event("Win Cond", '( when ( is-event-true-delay "Pod %d Saved" 55 ) ( do-nothing ) )' % cfg["pods"])
    fails = [("Lifeline Lost", '( is-destroyed-delay 1 "Lifeline 1" )')]
    fails += [("Pod %d Lost" % i, '( is-destroyed-delay 1 "Pod %d" )' % i) for i in range(1, cfg["pods"] + 1)]
    _finish(m, cfg, win_end, fail_end, fails, ("Pick up every pilot", "Bring all %d pilots aboard the Raptor" % cfg["pods"]))
    return m


# ---------------------------------------------------------------------------------------------------------------------
CONFIGS = [
 ("XM-Pods.fs2", rescue, 101, dict(
    tag="Pods", title="Lost Pilots",
    desc="A Viper squadron was caught in a jump scatter and the pilots ejected into the debris. The Raptor Lifeline has a few minutes to find "
         "and recover every one of them before the Raiders do. Red flight keeps her alive.",
    pods=4, pod_lines=["One more, lords, thank you.", "Alive, and cursing. That's a good sign.", "Barely breathing, but breathing.", "That's the last one!"],
    waves=[("Scav", "Raider", 4, 150, "Lifeline 1"), ("Reap", "Raider", 5, 330, "Lifeline 1"), ("Pike", "Advanced Raider", 4, 520, "Lifeline 1")],
    lines=[(3, "#Command", "Red flight, four of our pilots are in the debris field ahead. Lifeline picks them up, you keep the Raiders away."),
           (18, "Lifeline 1", "Lifeline one, rolling. Beacon tracking says four signals. Give me a few seconds at each."),
           (140, "Red 2", "Raiders on DRADIS, closing on the Raptor."), (320, "Red 3", "More of them. They smell the pilots, I swear."),
           (510, "Lifeline 1", "Red flight, last pod is close. Don't let them near me."), (640, "#Command", "Bring them all home, Red flight.")],
    win="All four pilots are aboard and the Raptor is clear. Good work, Red flight.", lose="We lost the rescue. Break off, Red flight.",
    debrief_win="Four pilots who would have died in the debris are alive tonight. The deck crew will remember it.",
    debrief_lose="A rescue is only as good as its escort. We lost the Raptor or a pilot.", tip="Stay between the Raptor and the next wave, not on top of her.")),
 ("XM-Crossing.fs2", escort, 102, dict(
    tag="Crossing", title="Crossing Fire",
    desc="Three Colonial Movers have to cross a lane between two Cylon pickets. Red flight runs close escort with the frigate Halyard.",
    wards=[("Mover 1", "Colonial Mover", (0.0, 0.0, 0.0)), ("Mover 2", "Colonial Mover", (-380.0, 100.0, -250.0)), ("Mover 3", "Colonial Mover", (330.0, -60.0, -500.0))],
    guard="Halyard", length=9000.0, jump_at=840,
    waves=[("Jackal", "Raider", 5, 90, "any"), ("Hound", "Advanced Raider", 4, 210, "Mover 1"), ("Mauler", "Heavy Raider", 3, 360, "Mover 2"),
           ("Fang", "Raider", 6, 520, "any"), ("Anvil", "Heavy Raider", 3, 680, "Mover 1")],
    lines=[(3, "#Command", "Red flight, three Movers need to cross between the pickets. Halyard rides with you."),
           (20, "Mover 1", "Mover one, holding the lane. We're not fast, but we don't stop."), (95, "Red 2", "Raiders at the first picket. Go to guns."),
           (215, "Halyard", "Halyard to Red flight, flak is up. Keep them in the lane."), (365, "Red 3", "Heavies! They carry torpedoes. Kill them early."),
           (520, "Mover 2", "Mover two, we took a hit but we're holding."), (690, "#Command", "One more wave, then the jump point. Don't let up.")],
    win="The convoy is across. Three Movers will keep the fleet fed. Well done.", lose="The lead Mover is gone. Break off, Red flight.",
    debrief_win="Three Movers through two pickets. The fleet eats well.", debrief_lose="The lead Mover was lost in the crossing.",
    tip="The Heavy Raiders arrive late and from the flank. Kill them before they close.")),
 ("XM-TankerDown.fs2", defend, 103, dict(
    tag="Tanker", title="Tanker Down",
    desc="The Prometheus tanker Boa's Journey lost a tylium line and is drifting while the crew patches it. Red flight and the frigate Halyard cover her for twelve minutes.",
    wards=[("Boa's Journey", "Prometheus", (0.0, 0.0, 0.0))], guard="Halyard", hold=720, theseus=False,
    friends=[("Green", 4, 0)],
    waves=[("Scrap", "Raider", 6, 45, "Boa's Journey"), ("Nail", "Raider", 6, 150, "Boa's Journey"), ("Hawk", "Heavy Raider", 3, 270, "Boa's Journey"),
           ("Dart", "Advanced Raider", 5, 400, "Boa's Journey"), ("Gnaw", "Raider", 8, 520, "any"), ("Maul", "Heavy Raider", 4, 630, "Boa's Journey")],
    lines=[(3, "#Command", "Red flight, the Boa's Journey is leaking tylium. Cover her until the crew seals the line."),
           (15, "Halyard", "Halyard to Red flight, we're on her flank. Green flight is on the high side."),
           (50, "Red 2", "Raiders coming in low. They want the leak."), (155, "Red 3", "The tanker's glowing like a lantern. They can see her from a lightyear."),
           (275, "Halyard", "Heavy Raiders, tanker side! Don't let them launch."), (410, "Red 2", "Advanced models. Break and chase, they won't turn."),
           (530, "#Command", "Four minutes. The crew says almost there."), (640, "Red 3", "More Heavies. Ugly day for a repair job.")],
    objective="Keep the tanker alive until the crew seals the leak", win="The Boa's Journey is patched and alive. The fleet's fuel is safe.",
    lose="The tanker is gone, and the fuel with her.", debrief_win="Twelve minutes under fire and the tanker survived. The fleet won't go dry.",
    debrief_lose="The Boa's Journey blew apart.", tip="Heavy Raiders carry torpedoes: intercept them before they launch.")),
 ("XM-Needle.fs2", rescue, 104, dict(
    tag="Needle", title="Needle Thread",
    desc="A Raptor must thread through a debris belt to recover two ejected crews and come back. Light contact is expected, which is why nobody gets careless.",
    pods=2, pod_lines=["Got them, both alive.", "Second crew aboard. Heading home."],
    waves=[("Peck", "Raider", 3, 180, "Lifeline 1"), ("Dive", "Raider", 4, 360, "Lifeline 1")],
    lines=[(3, "#Command", "Red flight, a Raptor goes in to recover two crews from the belt. Stay with her."),
           (30, "Lifeline 1", "Lifeline one, picking my way. Rocks are thick."), (190, "Red 2", "Raiders, three of them, closing."),
           (420, "Red 3", "Last crew is just ahead. Quiet now."), (520, "#Command", "Good. Bring her home.")],
    win="Both crews are aboard. Easy work, Red flight.", lose="We lost the Raptor. Break off.",
    debrief_win="Quiet rescue, clean result.", debrief_lose="The Raptor was lost in the belt.", tip="Raptors are slow: fly in front of her.")),
 ("XM-Decoy.fs2", hunt, 105, dict(
    tag="Decoy", title="Decoy",
    desc="A basestar is parked near the fleet. Command wants it drawn off. Red flight kills its four Heavy Raider escorts and holds its attention until the fleet slips away.",
    targets=[("Heavy 1", "Heavy Raider", (-900.0, 100.0, 6400.0), "ai-chase-any 70"), ("Heavy 2", "Heavy Raider", (-300.0, 0.0, 6600.0), "ai-chase-any 70"),
             ("Heavy 3", "Heavy Raider", (300.0, 120.0, 6500.0), "ai-chase-any 70"), ("Heavy 4", "Heavy Raider", (900.0, -60.0, 6300.0), "ai-chase-any 70")],
    limit=900, friends=[("Blue", 2, 120)], waves=[("Cover", "Raider", 6, 150, "any"), ("Sweep", "Advanced Raider", 4, 330, "any"), ("Roar", "Raider", 8, 520, "any")],
    goal=("Kill the escort", "Destroy all four Heavy Raiders"),
    lines=[(3, "#Command", "Red flight, four Heavies are screening the basestar. Kill them and we'll slip away while it watches you."),
           (25, "Red 2", "Eyes on the Heavies. Four of them, tight formation."), (150, "Red 3", "More Raiders from the basestar. They're awake."),
           (330, "Red 2", "Advanced models. Keep your speed up."), (520, "#Command", "Theseus to Red flight, the fleet is clear of the area. Finish and get out."),
           (640, "Red 3", "I hate being bait. I'm good at it though.")],
    win="The escort is dead and the fleet slipped away. Pull back, Red flight.", lose="Red flight is down or the window closed.",
    debrief_win="The basestar chased your wake while the fleet escaped.", debrief_lose="The decoy failed.", tip="Heavies first, fighters second.")),
 ("XM-Basestar.fs2", hunt, 106, dict(
    tag="Hunt", title="Basestar Hunt",
    desc="A lone basestar has been shadowing the fleet. Red flight and Blue flight go out to kill her and her Raider screen.",
    targets=[("Reaver", "Basestar", (500.0, 300.0, 7600.0), "ai-chase-any 70")],
    limit=1380, friends=[("Blue", 4, 0)], callsigns=["Ghost", "Rook", "Tango", "Mule", "Wren", "Kite"],
    waves=[("Net", "Raider", 6, 120, "any"), ("Thorn", "Heavy Raider", 4, 300, "any"), ("Vane", "Advanced Raider", 6, 480, "any"), ("Chaff", "Raider", 8, 700, "any")],
    goal=("Sink the Reaver", "Destroy the basestar"),
    lines=[(3, "#Command", "Red flight, a lone basestar is out there and she knows we're here. Kill her."),
           (60, "Red 2", "Basestar at eleven, range ten kilometres. Raiders ahead of her."), (130, "Red 3", "Raiders on our nose. Lock and shoot."),
           (310, "Red 2", "Heavies launching. Nukes!"), (500, "Red 3", "Advanced Raiders from the left. They're quick."),
           (720, "#Command", "Keep the pressure on. We can't let her run."), (1000, "Red 2", "Her hull is cracking. A few more passes.")],
    win="The Reaver is breaking apart. Good hunting, Red flight.", lose="Red flight is down or she got away.",
    debrief_win="One more basestar off the board.", debrief_lose="The hunt failed.", tip="Missiles and guns on the same turret arc work best.")),
 ("XM-Intercept.fs2", hunt, 107, dict(
    tag="Intercept", title="Ghost Convoy",
    desc="Six Cylon-aligned Movers are running a blockade. They jump in eight minutes. Red flight and Blue flight kill all six before the drives are ready.",
    targets=[("Runner 1", "Colonial Mover", (-800.0, 100.0, 5600.0), "ai-waypoints-once \"Lane\" 70"), ("Runner 2", "Colonial Mover", (-400.0, 0.0, 5800.0), "ai-waypoints-once \"Lane\" 70"),
             ("Runner 3", "Colonial Mover", (0.0, 120.0, 6000.0), "ai-waypoints-once \"Lane\" 70"), ("Runner 4", "Colonial Mover", (400.0, -50.0, 5700.0), "ai-waypoints-once \"Lane\" 70"),
             ("Runner 5", "Colonial Mover", (800.0, 60.0, 5900.0), "ai-waypoints-once \"Lane\" 70"), ("Runner 6", "Colonial Mover", (0.0, -150.0, 6200.0), "ai-waypoints-once \"Lane\" 70")],
    escape=480, friends=[("Blue", 2, 0)], waves=[("Guard", "Raider", 5, 100, "any"), ("Sting", "Advanced Raider", 4, 260, "any")],
    goal=("Stop the runners", "Destroy all six Movers before they jump"),
    lines=[(3, "#Command", "Red flight, six blockade runners are about to jump. Stop every one of them."),
           (35, "Red 2", "Runners in a loose pack. They're not armed."), (100, "Red 3", "Raiders coming in to guard them."),
           (260, "Red 2", "Advanced Raiders, high side."), (400, "#Command", "Eighty seconds to their jump."), (440, "Red 3", "Two left. Guns, guns!")],
    win="All six runners are scrap. Good shooting.", lose="A runner escaped or Red flight is down.",
    debrief_win="The blockade is broken. Nothing escaped.", debrief_lose="A Mover got away.", tip="Use missiles on the far ones, guns on the near ones.")),
 ("XM-Quiet.fs2", defend, 108, dict(
    tag="Quiet", title="Quiet Night",
    desc="A light night on the picket. The shuttle Pixie ferries a deck crew and the Raiders are expected to be few. Easy duty, at least on paper.",
    wards=[("Pixie", "Shuttle Mark I", (0.0, 0.0, 0.0))], guard=None, hold=360, theseus=False, friends=[("Green", 3, 0)],
    waves=[("Peck", "Raider", 3, 100, "Pixie"), ("Test", "Raider", 4, 220, "any")],
    lines=[(3, "#Command", "Red flight, light duty tonight. The Pixie ferries a deck crew, you keep an eye out."),
           (30, "Pixie", "Pixie here, passengers are asleep. I'm not."), (110, "Red 2", "Raiders on DRADIS, three. Small."),
           (230, "Red 3", "Four more. I thought it'd be quiet."), (330, "#Command", "Good. Bring her in.")],
    objective="Keep the shuttle alive", win="The Pixie is in and the deck crew is none the wiser.", lose="The shuttle is lost.",
    debrief_win="An easy night, easily won.", debrief_lose="Even a quiet night can go wrong.", tip="Never leave a shuttle alone, even for a minute.")),
 ("XM-LastShuttle.fs2", escort, 109, dict(
    tag="Shuttle", title="Last Shuttle",
    desc="The last evacuation shuttle from a dying station has to cross to the Theseus before the Raiders catch it. Red flight flies cover.",
    wards=[("Shuttle 1", "Gemenon Traveler", (0.0, 0.0, 0.0))], length=7000.0, jump_at=420,
    waves=[("Fast", "Advanced Raider", 4, 60, "Shuttle 1"), ("Dart", "Raider", 6, 160, "Shuttle 1"), ("Last", "Heavy Raider", 3, 280, "Shuttle 1")],
    lines=[(3, "#Command", "Red flight, the last shuttle is lifting off. Get her to the fleet."), (20, "Shuttle 1", "Shuttle one, we have forty aboard. Hurry, please."),
           (65, "Red 2", "Fast ones on our six. Break them up."), (165, "Red 3", "More Raiders. They're after the shuttle."), (285, "Red 2", "Heavies. Don't let them launch."),
           (380, "#Command", "Thirty seconds. Fly, fly.")],
    win="Forty people are aboard the Theseus. Well done, Red flight.", lose="The shuttle is gone. Break off.",
    debrief_win="Forty people made it.", debrief_lose="The shuttle was lost.", tip="Break their formation early, they're fast.")),
 ("XM-Gauntlet.fs2", defend, 110, dict(
    tag="Gauntlet", title="The Gauntlet",
    desc="The tanker Cassia, the freighter Hesper and the frigate Halyard hold a picket against the heaviest assault the Cylons have thrown in a month. Twenty-two minutes, no reinforcements until the Theseus arrives.",
    wards=[("Cassia", "Prometheus", (0.0, 0.0, 0.0)), ("Hesper", "Gemenon Freighter", (-420.0, 100.0, -260.0))], guard="Halyard", hold=1320, theseus=True,
    friends=[("Green", 6, 0), ("Blue", 6, 480)],
    waves=[("A1", "Raider", 6, 40, "Cassia"), ("A2", "Raider", 8, 140, "Hesper"), ("A3", "Heavy Raider", 4, 260, "Cassia"), ("A4", "Advanced Raider", 6, 380, "Hesper"),
           ("A5", "Raider", 10, 500, "any"), ("A6", "Heavy Raider", 5, 640, "Cassia"), ("A7", "Advanced Raider", 8, 780, "Hesper"), ("A8", "Raider", 10, 920, "any"),
           ("A9", "Heavy Raider", 6, 1060, "Cassia"), ("A10", "Raider", 12, 1180, "any")],
    lines=[(3, "#Command", "Red flight, the Cassia and the Hesper are on picket with Halyard. The Cylons are throwing everything. The Theseus is twenty-two minutes out."),
           (30, "Halyard", "Halyard to all stations, Green flight is on the high side. Hold the line."), (150, "Red 2", "Second wave on the Hesper. Eight of them."),
           (270, "Red 3", "Heavy Raiders for the tanker. Nukes!"), (500, "Cassia", "Cassia, we've got hull breaches on deck four. We can hold, barely."),
           (640, "Halyard", "Halyard, Heavies. Concentrate fire."), (1000, "Red 2", "I've lost count of the waves."), (1250, "#Command", "Theseus is jumping in. One more minute.")],
    objective="Keep the Cassia alive until the Theseus arrives", win="The Theseus is here and the picket held. Remarkable, Red flight.", lose="The picket has failed.",
    debrief_win="Twenty-two minutes of the heaviest assault of the month, and the picket stands.", debrief_lose="The Cassia or the Hesper was lost.",
    tip="The Heavy Raiders are the only wave that can hurt the Cassia. Kill them first.")),
]

META = {
    "XM-Pods.fs2": ("~9 min", "Easy"), "XM-Crossing.fs2": ("~14 min", "Medium"), "XM-TankerDown.fs2": ("~12 min", "Hard"),
    "XM-Needle.fs2": ("~7 min", "Easy"), "XM-Decoy.fs2": ("~12 min", "Hard"), "XM-Basestar.fs2": ("~20 min", "Hard"),
    "XM-Intercept.fs2": ("~9 min", "Medium"), "XM-Quiet.fs2": ("~6 min", "Very Easy"), "XM-LastShuttle.fs2": ("~8 min", "Hard"),
    "XM-Gauntlet.fs2": ("~23 min", "Very Hard"),
}


def build_all():
    return [(fname, fn(cfg, seed)) for fname, fn, seed, cfg in CONFIGS]
