"""Five long missions (20+ minutes) for the Thunderlords Patrol Log. Imported by make_extra_missions.py.

All of them share one rhythm: a phase starts when the previous one has been fought down AND a minimum time has
passed, so a mission never takes less than its planned length, and never advances while the player is losing."""
import math
from fsmission import Mission, offset

# set by make_extra_missions.py (it owns the shared flag constants and the win/fail helpers)
G = {}


def _setup():
    return G["TEST"], G["CIVIL"], G["CAPITAL"], G["win_end"], G["fail_end"]


def phase(m, name, after, delay, also=None):
    """Event `name` fires `delay` seconds after event `after`, and (if given) once `also` is true."""
    cond = '( is-event-true-delay "%s" %d )' % (after, delay)
    if also:
        cond = "( and %s %s )" % (cond, also)
    m.event(name, "( when %s ( do-nothing ) )" % cond)


def say(m, event, delay, sender, msg_name, text, alive=True):
    m.message(msg_name, text)
    cond = '( is-event-true-delay "%s" %d )' % (event, delay)
    if alive and not sender.startswith("#"):
        cond = '( and %s ( not ( is-destroyed-delay 0 "%s" ) ) )' % (cond, sender)
    m.event("Say " + msg_name, '( when %s ( send-message "%s" "High" "%s" ) )' % (cond, sender, msg_name))


def blue_wing(m, pos, face, arrival):
    for i, (cs, off) in enumerate([("Ghost", -60.0), ("Rook", 0.0)]):
        m.ship("Blue %d" % (i + 1), "Viper Mark VII", "Friendly", offset(pos, off, 0.0, -20.0 * i), face, arrival=arrival,
               flags='( "cargo-known" "don\'t-collide-invisible" )', callsign=cs, ai_class="Lieutenant",
               primaries=["MEC-A6", "MEC-A6"], secondaries=["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"])
    m.wing("Blue", ["Blue 1", "Blue 2"], arrival, goals="ai-chase-any 60")



# --- wreckage: drifting hull plates and wrecks (models generated with the assetgen queue, see make_wrecks.py) -----------
_orig_ship = Mission.ship


def _recording_ship(self, name, cls, team, pos, *a, **k):
    self.__dict__.setdefault("_placed", []).append(pos)
    return _orig_ship(self, name, cls, team, pos, *a, **k)


Mission.ship = _recording_ship
# The generated wreck models (split from two assetgen jobs, see split_glb.py) are a separate model pack: while this is False
# the missions use the stock civilian hulks and no wreckage props.
USE_WRECKS = False
WRECK_PIECES = ["Wreck Hull", "Wreck Flight Deck", "Wreck Engine", "Wreck Shell", "Wreck Wall", "Wreck Spine"]
HULK_CLASSES = (["Wreck Hull", "Wreck Flight Deck", "Wreck Engine", "Wreck Carrier"] if USE_WRECKS else
                ["Gemenon Traveler", "Gemenon Freighter", "Colonial Mover", "Intersun Passenger Cruiser"])
PROP_FLAGS = '( "invulnerable" "hidden-from-sensors" "no-shields" "don\'t-collide-invisible" )'


def _free(m, pos, clearance):
    return all(sum((a - b) ** 2 for a, b in zip(pos, q)) > clearance ** 2 for q in m.__dict__.get("_placed", []))


def wreckage(m, tag, center, plates=6, spread=900.0, seed=1, big=None, big_at=None):
    """Scatter inert hull plates around `center` (never closer than 500 m to anything already in the mission) and optionally
    one large wreck (class `big`, at `big_at`)."""
    if not USE_WRECKS:
        return
    import random
    r = random.Random(seed)
    if big:
        pos = big_at
        m.ship("Remnant %s" % tag, big, "Friendly", pos, offset(pos, r.uniform(-1, 1), r.uniform(-0.3, 0.3), r.uniform(-1, 1)),
               arrival="( true )", flags=PROP_FLAGS, score=0)
    n = 0
    for _ in range(min(plates, 4) * 20):          # the pieces are 300 to 700 m long: few of them, well apart
        if n >= min(plates, 4):
            break
        ang, rad = r.uniform(0, 6.2832), r.uniform(1100.0, 1100.0 + spread)
        pos = offset(center, rad * math.cos(ang), r.uniform(-spread * 0.4, spread * 0.4), rad * math.sin(ang))
        if not _free(m, pos, 900.0):
            continue
        n += 1
        m.ship("Debris %s%d" % (tag, n), r.choice(WRECK_PIECES), "Friendly", pos,
               offset(pos, r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)),
               arrival="( true )", flags=PROP_FLAGS, score=0)


# ==============================================================================================================
def long_watch():
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("The Long Watch",
                "The tanker Cassia needs half an hour at the Halyard's picket station to top up the fleet's reserves, and the "
                "Cylons will find out. Red flight holds the station through six waves until Cassia's pumps are done and both ships "
                "can jump.", TEST)
    m.load_screen = "Load_SP-R1-M5.tga"
    m.background["sun_angles"] = "2.100000 0.900000 4.700000"
    H, C = (0.0, 0.0, 0.0), (-700.0, -160.0, 350.0)
    m.player_wing("Red", (-1800.0, 350.0, -1200.0), H, ["Shadow", "Flask"], guard='ai-guard "Cassia" 60')
    go = '( is-event-true-delay "Jump Go" 25 )'
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", H, (0.0, 0.0, 5000.0), arrival="( true )", departure=go,
           flags=CAPITAL, shields=0, score=600)
    m.ship("Cassia", "Prometheus", "Friendly", C, (0.0, 0.0, 5000.0), arrival="( true )", departure=go, flags=CIVIL,
           hull=100, shields=0, score=400, cargo="Tylium")
    blue_wing(m, (-1700.0, 250.0, -1300.0), H, '( is-event-true-delay "Blue Cue" 0 )')

    # the six waves
    m.cylon_wing("Scout", "Raider", 4, (3000.0, 400.0, 3200.0), H, '( is-event-true-delay "Phase 1" 0 )', 'ai-chase "Halyard" 70')
    m.cylon_wing("Fang", "Raider", 4, (-3200.0, -300.0, 3600.0), H, '( is-event-true-delay "Phase 2" 0 )', 'ai-chase "Cassia" 70')
    m.cylon_wing("Maul", "Heavy Raider", 3, (2600.0, -500.0, 3800.0), H, '( is-event-true-delay "Phase 2" 25 )',
                 'ai-chase "Halyard" 90', spacing=150.0, score=35)
    m.cylon_wing("Wisp", "Advanced Raider", 4, (3400.0, 900.0, -1800.0), H, '( is-event-true-delay "Phase 3" 0 )',
                 "ai-chase-any 70", score=20)
    m.ship("Nemesis", "Basestar", "Hostile", (5200.0, 900.0, 9500.0), H, arrival='( is-event-true-delay "Phase 4" 0 )',
           ai_goals='ai-chase "Halyard" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Horde", "Raider", 6, (4600.0, 800.0, 8200.0), H, '( is-event-true-delay "Phase 4" 12 )', "ai-chase-any 60")
    m.cylon_wing("Hammer", "Heavy Raider", 4, (-2800.0, -700.0, 4200.0), H, '( is-event-true-delay "Phase 5" 0 )',
                 'ai-chase "Cassia" 100', spacing=160.0, score=35)
    m.cylon_wing("Dusk", "Advanced Raider", 4, (2600.0, 1100.0, -2400.0), H, '( is-event-true-delay "Phase 6" 0 )',
                 "ai-chase-any 80", score=20)
    m.cylon_wing("Last", "Raider", 6, (-3600.0, 200.0, 3000.0), H, '( is-event-true-delay "Phase 6" 20 )', 'ai-chase "Halyard" 70')

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" "Cassia" ) )')
    say(m, "Start", 2, "#Command", "L Orders", "Red flight, Halyard and Cassia hold station at the western picket. Cassia needs thirty minutes of pumping, "
        "and the Cylons will smell it on the wind. Nobody leaves until she's full.")
    say(m, "Start", 14, "Cassia", "L Cassia", "Cassia, pumps are running. Thirty-two minutes on my gauge, I'm sorry. I'll shout the moment it's done.")
    say(m, "Start", 24, "Halyard", "L Halyard", "Halyard here, flak is up and the gunners are fresh. Red leader, keep them off Cassia's flanks.")
    m.event("Blue Cue", '( when ( is-event-true-delay "Start" 360 ) ( do-nothing ) )')
    phase(m, "Phase 1", "Start", 70)
    say(m, "Phase 1", 6, "Red 3", "L Scout", "Four Raiders, bearing zero three zero. Probing the line, they want to see how hard we hit back.")
    phase(m, "Phase 2", "Phase 1", 200, '( percent-ships-destroyed 75 "Scout" )')
    say(m, "Phase 2", 6, "Red 2", "L Fang", "More company from the north! They're coming for Cassia this time.")
    say(m, "Phase 2", 32, "Halyard", "L Maul", "Heavy Raiders on the stern, torpedo profile. All batteries, tracking!")
    say(m, "Phase 2", 90, "Cassia", "L Pumps 1", "Pumps are at thirty percent. If you can keep it quiet for a few minutes, it would be nice.")
    phase(m, "Phase 3", "Phase 2", 210, '( and ( percent-ships-destroyed 75 "Fang" ) ( percent-ships-destroyed 75 "Maul" ) )')
    say(m, "Phase 3", 4, "Blue 1", "L Blue In", "Ghost and Rook on station. Command sent us to hold the line with you.")
    say(m, "Phase 3", 14, "Red 2", "L Wisp", "Advanced models, fast ones. They're trying to cut around the back of the Halyard.")
    say(m, "Phase 3", 100, "Halyard", "L Halyard Hit", "Taking hits on the dorsal plating, nothing structural. Keep them off our engines, Red flight.")
    phase(m, "Phase 4", "Phase 3", 230, '( percent-ships-destroyed 75 "Wisp" )')
    say(m, "Phase 4", 4, "#Command", "L Basestar", "DRADIS, basestar! One of theirs has jumped in thirty kilometres out and is launching. Halyard, hold your position.")
    say(m, "Phase 4", 20, "Cassia", "L Pumps 2", "Sixty percent. Please tell me I don't have to disconnect.")
    say(m, "Phase 4", 60, "Red 3", "L Horde", "Six Raiders off the basestar. They're all over us!")
    phase(m, "Phase 5", "Phase 4", 240, '( percent-ships-destroyed 75 "Horde" )')
    say(m, "Phase 5", 6, "Halyard", "L Hammer", "Four Heavy Raiders breaking from the basestar, straight for Cassia! Red flight, get on them!")
    say(m, "Phase 5", 80, "Red 2", "L Hammer Down", "Got one! Keep going, they're the ones with the torpedoes.")
    phase(m, "Phase 6", "Phase 5", 200, '( percent-ships-destroyed 75 "Hammer" )')
    say(m, "Phase 6", 4, "Cassia", "L Pumps 3", "Ninety percent! Ten more minutes and I can jump. Hold on to me, Red flight.")
    say(m, "Phase 6", 40, "Red 3", "L Dusk", "Last of the escorts coming around, I count eight. Everything we have, now!")
    phase(m, "Jump Cue", "Phase 6", 180, '( percent-ships-destroyed 75 "Dusk" "Last" )')
    say(m, "Jump Cue", 3, "Cassia", "L Full", "Tanks full! Spooling the drive. Thank you, Red flight, thank you.")
    m.event("Jump Go", '( when ( is-event-true-delay "Jump Cue" 10 ) ( do-nothing ) )')
    m.message("L Win", "Cassia and Halyard are away with a full load of tylium. Half an hour on station and nobody lost. Excellent work, Red flight.")
    m.event("Win", '( when ( and ( has-departed-delay 2 "Cassia" ) ( has-departed-delay 2 "Halyard" ) ) ( send-message "#Command" "High" "L Win" ) )')
    win_end(m, "Win")
    m.message("L Lost", "We lost the station. Break off and fall back to the fleet.")
    m.event("Cassia Lost", '( when ( is-destroyed-delay 1 "Cassia" ) ( send-message "#Command" "High" "L Lost" ) )')
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "L Lost" ) )')
    fail_end(m, ["Cassia Lost", "Halyard Lost"])

    m.goal("Primary", "Hold the station", "Keep Cassia and the Halyard alive until they jump", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Break the waves", "Destroy the Cylon attack waves", '( percent-ships-destroyed 70 "Scout" "Fang" "Maul" "Wisp" "Horde" "Hammer" "Dusk" "Last" )', 100)
    m.goal("Bonus", "Sink the Nemesis escorts", "Destroy all four Heavy Raiders of the Hammer wing", '( is-destroyed-delay 0 "Hammer 1" "Hammer 2" "Hammer 3" "Hammer 4" )', 40)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Thirty minutes of pumping, six Cylon waves and a basestar, and Cassia jumped with her tanks full. The reserve is safe.",
              "Kill the Heavy Raiders first, every wave after the second tries to reach the tanker.")
    m.debrief('( or ( is-event-true-delay "Cassia Lost" 0 ) ( is-event-true-delay "Halyard Lost" 0 ) )',
              "The station fell and the tylium with it. The reserve will be short this month.",
              "Keep your wing close to Cassia and take the Heavy Raiders before they release their torpedoes.")
    wreckage(m, "W", offset(H, 1800.0, 200.0, 2600.0), plates=7, spread=1100.0, seed=11, big="Wreck Hull", big_at=(3600.0, 500.0, 4800.0))
    return m


# ==============================================================================================================
def cold_convoy():
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Cold Convoy",
                "Three civilian ships and the frigate Halyard have twenty-two minutes to cross the Ragnar belt to the jump point. "
                "The Cylons will hit them from every side. Red flight escorts, and loses nobody.", TEST)
    m.load_screen = "Load_SP-R1-M6.tga"
    m.background["sun_angles"] = "5.000000 1.700000 3.100000"
    L = [(0.0, 0.0, 2500.0), (350.0, 150.0, 6000.0), (-300.0, 250.0, 9500.0), (200.0, 100.0, 13000.0)]
    END = (200.0, 100.0, 14000.0)
    P = {"Tern": (-250.0, 60.0, 0.0), "Briony": (250.0, -40.0, -250.0), "Aster": (0.0, -120.0, 450.0)}
    jump = '( is-event-true-delay "Convoy Jump" 14 )'
    m.player_wing("Red", (0.0, 300.0, -1900.0), END, ["Shadow", "Flask"], guard='ai-guard "Aster" 60')
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", (700.0, 0.0, -400.0), END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Convoy Lane" 40', flags=CAPITAL, shields=0, score=600)
    for name, cls in (("Tern", "Gemenon Freighter"), ("Briony", "Gemenon Traveler"), ("Aster", "Intersun Passenger Cruiser")):
        m.ship(name, cls, "Friendly", P[name], END, arrival="( true )", departure=jump, ai_goals='ai-waypoints-once "Convoy Lane" 40',
               flags=CIVIL, hull=100, shields=0, score=300)
    m.waypoint_list("Convoy Lane", L)
    blue_wing(m, (-400.0, 300.0, -2000.0), END, '( is-event-true-delay "Blue Cue" 0 )')

    ctr = lambda x, y, z: (x, y, z)
    m.cylon_wing("Hawk", "Raider", 4, ctr(3200, 200, 3600), P["Aster"], '( is-event-true-delay "Wave 1" 0 )', 'ai-chase "Aster" 70')
    m.cylon_wing("Mauler", "Heavy Raider", 3, ctr(-3000, -400, 5200), P["Aster"], '( is-event-true-delay "Wave 2" 0 )', 'ai-chase "Briony" 90', spacing=150.0, score=35)
    m.cylon_wing("Kite", "Advanced Raider", 4, ctr(3400, 800, 8200), P["Aster"], '( is-event-true-delay "Wave 3" 0 )', 'ai-chase "Tern" 80', score=20)
    m.cylon_wing("Fury", "Advanced Raider", 4, ctr(-3400, 700, 9000), P["Aster"], '( is-event-true-delay "Wave 3" 15 )', "ai-chase-any 80", score=20)
    m.ship("Warden", "Basestar", "Hostile", (4800.0, 900.0, 15000.0), P["Aster"], arrival='( is-event-true-delay "Wave 4" 0 )',
           ai_goals='ai-chase "Aster" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Swarm", "Raider", 6, ctr(4200, 700, 13600), P["Aster"], '( is-event-true-delay "Wave 4" 10 )', "ai-chase-any 60")
    m.cylon_wing("Talon", "Heavy Raider", 4, ctr(-3000, -600, 11000), P["Aster"], '( is-event-true-delay "Wave 5" 0 )', 'ai-chase "Aster" 100', spacing=160.0, score=35)
    m.cylon_wing("Dust", "Advanced Raider", 5, ctr(3000, 1000, 6000), P["Aster"], '( is-event-true-delay "Wave 6" 0 )', "ai-chase-any 80", score=20)

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" "Tern" "Briony" "Aster" ) )')
    say(m, "Start", 2, "#Command", "C Orders", "Red flight, the convoy has twenty-two minutes to make the jump point, nine hundred metres a minute no faster. "
        "Halyard rides with it. Keep every ship alive.")
    say(m, "Start", 16, "Aster", "C Aster", "Aster here, four hundred and twelve aboard. We were told this would be quiet.")
    say(m, "Start", 30, "Tern", "C Tern", "Tern, loaded to the gunwales with medical supplies. We'll stay on the lane, Red leader.")
    m.event("Blue Cue", '( when ( is-event-true-delay "Start" 420 ) ( do-nothing ) )')
    phase(m, "Wave 1", "Start", 100)
    say(m, "Wave 1", 6, "Red 3", "C Hawk", "Four Raiders from the port beam. They're after the cruiser.")
    phase(m, "Wave 2", "Wave 1", 220, '( percent-ships-destroyed 75 "Hawk" )')
    say(m, "Wave 2", 6, "Halyard", "C Mauler", "Heavy Raiders on the stern! Red flight, they have torpedoes!")
    phase(m, "Wave 3", "Wave 2", 240, '( percent-ships-destroyed 75 "Mauler" )')
    say(m, "Wave 3", 5, "Red 2", "C Pincer", "Advanced Raiders from both flanks, they're trying to pincer us.")
    say(m, "Wave 3", 70, "Blue 1", "C Blue", "Ghost and Rook, joining from the fleet. Sorry we're late, Red leader.")
    phase(m, "Wave 4", "Wave 3", 260, '( percent-ships-destroyed 75 "Kite" "Fury" )')
    say(m, "Wave 4", 4, "#Command", "C Basestar", "DRADIS, basestar dead ahead! They set a trap at the jump point. Convoy, keep your course.")
    say(m, "Wave 4", 40, "Briony", "C Briony", "Briony, we're taking fire on the starboard side! Please hurry!")
    phase(m, "Wave 5", "Wave 4", 260, '( percent-ships-destroyed 75 "Swarm" )')
    say(m, "Wave 5", 5, "Halyard", "C Talon", "Four more Heavies, they want Aster. Everything we have on them!")
    phase(m, "Wave 6", "Wave 5", 210, '( percent-ships-destroyed 75 "Talon" )')
    say(m, "Wave 6", 4, "Red 3", "C Dust", "Last wave, five Advanced Raiders, all at once. Don't let anyone through!")
    phase(m, "Drive Ready", "Wave 6", 150, '( percent-ships-destroyed 75 "Dust" )')
    say(m, "Drive Ready", 2, "Aster", "C Jump", "Jump point in range! Spooling now, ten seconds. Thank you all.")
    m.event("Convoy Jump", '( when ( is-event-true-delay "Drive Ready" 8 ) ( do-nothing ) )')
    m.message("C Win", "The convoy is through, four hundred and twelve passengers and the whole medical shipment. A long, cold run and you did it well.")
    m.event("Win", '( when ( and ( has-departed-delay 2 "Aster" ) ( has-departed-delay 2 "Tern" ) ( has-departed-delay 2 "Briony" ) ) ( send-message "#Command" "High" "C Win" ) )')
    win_end(m, "Win")
    m.message("C Lost", "We lost a ship of the convoy. Break off, Red flight.")
    for n in ("Aster", "Tern", "Briony", "Halyard"):
        m.event("%s Lost" % n, '( when ( is-destroyed-delay 1 "%s" ) ( send-message "#Command" "High" "C Lost" ) )' % n)
    fail_end(m, ["Aster Lost", "Tern Lost", "Briony Lost", "Halyard Lost"])

    m.goal("Primary", "Deliver the convoy", "Get Aster, Tern and Briony to the jump point", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Keep the Halyard", "The Halyard must survive", '( and ( is-event-true-delay "Win" 0 ) ( not ( is-destroyed-delay 0 "Halyard" ) ) )', 50)
    m.goal("Bonus", "Sink the Warden", "Destroy the basestar Warden", '( is-destroyed-delay 0 "Warden" )', 50)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Every ship of the convoy reached the jump point. Twenty-two minutes of escort and six waves of Cylons, and nobody was lost.",
              "Meet the Heavy Raiders early, they do all the damage to slow ships.")
    m.debrief('( or ( is-event-true-delay "Aster Lost" 0 ) ( is-event-true-delay "Tern Lost" 0 ) ( is-event-true-delay "Briony Lost" 0 ) ( is-event-true-delay "Halyard Lost" 0 ) )',
              "A civilian ship went down on the lane. The convoy's loss is on all of us.",
              "Stay with the convoy rather than chasing Raiders, and kill the Heavies on every wave.")
    return m


# ==============================================================================================================
def dead_hulks():
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Dead Hulks",
                "A Colonial convoy died in the Perihelion belt two years ago, and Command wants what its wrecks are still "
                "broadcasting. The Raptor Lantern surveys four hulks while Red flight keeps the scavengers off her. Each stop takes "
                "its time.", TEST)
    m.load_screen = "Load_SP-R1-M2.tga"
    m.background["sun_angles"] = "3.700000 5.200000 1.300000"
    S = [(0.0, 0.0, 0.0), (2800.0, 400.0, 3600.0), (-2400.0, -300.0, 7600.0), (500.0, 600.0, 11800.0)]
    m.player_wing("Red", (-900.0, 250.0, -1700.0), S[0], ["Shadow", "Flask"], guard='ai-guard "Lantern 1" 60')
    m.ship("Lantern 1", "Raptor", "Friendly", (-150.0, 60.0, -500.0), S[0], arrival="( true )", ai_class="Lieutenant",
           flags='( "cargo-known" "no-shields" "escort" "don\'t-collide-invisible" )', hull=100, score=300,
           ai_goals='ai-waypoints-once "Leg 1" 60')
    m.waypoint_list("Leg 1", [offset(S[0], 0, 0, 450)])
    m.waypoint_list("Leg 2", [offset(S[1], 0, 0, 450)])
    m.waypoint_list("Leg 3", [offset(S[2], 0, 0, 450)])
    m.waypoint_list("Leg 4", [offset(S[3], 0, 0, 450)])
    m.waypoint_list("Home", [(0.0, 0.0, -2600.0)])
    hulk_flags = ('( "protect-ship" "no-shields" "invulnerable" "hidden-from-sensors" "don\'t-collide-invisible" )')
    for i, (pos, cls) in enumerate(zip(S, HULK_CLASSES)):
        m.ship("Hulk %s" % "ABCD"[i], cls, "Friendly", pos, offset(pos, 0.3, 0.8, 0.2), arrival="( true )", flags=hulk_flags, score=0)
    blue_wing(m, (-1300.0, 250.0, -1900.0), S[0], '( is-event-true-delay "Blue Cue" 0 )')

    spots = [(3600.0, 300.0, 5200.0), (-3600.0, 400.0, 6000.0), (3200.0, -300.0, 10200.0), (-3000.0, 500.0, 12600.0)]
    m.cylon_wing("Gleaner", "Raider", 4, spots[0], S[1], '( is-event-true-delay "Site 1 Done" 6 )', 'ai-chase "Lantern 1" 70')
    m.cylon_wing("Reaper", "Heavy Raider", 3, spots[1], S[2], '( is-event-true-delay "Site 2 Wait" 40 )', 'ai-chase "Lantern 1" 90', spacing=150.0, score=35)
    m.cylon_wing("Stalk", "Advanced Raider", 4, spots[2], S[3], '( is-event-true-delay "Site 3 Wait" 30 )', 'ai-chase "Lantern 1" 80', score=20)
    m.ship("Carrion", "Basestar", "Hostile", (5200.0, 1000.0, 15600.0), S[3], arrival='( is-event-true-delay "Site 4 Wait" 60 )',
           ai_goals='ai-chase "Lantern 1" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Scavs", "Raider", 6, spots[3], S[3], '( is-event-true-delay "Site 4 Wait" 70 )', "ai-chase-any 60")
    m.cylon_wing("Rear", "Raider", 4, (0.0, 200.0, -3600.0), S[0], '( is-event-true-delay "Leg 4 Go" 40 )', 'ai-chase "Lantern 1" 80')

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 25 "Lantern 1" ) )')
    say(m, "Start", 2, "#Command", "D Orders", "Red flight, escort the Raptor Lantern through four wrecks in the Perihelion belt. She needs several minutes at each to download "
        "the black boxes. Keep her alive and keep her within the survey range of every hulk.")
    say(m, "Start", 14, "Lantern 1", "D Lantern", "Lantern one, ready to start. I'll tell you the moment a site is done. Stay close, I'm unarmed.")
    m.event("Blue Cue", '( when ( is-event-true-delay "Start" 600 ) ( do-nothing ) )')
    # site arrivals: the raptor flies a short leg to each hulk, then sits on it for the survey
    for i, letter in enumerate("ABCD", start=1):
        m.event("Site %d Wait" % i, '( when ( < ( distance "Lantern 1" "Hulk %s" ) 650 ) ( do-nothing ) )' % letter)
        m.event("Site %d Done" % i, '( when ( is-event-true-delay "Site %d Wait" %d ) ( do-nothing ) )' % (i, 240 + 20 * i))
    say(m, "Site 1 Wait", 2, "Lantern 1", "D Site 1", "At the first hulk. Download started, about four minutes. Please don't let anything near me.")
    say(m, "Site 1 Done", 2, "Lantern 1", "D Site 1 Done", "First box is clean. Moving to the second wreck. Red flight, stay with me.")
    m.event("Leg 2 Go", '( when ( is-event-true-delay "Site 1 Done" 10 ) ( add-goal "Lantern 1" ( ai-waypoints-once "Leg 2" 60 ) ) )')
    say(m, "Site 1 Done", 14, "Red 3", "D Gleaner", "Four Raiders from the belt, scavengers. They smell the Raptor.")
    say(m, "Site 2 Wait", 3, "Lantern 1", "D Site 2", "Second wreck. This one has damaged memory, it'll take longer. Hold the line.")
    say(m, "Site 2 Wait", 45, "Red 2", "D Reaper", "Heavy Raiders from the high side! They're targeting Lantern!")
    say(m, "Site 2 Done", 2, "Lantern 1", "D Site 2 Done", "Second wreck done. On to number three. This is not a quiet belt.")
    m.event("Leg 3 Go", '( when ( is-event-true-delay "Site 2 Done" 10 ) ( add-goal "Lantern 1" ( ai-waypoints-once "Leg 3" 60 ) ) )')
    say(m, "Site 3 Wait", 3, "Lantern 1", "D Site 3", "Third wreck, a transport. There's a lot of data in this one, five minutes.")
    say(m, "Site 3 Wait", 35, "Red 3", "D Stalk", "Advanced Raiders, circling low. They're fast, don't let them get inside!")
    say(m, "Site 3 Done", 2, "Lantern 1", "D Site 3 Done", "Third done. Last one is the big hulk. Almost there.")
    m.event("Leg 4 Go", '( when ( is-event-true-delay "Site 3 Done" 10 ) ( add-goal "Lantern 1" ( ai-waypoints-once "Leg 4" 60 ) ) )')
    say(m, "Site 4 Wait", 3, "Lantern 1", "D Site 4", "Last wreck, the flagship's bridge. Six minutes. I'm sorry, it's the one that matters.")
    say(m, "Site 4 Wait", 65, "#Command", "D Basestar", "DRADIS, basestar, bearing zero four zero! A hunting group has followed the Raptor.")
    say(m, "Site 4 Done", 2, "Lantern 1", "D Site 4 Done", "Got everything! Heading home now. Cover me, Red flight, this part is not over.")
    m.event("Go Home", '( when ( is-event-true-delay "Site 4 Done" 10 ) ( add-goal "Lantern 1" ( ai-waypoints-once "Home" 80 ) ) )')
    m.event("Home Reached", '( when ( and ( is-event-true-delay "Site 4 Done" 30 ) ( < ( distance "Lantern 1" "Red 1" ) 3000 ) ( percent-ships-destroyed 50 "Scavs" ) ) ( do-nothing ) )')
    m.message("D Win", "Lantern is back in the fleet's range and the data is on the way to the analysts. A good haul, Red flight.")
    m.event("Win", '( when ( is-event-true-delay "Home Reached" 120 ) ( send-message "#Command" "High" "D Win" ) )')
    win_end(m, "Win")
    m.message("D Lost", "We lost Lantern and everything she carried. Break off.")
    m.event("Lantern Lost", '( when ( is-destroyed-delay 1 "Lantern 1" ) ( send-message "#Command" "High" "D Lost" ) )')
    fail_end(m, ["Lantern Lost"])

    m.goal("Primary", "Survey the four hulks", "Stay with Lantern until all four wrecks are downloaded", '( is-event-true-delay "Site 4 Done" 0 )', 100)
    m.goal("Primary", "Bring Lantern home", "Get the Raptor out of the belt alive", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Bonus", "Sink the Carrion", "Destroy the hunting basestar", '( is-destroyed-delay 0 "Carrion" )', 50)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Four wrecks, four black boxes and a basestar that tried to follow us home. The analysts will be busy for weeks.",
              "The Raptor is slow and unarmed, always fly between it and the Raiders.")
    m.debrief('( is-event-true-delay "Lantern Lost" 0 )', "We lost the Raptor and her data in the belt.",
              "Stay within a kilometre of Lantern at every wreck, the Heavies come on a timer.")
    for i, pos in enumerate(S):
        wreckage(m, "S%d_" % (i + 1), pos, plates=4, spread=700.0, seed=20 + i)
    return m


# ==============================================================================================================
def hammerfall():
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Hammerfall",
                "The fleet strikes at the Cylon staging area in Ostrava Reach: a damaged basestar, its raider screen and a second "
                "basestar still jumping in. Red flight leads Blue flight and the Halyard in. The Theseus arrives for the second round.",
                TEST)
    m.load_screen = "Load_SP-R1-M3.tga"
    m.background["sun_angles"] = "1.400000 3.900000 0.800000"
    H, A, B = (-1500.0, 0.0, -1000.0), (800.0, 300.0, 11000.0), (-1200.0, -400.0, 16500.0)
    m.player_wing("Red", (-2600.0, 350.0, -1800.0), A, ["Shadow", "Flask"], guard="ai-chase-any 60")
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", H, A, arrival="( true )", ai_goals='ai-chase "Alpha" 60',
           flags=CAPITAL, shields=0, score=600)
    blue_wing(m, (-2700.0, 250.0, -1900.0), A, "( true )")
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (-6000.0, 1200.0, -2500.0), B, arrival='( is-event-true-delay "Theseus In" 0 )',
           ai_goals='ai-chase "Beta" 80', flags=CAPITAL, shields=0, score=1000)

    m.ship("Alpha", "Basestar", "Hostile", A, H, arrival="( true )", ai_goals='ai-chase "Halyard" 70', ai_class="Lieutenant", hull=45,
           flags='( "no-arrival-message" )', score=1500)
    m.ship("Beta", "Basestar", "Hostile", B, H, arrival='( is-event-true-delay "Beta In" 0 )', ai_goals='ai-chase "Theseus" 80', ai_class="Lieutenant",
           hull=70, flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Screen", "Raider", 6, (1800.0, 300.0, 6000.0), H, "( true )", "ai-chase-any 60")
    m.cylon_wing("Lance", "Heavy Raider", 4, (-1500.0, 600.0, 7500.0), H, '( is-event-true-delay "Phase 2" 0 )', 'ai-chase "Halyard" 100', spacing=150.0, score=35)
    m.cylon_wing("Veil", "Advanced Raider", 5, (3000.0, 800.0, 8800.0), H, '( is-event-true-delay "Phase 3" 0 )', "ai-chase-any 80", score=20)
    m.cylon_wing("Pyre", "Raider", 6, (-2600.0, 500.0, 13000.0), H, '( is-event-true-delay "Beta In" 8 )', "ai-chase-any 60")
    m.cylon_wing("Spike", "Heavy Raider", 4, (1800.0, 200.0, 14500.0), H, '( is-event-true-delay "Beta In" 70 )', 'ai-chase "Theseus" 100', spacing=150.0, score=35)

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" ) )')
    say(m, "Start", 2, "#Command", "H Orders", "Red flight, this is the strike on Ostrava Reach. The first basestar is already damaged. Halyard and Blue flight go in with you, "
        "Theseus follows in force once the second one shows. Destroy both.")
    say(m, "Start", 20, "Blue 1", "H Ghost", "Ghost and Rook on your wing, Red leader. Ready to light them up.")
    say(m, "Start", 32, "Halyard", "H Halyard", "Halyard, flak is hot. We'll take the first bite of that basestar, you take the screen.")
    phase(m, "Phase 2", "Start", 150, '( percent-ships-destroyed 70 "Screen" )')
    say(m, "Phase 2", 6, "Red 3", "H Lance", "Heavy Raiders from the basestar, torpedo profile! They want the Halyard!")
    phase(m, "Phase 3", "Phase 2", 240, '( percent-ships-destroyed 70 "Lance" )')
    say(m, "Phase 3", 6, "Red 2", "H Veil", "Advanced Raiders, five of them, hitting from high. They're good ones.")
    say(m, "Phase 3", 120, "Halyard", "H Alpha Hit", "We're hammering the basestar, her hull is breaking up! Keep the Raiders off us, Red flight!")
    phase(m, "Beta In", "Phase 3", 200, '( is-destroyed-delay 0 "Alpha" )')
    say(m, "Beta In", 3, "#Command", "H Beta", "Second basestar jumping in, bearing three three zero! Theseus, you are clear to engage.")
    phase(m, "Theseus In", "Beta In", 40)
    say(m, "Theseus In", 4, "Theseus", "H Theseus", "Theseus on station, all batteries. Red flight, you have the Raiders. We have the basestar.")
    say(m, "Theseus In", 120, "Red 3", "H Pyre", "Raiders everywhere, Theseus is drawing them but they keep coming! Cover the old girl!")
    say(m, "Theseus In", 240, "Theseus", "H Beta Hit", "Beta's hull is failing. Keep those Heavies off our bow, Red flight, one more minute!")
    m.message("H Win", "Both basestars are gone and the Cylon staging area is wreckage. Fleet to Red flight: that's the best afternoon we've had in a year.")
    m.event("Win", '( when ( and ( is-destroyed-delay 0 "Alpha" ) ( is-destroyed-delay 0 "Beta" ) ) ( send-message "#Command" "High" "H Win" ) )')
    win_end(m, "Win")
    m.message("H Lost", "The Halyard is gone and the strike has failed. Fall back to the fleet.")
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "H Lost" ) )')
    m.event("Theseus Lost", '( when ( is-destroyed-delay 1 "Theseus" ) ( send-message "#Command" "High" "H Lost" ) )')
    fail_end(m, ["Halyard Lost", "Theseus Lost"])

    m.goal("Primary", "Destroy the Alpha", "Sink the damaged basestar", '( is-destroyed-delay 0 "Alpha" )', 100)
    m.goal("Primary", "Destroy the Beta", "Sink the second basestar with the Theseus", '( is-destroyed-delay 0 "Beta" )', 100)
    m.goal("Bonus", "Keep the fleet whole", "Do not lose either of Blue flight", '( and ( is-event-true-delay "Win" 0 ) ( and ( not ( is-destroyed-delay 0 "Blue 1" ) ) ( not ( is-destroyed-delay 0 "Blue 2" ) ) ) )', 40)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Both basestars are wreckage and the Cylon staging area is gone. A real victory for the fleet.",
              "Clear the Raider screen before you press the basestar, the Heavies are what kill frigates.")
    m.debrief('( or ( is-event-true-delay "Halyard Lost" 0 ) ( is-event-true-delay "Theseus Lost" 0 ) )',
              "We lost a capital ship and the strike with her.",
              "Keep the Heavy Raiders off the Halyard and bring the Theseus in at the right moment.")
    wreckage(m, "H", offset(A, -1500.0, -200.0, -2800.0), plates=8, spread=1500.0, seed=31, big="Wreck Flight Deck", big_at=(-3400.0, -300.0, 6800.0))
    return m


# ==============================================================================================================
def last_stand():
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Last Stand at Armistice",
                "Armistice Station is being evacuated, and the movers need thirty minutes to load. The Cylons know it. Red flight and "
                "the Halyard hold the station through everything the Cylons throw at it, until the Theseus jumps in.",
                TEST)
    m.load_screen = "Load_SP-R1-M4.tga"
    m.background["sun_angles"] = "4.200000 2.400000 5.600000"
    S = (0.0, 0.0, 0.0)
    m.player_wing("Red", (-2200.0, 300.0, -1800.0), S, ["Shadow", "Flask"], guard='ai-guard "Armistice" 60')
    m.ship("Armistice", "Armistice Station", "Friendly", S, (0.0, 0.0, 5000.0), arrival="( true )",
           flags='( "cargo-known" "no-shields" "escort" "don\'t-collide-invisible" )', hull=100, score=1000)
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", (900.0, 100.0, -600.0), S, arrival="( true )", ai_goals="ai-chase-any 60",
           flags=CAPITAL, shields=0, score=600)
    movers = [("Allsop", (-500.0, 150.0, 300.0)), ("Keplaw", (500.0, -200.0, 500.0)), ("Pixie", (0.0, 300.0, 800.0))]
    for i, (n, pos) in enumerate(movers, start=1):
        m.ship(n, "Colonial Mover", "Friendly", pos, offset(pos, 0.0, 0.0, 6000.0), arrival="( true )",
               departure='( is-event-true-delay "Mover %d Go" 18 )' % i, flags=CIVIL, hull=100, shields=0, score=300)
    blue_wing(m, (-2300.0, 250.0, -1900.0), S, '( is-event-true-delay "Blue Cue" 0 )')
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (-6500.0, 1500.0, 2500.0), S, arrival='( is-event-true-delay "Theseus In" 0 )',
           ai_goals="ai-chase-any 80", flags=CAPITAL, shields=0, score=1000)

    cw = m.cylon_wing
    cw("Snap", "Raider", 4, (3400.0, 200.0, 3500.0), S, '( is-event-true-delay "Wave 1" 0 )', 'ai-chase "Allsop" 70')
    cw("Talon", "Heavy Raider", 3, (-3200.0, -400.0, 4200.0), S, '( is-event-true-delay "Wave 2" 0 )', 'ai-chase "Armistice" 90', spacing=150.0, score=35)
    cw("Wasp", "Advanced Raider", 5, (3800.0, 700.0, -2400.0), S, '( is-event-true-delay "Wave 3" 0 )', "ai-chase-any 80", score=20)
    m.ship("Ironhand", "Basestar", "Hostile", (5500.0, 1100.0, 10500.0), S, arrival='( is-event-true-delay "Wave 4" 0 )', ai_goals='ai-chase "Armistice" 80',
           ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    cw("Swarm", "Raider", 6, (4600.0, 900.0, 9200.0), S, '( is-event-true-delay "Wave 4" 10 )', "ai-chase-any 60")
    cw("Hook", "Heavy Raider", 4, (-3000.0, -700.0, 6200.0), S, '( is-event-true-delay "Wave 5" 0 )', 'ai-chase "Keplaw" 100', spacing=160.0, score=35)
    cw("Gale", "Advanced Raider", 6, (2800.0, 1200.0, -3200.0), S, '( is-event-true-delay "Wave 6" 0 )', "ai-chase-any 80", score=20)
    m.ship("Vulture", "Basestar", "Hostile", (-6000.0, -900.0, 9500.0), S, arrival='( is-event-true-delay "Wave 7" 0 )', ai_goals='ai-chase "Armistice" 90',
           ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    cw("Cull", "Raider", 6, (-5200.0, -700.0, 8200.0), S, '( is-event-true-delay "Wave 7" 10 )', "ai-chase-any 70")
    cw("Fall", "Heavy Raider", 5, (3600.0, 300.0, 5600.0), S, '( is-event-true-delay "Wave 7" 40 )', 'ai-chase "Pixie" 100', spacing=160.0, score=35)

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Armistice" "Allsop" "Keplaw" "Pixie" "Halyard" ) )')
    say(m, "Start", 2, "#Command", "A Orders", "Red flight, Armistice Station is the last port before the fleet. The movers load for thirty minutes and then jump, one by one. "
        "The Theseus is on her way, but she won't be here for twenty. Hold the station.")
    say(m, "Start", 20, "Allsop", "A Allsop", "Allsop, loading refugees. Two hundred and eighty, then I'm out. Thank you for being here.")
    say(m, "Start", 34, "Halyard", "A Halyard", "Halyard, taking position over the main docks. If they come for the station, they come through us.")
    m.event("Blue Cue", '( when ( is-event-true-delay "Start" 300 ) ( do-nothing ) )')
    phase(m, "Wave 1", "Start", 90)
    say(m, "Wave 1", 6, "Red 3", "A Snap", "Raiders, four of them, straight for Allsop. Cover the mover!")
    phase(m, "Wave 2", "Wave 1", 190, '( percent-ships-destroyed 75 "Snap" )')
    say(m, "Wave 2", 6, "Red 2", "A Talon", "Heavy Raiders on the dorsal side! They're going for the station itself!")
    phase(m, "Mover 1 Go", "Wave 2", 150, '( percent-ships-destroyed 75 "Talon" )')
    say(m, "Mover 1 Go", 2, "Allsop", "A Allsop Go", "Allsop is full! Jumping. Please keep the others safe.")
    phase(m, "Wave 3", "Mover 1 Go", 20)
    say(m, "Wave 3", 6, "Red 3", "A Wasp", "Advanced Raiders, five, from the sunward side! They're fast!")
    say(m, "Wave 3", 70, "Blue 1", "A Blue", "Ghost and Rook in the fight. Sorry we're late, Red leader.")
    phase(m, "Wave 4", "Wave 3", 210, '( percent-ships-destroyed 75 "Wasp" )')
    say(m, "Wave 4", 4, "#Command", "A Basestar", "DRADIS, basestar! One of theirs, dead ahead! Everyone, hold your positions!")
    say(m, "Wave 4", 40, "Keplaw", "A Keplaw", "Keplaw, loading at the lower docks. We saw the basestar. Two more minutes!")
    phase(m, "Mover 2 Go", "Wave 4", 220, '( percent-ships-destroyed 75 "Swarm" )')
    say(m, "Mover 2 Go", 2, "Keplaw", "A Keplaw Go", "Keplaw away! Thank you, Red flight. Two hundred more of us are alive.")
    phase(m, "Wave 5", "Mover 2 Go", 20)
    say(m, "Wave 5", 5, "Halyard", "A Hook", "Four Heavy Raiders breaking for the movers! Red flight, get on them!")
    phase(m, "Wave 6", "Wave 5", 180, '( percent-ships-destroyed 75 "Hook" )')
    say(m, "Wave 6", 5, "Red 2", "A Gale", "Six Advanced Raiders from the high side, that's their best wave yet.")
    phase(m, "Wave 7", "Wave 6", 200, '( percent-ships-destroyed 75 "Gale" )')
    say(m, "Wave 7", 4, "#Command", "A Vulture", "A second basestar! Armistice Station, hold on, Theseus is thirty seconds out!")
    phase(m, "Theseus In", "Wave 7", 30)
    say(m, "Theseus In", 4, "Theseus", "A Theseus", "Theseus on station! All batteries, firing! Red flight, you are not alone any more!")
    phase(m, "Mover 3 Go", "Theseus In", 120, '( percent-ships-destroyed 60 "Cull" "Fall" )')
    say(m, "Mover 3 Go", 2, "Pixie", "A Pixie Go", "Pixie is loaded, the last one. Jumping! Thank you, all of you.")
    m.message("A Win", "All three movers are away and the station still stands. The Theseus has the field. Outstanding work, Red flight. You held Armistice.")
    m.event("Win", '( when ( and ( has-departed-delay 2 "Allsop" ) ( has-departed-delay 2 "Keplaw" ) ( has-departed-delay 2 "Pixie" ) ( is-event-true-delay "Mover 3 Go" 120 ) ) ( send-message "#Command" "High" "A Win" ) )')
    win_end(m, "Win")
    m.message("A Lost", "Armistice Station is lost. Fall back to the fleet.")
    for n in ("Armistice", "Allsop", "Keplaw", "Pixie", "Halyard"):
        m.event("%s Lost" % n, '( when ( is-destroyed-delay 1 "%s" ) ( send-message "#Command" "High" "A Lost" ) )' % n)
    fail_end(m, ["Armistice Lost", "Allsop Lost", "Keplaw Lost", "Pixie Lost", "Halyard Lost"])

    m.goal("Primary", "Hold Armistice", "Keep the station and the three movers alive until the last has jumped", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Keep the Halyard", "The Halyard must survive", '( and ( is-event-true-delay "Win" 0 ) ( not ( is-destroyed-delay 0 "Halyard" ) ) )', 50)
    m.goal("Bonus", "Sink both basestars", "Destroy Ironhand and Vulture with the Theseus", '( and ( is-destroyed-delay 0 "Ironhand" ) ( is-destroyed-delay 0 "Vulture" ) )', 60)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Armistice Station held for half an hour. Seven hundred refugees are on their way to the fleet, and the Theseus is in the field.",
              "Every wave goes for a different target. Learn them and meet them early.")
    m.debrief('( or ( is-event-true-delay "Armistice Lost" 0 ) ( is-event-true-delay "Allsop Lost" 0 ) ( is-event-true-delay "Keplaw Lost" 0 ) ( is-event-true-delay "Pixie Lost" 0 ) ( is-event-true-delay "Halyard Lost" 0 ) )',
              "The station fell, and the people who were still aboard went with it.",
              "Kill the Heavy Raiders first. They go for the movers.")
    wreckage(m, "L", S, plates=9, spread=1700.0, seed=41, big="Wreck Carrier", big_at=(-4300.0, 600.0, 3900.0))
    return m


# ==============================================================================================================
def gunnery_range():
    """Gunnery qualification on the old Cylotron training drones (Mark IX and Mark X, as in the tutorial missions)."""
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Gunnery Qualification",
                "The Theseus's deck boss wants every pilot's gunnery on record. The Cylotron drones are out on the range: "
                "first a row of parked Mark IX targets, then Mark X drones on a run, then a fast pass. Nothing shoots back.",
                True)
    m.load_screen = "Load_SP-R1-M1.tga"
    m.background["sun_angles"] = "5.100000 2.200000 0.700000"
    m.player_wing("Red", (400.0, 100.0, -1500.0), (0.0, 0.0, 0.0), [], guard="ai-chase-any 50")
    idle = '( "cargo-known" "no-shields" "no-arrival-warp" "don\'t-collide-invisible" )'
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (0.0, 0.0, 0.0), (0.0, 0.0, 5000.0), arrival="( true )",
           flags=idle, flags2='( "immobile" )', shields=0, score=0)
    drone_flags = '( "cargo-known" "no-shields" "don\'t-collide-invisible" )'
    C = (2400.0, 0.0, 2000.0)
    for i in range(6):                                   # parked row of Mark IX drones
        pos = offset(C, (i - 2.5) * 260.0, ((i % 2) * 2 - 1) * 90.0, 0.0)
        m.ship("Target %d" % (i + 1), "Cylotron Mark IX Drone", "Neutral", pos, offset(pos, 0.0, 0.0, -3000.0),
               arrival="( true )", flags=drone_flags, flags2='( "immobile" )', hull=100, shields=0, score=10)
    m.waypoint_list("Run A", [(-2200.0, 300.0, 3600.0), (2600.0, 500.0, 4200.0), (2800.0, -300.0, 2400.0), (-1600.0, -200.0, 2200.0)])
    m.waypoint_list("Run B", [(3400.0, 200.0, 700.0), (700.0, 700.0, 2600.0), (-3000.0, 100.0, 4600.0)])
    m.event("Start", '( when ( true ) ( do-nothing ) )')
    say(m, "Start", 2, "#Command", "R Welcome", "Red 1, Theseus. Gunnery range is yours. Six Mark IX drones are parked on the far side. "
        "Kill them all, guns or missiles, I don't care which.")
    m.event("Row Done", '( when ( is-destroyed-delay 0 "Target 1" "Target 2" "Target 3" "Target 4" "Target 5" "Target 6" ) ( do-nothing ) )')
    say(m, "Row Done", 4, "#Command", "R Row", "Clean row. Next, six Mark X drones on a run. They don't dodge, but they don't hold still either. "
        "Lead them.")
    m.event("Runners Go", '( when ( is-event-true-delay "Row Done" 12 ) ( do-nothing ) )')
    for i in range(6):
        pos = offset((-2800.0, 100.0, 3200.0), i * 90.0, (i % 3) * 60.0, i * 70.0)
        m.ship("Runner %d" % (i + 1), "Cylotron Mark X Drone", "Neutral", pos, (2600.0, 500.0, 4200.0),
               arrival='( is-event-true-delay "Runners Go" 0 )', flags=drone_flags, hull=100, shields=0, score=10,
               ai_goals='ai-waypoints-once "Run A" 60', velocity=60)
    m.event("Runners Done", '( when ( is-destroyed-delay 0 "Runner 1" "Runner 2" "Runner 3" "Runner 4" "Runner 5" "Runner 6" ) ( do-nothing ) )')
    say(m, "Runners Done", 4, "#Command", "R Run", "Good shooting. Last pass: four drones at full throttle. If you can hit those you can hit a Raider.")
    m.event("Sprint Go", '( when ( is-event-true-delay "Runners Done" 12 ) ( do-nothing ) )')
    for i in range(4):
        pos = offset((3600.0, 250.0, 500.0), 0.0, i * 70.0, i * 110.0)
        m.ship("Sprint %d" % (i + 1), "Cylotron Mark X Drone", "Neutral", pos, (-3000.0, 100.0, 4600.0),
               arrival='( is-event-true-delay "Sprint Go" 0 )', flags=drone_flags, hull=100, shields=0, score=15,
               ai_goals='ai-waypoints-once "Run B" 80', velocity=90)
    m.event("Sprint Done", '( when ( is-destroyed-delay 0 "Sprint 1" "Sprint 2" "Sprint 3" "Sprint 4" ) ( do-nothing ) )')
    say(m, "Sprint Done", 4, "#Command", "R Done", "Range cleared. I'm logging that qualification. Come home whenever you like.")
    win_end(m, "Sprint Done")
    m.goal("Primary", "Parked drones", "Destroy the six Mark IX drones", '( is-event-true-delay "Row Done" 0 )', 100)
    m.goal("Primary", "Running drones", "Destroy the six Mark X drones on their run", '( is-event-true-delay "Runners Done" 0 )', 100)
    m.goal("Primary", "Fast pass", "Destroy the four sprinting drones", '( is-event-true-delay "Sprint Done" 0 )', 100)
    m.debrief('( is-event-true-delay "Sprint Done" 0 )',
              "Sixteen drones down, none of them shot back. Your gunnery is on the board.",
              "Nothing to fix. Come back any time to practise your lead.")
    return m


# ==============================================================================================================
def open_door():
    """Rescue that is a trap: the dead freighter Aurelia Dawn broadcasts a survivors' beacon, the Raptor goes in, and it is bait."""
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Open Door",
                "A freighter drifts dead on the edge of the Ravine, her beacon calling for rescue. The Raptor Lifeline goes in to "
                "take off her crew and Red flight goes with her. Command doesn't like how quiet the sector is.", TEST)
    m.load_screen = "Load_SP-R1-M2.tga"
    m.background["sun_angles"] = "2.600000 4.400000 0.900000"
    F = (0.0, 0.0, 6200.0)                                    # the derelict
    m.player_wing("Red", (-700.0, 200.0, -1200.0), F, ["Shadow", "Flask"], guard='ai-guard "Lifeline 1" 60')
    m.ship("Lifeline 1", "Raptor", "Friendly", (-120.0, 50.0, -400.0), F, arrival="( true )", ai_class="Lieutenant",
           flags='( "cargo-known" "no-shields" "escort" "don\'t-collide-invisible" )', hull=100, score=300,
           ai_goals='ai-waypoints-once "Approach" 70')
    m.waypoint_list("Approach", [(0.0, 0.0, 2600.0), offset(F, 0.0, 120.0, -520.0)])
    m.waypoint_list("Home", [(0.0, 0.0, -2800.0)])
    m.ship("Aurelia Dawn", "Gemenon Freighter", "Friendly", F, offset(F, 0.6, 0.1, 1.0), arrival="( true )",
           flags='( "invulnerable" "no-shields" "cargo-known" "don\'t-collide-invisible" )', score=0)
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (0.0, -400.0, -9000.0), (0.0, -400.0, 0.0), arrival="( true )",
           flags='( "cargo-known" "no-shields" "no-arrival-warp" "don\'t-collide-invisible" )', flags2='( "immobile" )',
           shields=0, score=0)
    wreckage(m, "R", F, plates=3, spread=900.0, seed=77)

    # the trap: three Raider groups and a basestar jump in once the Raptor has been sitting at the freighter for a while
    m.cylon_wing("Snare", "Raider", 4, (3000.0, 300.0, 8800.0), F, '( is-event-true-delay "Dock Wait" 28 )', 'ai-chase "Lifeline 1" 90')
    m.cylon_wing("Jaw", "Advanced Raider", 3, (-3200.0, -200.0, 8200.0), F, '( is-event-true-delay "Dock Wait" 40 )', 'ai-chase "Lifeline 1" 90', score=20)
    m.ship("Warden", "Basestar", "Hostile", (1500.0, 900.0, 11600.0), F, arrival='( is-event-true-delay "Dock Wait" 55 )',
           ai_goals='ai-chase "Lifeline 1" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Tail", "Raider", 4, (0.0, 200.0, -3800.0), F, '( is-event-true-delay "Blast" 20 )', 'ai-chase "Lifeline 1" 80')

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 25 "Lifeline 1" ) )')
    say(m, "Start", 2, "#Command", "O Orders", "Red flight, a freighter, the Aurelia Dawn, is drifting dead beyond the Ravine and says she has "
        "survivors aboard. Escort the Raptor Lifeline in, let her take them off and bring her home. Keep your eyes open, this is too easy.")
    say(m, "Start", 14, "Lifeline 1", "O Lifeline", "Lifeline one, rolling. Aurelia Dawn, we're coming. Hold on out there.")
    # the Raptor sits at the freighter for the pickup
    m.event("Dock Wait", '( when ( < ( distance "Lifeline 1" "Aurelia Dawn" ) 700 ) ( do-nothing ) )')
    say(m, "Dock Wait", 2, "Lifeline 1", "O Dock", "On station. No answer on the radio, but the beacon is strong. I'm opening the lock, give me ninety seconds.")
    say(m, "Dock Wait", 20, "Lifeline 1", "O Empty", "The ship is empty! No crew, no bodies, the beacon is a recording looped on a relay. It's a trap, get me out of here!")
    m.event("Leave", '( when ( is-event-true-delay "Dock Wait" 22 ) ( add-goal "Lifeline 1" ( ai-waypoints-once "Home" 90 ) ) )')
    say(m, "Dock Wait", 30, "Red 2", "O Snare", "Raiders jumping in on our six! They were waiting.")
    say(m, "Dock Wait", 55, "#Command", "O Warden", "DRADIS, basestar, bearing zero two zero! They baited the Raptor, Red flight, bring her home.")
    say(m, "Dock Wait", 62, "Lifeline 1", "O Reactor", "Red flight, the freighter's reactor is spooling up, the whole hull is rigged! Get clear!")
    # the freighter blows at 90 s: anything within 900 m goes with it. Order matters: the Raptor check runs before the hull dies.
    m.event("Blast Check", '( when ( and ( is-event-true-delay "Dock Wait" 90 ) ( < ( distance "Lifeline 1" "Aurelia Dawn" ) 900 ) ) ( destroy-instantly "Lifeline 1" ) )')
    m.event("Blast", '( when ( is-event-true-delay "Dock Wait" 90 ) ( destroy-instantly "Aurelia Dawn" ) )')
    m.event("Clear", '( when ( and ( is-event-true-delay "Blast" 40 ) ( < ( distance "Lifeline 1" "Red 1" ) 3000 ) ( percent-ships-destroyed 50 "Snare" ) ( percent-ships-destroyed 50 "Jaw" ) ( percent-ships-destroyed 50 "Tail" ) ) ( do-nothing ) )')
    m.message("O Win", "Lifeline is back under the Theseus' guns. You smelled that trap before the Cylons finished laying it. Well done, Red flight.")
    m.event("Win", '( when ( is-event-true-delay "Clear" 40 ) ( send-message "#Command" "High" "O Win" ) )')
    win_end(m, "Win")
    m.message("O Lost", "We lost Lifeline. Break off, Red flight.")
    m.event("Lifeline Lost", '( when ( is-destroyed-delay 1 "Lifeline 1" ) ( send-message "#Command" "High" "O Lost" ) )')
    fail_end(m, ["Lifeline Lost"])

    m.goal("Primary", "Take the Raptor to the freighter", "Escort Lifeline to the Aurelia Dawn", '( is-event-true-delay "Dock Wait" 0 )', 100)
    m.goal("Primary", "Bring Lifeline home", "Get the Raptor away before the freighter blows and back to the fleet", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Bonus", "Sink the Warden", "Destroy the baiting basestar", '( is-destroyed-delay 0 "Warden" )', 50)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "An empty freighter, a looped beacon, a rigged reactor and a basestar waiting on the far side. The Raptor made it back.",
              "When a distress call is too perfect, keep the Raptor moving the moment it reports the ship is empty.")
    m.debrief('( is-event-true-delay "Lifeline Lost" 0 )', "We lost the Raptor at the Aurelia Dawn.",
              "Once the freighter is declared empty, clear 900 m before the reactor goes: about a minute after the Raptor leaves.")
    return m


# ==============================================================================================================
def stand_fast():
    """Two civilian ships with cooked jump drives; a Bolitho frigate and three Assault Raptors jumped in to help. Hold until the Theseus arrives."""
    TEST, CIVIL, CAPITAL, win_end, fail_end = _setup()
    m = Mission("Stand Fast",
                "The freighter Hesper and the passenger liner Pilgrim Mercy made a bad jump and are dead in space with their drives "
                "cooked, eleven minutes from the Theseus. The Bolitho frigate Halyard and three Assault Raptors jumped in to help, but the Cylons "
                "found them first and they keep coming. Keep the Hesper and the Pilgrim Mercy alive until the battlestar jumps in.", TEST)
    m.load_screen = "Load_SP-R1-M3.tga"
    m.background["sun_angles"] = "4.200000 1.700000 1.100000"
    C = (0.0, 0.0, 0.0)
    m.player_wing("Red", (-900.0, 250.0, -1500.0), C, ["Shadow", "Flask"], guard="ai-chase-any 60")
    dead = '( "cargo-known" "no-arrival-warp" "don\'t-collide-invisible" )'
    m.ship("Hesper", "Gemenon Freighter", "Friendly", (-150.0, 0.0, 200.0), (0.0, 0.0, 3000.0), arrival="( true )", flags=CIVIL,
           flags2='( "immobile" )', hull=100, shields=0, score=0)
    m.ship("Pilgrim Mercy", "Intersun Passenger Cruiser", "Friendly", (450.0, -60.0, -100.0), (0.0, 0.0, 3000.0), arrival="( true )",
           flags=CIVIL, flags2='( "immobile" )', hull=100, shields=0, score=0)
    # the Bolitho frigate came to help: its drives work, it stays on the civilians and fights
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", (500.0, 150.0, 700.0), (500.0, 150.0, 3700.0), arrival="( true )", flags=dead,
           ai_goals='ai-guard "Pilgrim Mercy" 90', ai_class="Lieutenant", shields=100, score=0)
    # three Assault Raptors (more guns than the plain Raptor) for support, hugging the civilians
    raptor_flags = '( "cargo-known" "no-shields" "escort" "don\'t-collide-invisible" )'
    for name, pos, ward in [("Mender 1", (-30.0, 50.0, 330.0), "Hesper"), ("Mender 2", (-280.0, -30.0, 130.0), "Hesper"),
                            ("Mender 3", (330.0, -20.0, 20.0), "Pilgrim Mercy")]:
        m.ship(name, "Assault Raptor", "Friendly", pos, offset(pos, 0.0, 0.0, 3000.0), arrival="( true )", flags=raptor_flags,
               ai_goals='ai-guard "%s" 100' % ward, ai_class="Lieutenant", hull=100, shields=0, score=0)
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (400.0, -300.0, -9000.0), (200.0, -300.0, 0.0),
           arrival='( is-event-true-delay "Start" 660 )', ai_goals='ai-chase-any 100', flags='( "cargo-known" "no-shields" "don\'t-collide-invisible" )',
           shields=0, score=0)

    def friendly_wing(wname, callsigns, pos, arrival):
        names = []
        for i, cs in enumerate(callsigns):
            n = "%s %d" % (wname, i + 1)
            p = offset(pos, 70.0 * (i - (len(callsigns) - 1) / 2.0), 0.0, -30.0 * i)
            m.ship(n, "Viper Mark VII", "Friendly", p, C, arrival=arrival, flags='( "cargo-known" "don\'t-collide-invisible" )',
                   callsign=cs, ai_class="Lieutenant", primaries=["MEC-A6", "MEC-A6"],
                   secondaries=["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"])
            names.append(n)
        m.wing(wname, names, arrival, goals="ai-chase-any 60")
    # Green flight (six) is on station from the start, Blue flight (six) jumps in after four minutes
    friendly_wing("Green", ["Spike", "Brick", "Cutter", "Dagger", "Nail", "Pike"], (200.0, 350.0, -700.0), "( true )")
    friendly_wing("Blue", ["Ghost", "Rook", "Tango", "Mule", "Vigil", "Strut"], (-1300.0, 250.0, -2000.0), '( is-event-true-delay "Start" 240 )')

    # attack waves, all hunting the civilians first; positions around the group, one every 40 to 60 seconds
    m.cylon_wing("Scout", "Raider", 6, (3200.0, 300.0, 4200.0), C, '( is-event-true-delay "Start" 40 )', 'ai-chase "Hesper" 80')
    m.cylon_wing("Hunter", "Raider", 8, (-3600.0, -200.0, 3600.0), C, '( is-event-true-delay "Start" 95 )', 'ai-chase "Pilgrim Mercy" 80')
    m.cylon_wing("Hammer", "Heavy Raider", 4, (500.0, 900.0, 5200.0), C, '( is-event-true-delay "Start" 150 )', 'ai-chase "Hesper" 90', spacing=150.0, score=35)
    m.cylon_wing("Needle", "Advanced Raider", 6, (3800.0, 500.0, -2600.0), C, '( is-event-true-delay "Start" 205 )', 'ai-chase "Pilgrim Mercy" 90', score=20)
    m.cylon_wing("Swarm", "Raider", 8, (-3400.0, 200.0, -3000.0), C, '( is-event-true-delay "Start" 260 )', 'ai-chase "Hesper" 70')
    m.cylon_wing("Fang", "Raider", 6, (0.0, -600.0, 4800.0), C, '( is-event-true-delay "Start" 315 )', 'ai-chase "Pilgrim Mercy" 80')
    m.cylon_wing("Talon", "Heavy Raider", 4, (-1500.0, 1000.0, 5600.0), C, '( is-event-true-delay "Start" 370 )', 'ai-chase "Hesper" 90', spacing=150.0, score=35)
    m.ship("Anvil", "Basestar", "Hostile", (1800.0, 1200.0, 9000.0), C, arrival='( is-event-true-delay "Start" 400 )',
           ai_goals='ai-chase "Halyard" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Reaper", "Advanced Raider", 6, (3600.0, 400.0, 3000.0), C, '( is-event-true-delay "Start" 430 )', 'ai-chase "Pilgrim Mercy" 90', score=20)
    m.cylon_wing("Wave", "Raider", 10, (-3000.0, 100.0, 4000.0), C, '( is-event-true-delay "Start" 490 )', "ai-chase-any 60")
    m.cylon_wing("Last", "Raider", 8, (2600.0, -300.0, -3400.0), C, '( is-event-true-delay "Start" 560 )', 'ai-chase "Hesper" 70')

    m.event("Start", '( when ( true ) ( do-nothing ) )')
    say(m, "Start", 2, "#Command", "S Orders", "Red flight, the Hesper and the Pilgrim Mercy made a bad jump and are dead in space. Halyard jumped in to cover them "
        "with three assault Raptors and Green flight. The Theseus is eleven minutes out. Hold the line and keep the civilians alive.")
    say(m, "Start", 14, "Halyard", "S Halyard", "Halyard to Red flight, we jumped in as soon as we got their call. We can't tow them, we can only guard them. Stay close.")
    say(m, "Start", 40, "Halyard", "S Scouts", "Contacts, six Raiders, bearing zero three zero. They're going for the Hesper!")
    say(m, "Start", 24, "Mender 1", "S Menders", "Mender one, three assault Raptors on station. We're sitting right on the civilians, nobody gets a clear shot at them without going through us.")
    say(m, "Start", 95, "Pilgrim Mercy", "S Mercy", "Pilgrim Mercy! There are eight more coming at us from the port side! We have three hundred people aboard!")
    say(m, "Start", 130, "#Command", "S Eight", "Theseus to Red flight, eight minutes. Hang on.")
    say(m, "Start", 150, "Halyard", "S Heavies", "Heavy Raiders high above us! Concentrate fire, don't let them reach the passenger liner.")
    say(m, "Start", 205, "Red 2", "S Needles", "Advanced Raiders from the rear! They're fast, stay on them!")
    say(m, "Start", 240, "#Command", "S Blue", "Blue flight is jumping in to reinforce you. Five minutes, Red flight.")
    say(m, "Start", 315, "Halyard", "S Fang", "Another wave from below, there's no end to them!")
    say(m, "Start", 400, "#Command", "S Basestar", "DRADIS, basestar, bearing one four zero! It's hunting the Halyard. Four minutes, Red flight.")
    say(m, "Start", 560, "#Command", "S Last", "Last wave coming in. One hundred seconds to the Theseus!")
    say(m, "Start", 660, "Theseus", "S Theseus", "Theseus is here! All guns, open fire. Red flight, well held.")
    m.event("Cleared", '( when ( and ( is-event-true-delay "Start" 700 ) ( percent-ships-destroyed 60 "Wave" ) ( percent-ships-destroyed 60 "Last" ) ( percent-ships-destroyed 60 "Hunter" ) ) ( do-nothing ) )')
    m.message("S Win", "The Cylons are breaking off and the Hesper and the Pilgrim Mercy are alive. The fleet owes you a drink, Red flight.")
    m.event("Win", '( when ( is-event-true-delay "Cleared" 25 ) ( send-message "#Command" "High" "S Win" ) )')
    win_end(m, "Win")
    m.message("S Lost1", "We lost the Hesper. Break off, Red flight.")
    m.message("S Lost2", "We lost the Pilgrim Mercy. Break off, Red flight.")
    m.event("Hesper Lost", '( when ( is-destroyed-delay 1 "Hesper" ) ( send-message "#Command" "High" "S Lost1" ) )')
    m.event("Mercy Lost", '( when ( is-destroyed-delay 1 "Pilgrim Mercy" ) ( send-message "#Command" "High" "S Lost2" ) )')
    fail_end(m, ["Hesper Lost", "Mercy Lost"])

    m.goal("Primary", "Protect the Hesper", "Keep the freighter alive until the Theseus arrives", '( and ( is-event-true-delay "Win" 0 ) ( not ( is-destroyed-delay 0 "Hesper" ) ) )', 100)
    m.goal("Primary", "Protect the Pilgrim Mercy", "Keep the passenger liner alive until the Theseus arrives", '( and ( is-event-true-delay "Win" 0 ) ( not ( is-destroyed-delay 0 "Pilgrim Mercy" ) ) )', 100)
    m.goal("Bonus", "Keep the Halyard", "The Bolitho frigate must survive", '( and ( is-event-true-delay "Win" 0 ) ( not ( is-destroyed-delay 0 "Halyard" ) ) )', 50)
    m.goal("Bonus", "Sink the Anvil", "Destroy the hunting basestar", '( is-destroyed-delay 0 "Anvil" )', 50)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Eleven minutes, eleven waves and a basestar, and both civilian ships are still in one piece. The Halyard took the worst of it.",
              "Kill the Heavy Raiders first, they are the only wave that can hurt the Halyard.")
    m.debrief('( or ( is-event-true-delay "Hesper Lost" 0 ) ( is-event-true-delay "Mercy Lost" 0 ) )', "A civilian ship was lost before the Theseus came.",
              "The Raiders go for the civilians first: put Red flight between each wave and its target.")
    return m
