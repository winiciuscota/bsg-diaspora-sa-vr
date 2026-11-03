#!/usr/bin/env python3
"""Generates the sample mission "Vigil at the Ashen Veil" (XM-Vigil.fs2) for the Diaspora overlay mod.

Story (invented for this sample, set in the Diaspora fleet):
  Eleven hours after the first strikes, the refugee transport Pilgrim Mercy (212 souls out of Gemenon Heights
  colony) fell out of FTL inside the Ashen Veil nebula with a cracked drive and went dark. Battlestar Theseus
  sends Red flight (72nd Thunderlords) to hold the nebula while Raptor Gleaner 1 ferries the survivors off and
  the Mercy's engineers coax the drive back to life. The Cylons have been shadowing the transport and are not
  going to let her leave.

Usage: python3 -I tools/make_vigil.py OUT.fs2 [--test]   (--test makes the player invulnerable, for unattended runs)
"""
import math
import sys

NL = "\r\n"
out = []


def w(s=""):
    out.append(s)


def norm(v):
    m = math.sqrt(sum(c * c for c in v))
    return tuple(c / m for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def orient(src, dst):
    """3x3 orientation (right, up, forward rows) for an object at src facing dst."""
    f = norm(tuple(d - s for s, d in zip(src, dst)))
    up_hint = (0.0, 1.0, 0.0) if abs(f[1]) < 0.95 else (0.0, 0.0, 1.0)
    r = norm(cross(up_hint, f))
    u = cross(f, r)
    return r, u, f


def fmt3(v):
    return "%.6f, %.6f, %.6f" % v


def xstr(text):
    return 'XSTR("%s", -1)' % text.replace('"', "'")


# --------------------------------------------------------------------------------------------------------------
# geometry (meters). The Pilgrim Mercy sits at the origin.
MERCY = (0.0, 0.0, 0.0)
RED_START = (0.0, 40.0, -2800.0)
RED_FACE = (2200.0, 0.0, 400.0)   # beside the cruiser, so a hands-off player drifts past instead of ramming it
GLEANER_IN = (-3200.0, 300.0, -3600.0)
ALPHA_IN = (3500.0, -400.0, 2500.0)
BRAVO_IN = (-3000.0, 800.0, 3000.0)
CHARLIE_IN = (200.0, 1500.0, 3800.0)
PYRE_IN = (4500.0, 700.0, 6500.0)

objects = []


def ship(name, cls, team, pos, face, extra=None, arrival="( false )", departure="( false )", ai_goals=None,
         flags='( "cargo-known" )', flags2="( )", hull=100, shields=100, callsign=None, ai_class=None, velocity=None,
         primaries=None, secondaries=None, score=10):
    o = []
    o.append("$Name: %s" % name)
    o.append("$Class: %s" % cls)
    if callsign:
        o.append("$Callsign: %s" % callsign)
        o.append("")
    o.append("$Team: %s" % team)
    o.append("$Location: %s" % fmt3(pos))
    r, u, f = orient(pos, face)
    o.append("$Orientation:")
    o.append("\t%s," % fmt3(r))
    o.append("\t%s," % fmt3(u))
    o.append("\t%s" % fmt3(f))
    o.append("$AI Behavior: None")
    if ai_class:
        o.append("+AI Class: %s" % ai_class)
    if ai_goals:
        o.append("$AI Goals: ( goals ( %s ) )" % ai_goals)
    o.append('$Cargo 1:  XSTR("Nothing", 150)')
    if velocity:
        o.append("+Initial Velocity: %d" % velocity)
    o.append("+Initial Hull: %d" % hull)
    o.append("+Initial Shields: %d" % shields)
    o.append("+Subsystem: Pilot")
    if primaries:
        o.append("+Primary Banks: ( %s )" % " ".join('"%s"' % p for p in primaries))
    if secondaries:
        o.append("+Secondary Banks: ( %s )" % " ".join('"%s"' % p for p in secondaries))
    o.append("$Arrival Location: Hyperspace")
    o.append("$Arrival Cue: %s" % arrival)
    o.append("$Departure Location: Hyperspace")
    o.append("$Departure Cue: %s" % departure)
    o.append("$Determination: 10")
    o.append("+Flags: %s" % flags)
    o.append("+Flags2: %s" % flags2)
    o.append("+Respawn priority: 0")
    o.append("+Orders Accepted: 0\t\t;! note that this is a bitfield!!!")
    o.append("+Group: 0")
    o.append("+Use Table Score:")
    o.append("+Score: %d" % score)
    objects.append(o)


viper_guns = ["MEC-A6", "MEC-A6"]
viper_missiles = ["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"]
TEST = '--test' in sys.argv
args_out = [a for a in sys.argv[1:] if not a.startswith('--')]
player_flags = '( "cargo-known" "player-start" "don\'t-collide-invisible"%s )' % (' "invulnerable"' if TEST else '')
wing_flags = '( "cargo-known" "don\'t-collide-invisible" )'

ship("Red 1", "Viper Mark VII", "Friendly", RED_START, RED_FACE, flags=player_flags, primaries=viper_guns,
     secondaries=viper_missiles, score=12)
ship("Red 2", "Viper Mark VII", "Friendly", (-60.0, 40.0, -2790.0), RED_FACE, flags=wing_flags, callsign="Shadow",
     ai_class="Lieutenant", primaries=viper_guns, secondaries=viper_missiles)
ship("Red 3", "Viper Mark VII", "Friendly", (60.0, 40.0, -2790.0), RED_FACE, flags=wing_flags, callsign="Flask",
     ai_class="Lieutenant", primaries=viper_guns, secondaries=viper_missiles)

ship("Pilgrim Mercy", "Intersun Passenger Cruiser", "Friendly", MERCY, (0.0, 0.0, -1000.0),
     arrival="( true )", departure='( is-event-true-delay "Mercy Spool" 70 )',
     ai_goals="ai-play-dead 100", hull=60, shields=0, flags='( "cargo-known" "no-shields" "no-arrival-warp" )',
     score=500)

ship("Gleaner 1", "Raptor", "Friendly", GLEANER_IN, MERCY, ai_goals='ai-waypoints-once "Gleaner Run" 90',
     arrival='( is-event-true-delay "Start" 70 )', departure='( is-event-true-delay "Transfer Done" 8 )',
     ai_class="Lieutenant", flags='( "cargo-known" "no-arrival-message" )', score=100, velocity=60)

for i in range(1, 5):
    off = (i - 2.5) * 70.0
    ship("Alpha %d" % i, "Raider", "Hostile", (ALPHA_IN[0] + off, ALPHA_IN[1], ALPHA_IN[2] + off), MERCY,
         ai_class="Lieutenant", flags='( "no-shields" "no-arrival-warp" )', flags2='( "no-ets" )', velocity=33)
for i in range(1, 4):
    off = (i - 2) * 80.0
    ship("Bravo %d" % i, "Advanced Raider", "Hostile", (BRAVO_IN[0] + off, BRAVO_IN[1], BRAVO_IN[2] - off), MERCY,
         ai_class="Lieutenant", flags='( "no-shields" "no-arrival-warp" )', flags2='( "no-ets" )', velocity=33,
         score=20)
for i in range(1, 3):
    off = (i - 1.5) * 120.0
    ship("Charlie %d" % i, "Heavy Raider", "Hostile", (CHARLIE_IN[0] + off, CHARLIE_IN[1], CHARLIE_IN[2]), MERCY,
         ai_class="Lieutenant", flags='( "no-shields" "no-arrival-warp" )', flags2='( "no-ets" )', velocity=33,
         score=35)

ship("Pyre", "Basestar", "Hostile", PYRE_IN, MERCY, ai_goals='ai-chase "Pilgrim Mercy" 60',
     arrival='( is-event-true-delay "Transfer Done" 28 )', ai_class="Lieutenant",
     flags='( "no-arrival-message" "hidden-from-sensors" )', score=1000)
# Pyre must show up on DRADIS so the player sees it: drop the hidden flag again
objects[-1] = [l.replace(' "hidden-from-sensors"', "") for l in objects[-1]]

# --------------------------------------------------------------------------------------------------------------
messages = [
    ("HQ Orders", "Red flight, Theseus. The pilgrim ship Pilgrim Mercy fell out of FTL inside the Ashen Veil eleven hours ago and went dark. "
     "Two hundred and twelve civilians from Gemenon Heights are aboard and her drive is cracked. Gleaner 1 is jumping in to take them off. "
     "Hold the Veil and keep that Raptor alive."),
    ("Mercy Hail", "Red flight, this is Captain Ilyra Voss of the Pilgrim Mercy. Thank the Lords. Our engines are slag and the shields are gone, "
     "but the chief thinks she can nurse the drive back if you give her a few minutes."),
    ("S Contacts", "Contacts, Red Leader! Raiders, coming in off the Veil. Gods, they were waiting for us."),
    ("F Count", "I count four. They're ignoring us, they're heading straight for the cruiser."),
    ("Gleaner Arrive", "Gleaner 1 on approach. Two minutes to dock and load. Somebody keep the Cylons off my back."),
    ("Gleaner Dock", "Docked. Loading civilians now, this is going to take a minute."),
    ("S Advanced", "More Raiders! These are fast, advanced models. Keep them off the Raptor."),
    ("Gleaner Done", "That's everyone, two hundred and twelve, babies and all. Undocking. Mercy, spool your FTL and go."),
    ("Mercy Spool", "Spooling the drive. Seventy seconds, give or take. Don't let them touch us."),
    ("S Heavy", "Heavy Raiders, two o'clock high! They're going for the engines."),
    ("HQ Basestar", "Red flight, DRADIS shows a basestar jumping in at the edge of the Veil. Your window is closing."),
    ("Mercy Jump", "Jumping! The Lords watch over you, Thunderlords."),
    ("HQ Win", "The Mercy is clear and on her way to the fleet. Outstanding work, Red flight. Come on home."),
    ("HQ Mercy Lost", "We've lost the Mercy. Gods help them. Break off and return to Theseus, Red flight."),
    ("HQ Gleaner Lost", "Gleaner 1 is down. Without her the Mercy is stranded. Abort and return to Theseus."),
]

events = []


def event(name, formula, chained=None):
    events.append((name, formula, chained))


# The Mercy cannot be killed outright early on (guardian threshold 25 %), so a slow reaction costs hull, not the mission.
# The cushion is taken away 30 s into the FTL spool, when the heavy raiders arrive (never in the --test variant).
event("Start", "( when ( true ) ( ship-guardian-threshold 25 \"Pilgrim Mercy\" ) )")
event("Briefing Msg", '( when ( is-event-true-delay "Start" 3 ) ( send-message "#Command" "High" "HQ Orders" ) )')
event("Mercy Hail Msg", '( when ( is-event-true-delay "Briefing Msg" 22 ) ( send-message "Pilgrim Mercy" "High" "Mercy Hail" ) )')
event("Alpha Cue", '( when ( is-event-true-delay "Mercy Hail Msg" 14 ) ( do-nothing ) )')
event("Alpha Msg", '( when ( has-arrived-delay 4 "Alpha" ) ( send-message "Red 2" "High" "S Contacts" ) )')
event("Alpha Msg 2", '( when ( has-arrived-delay 10 "Alpha" ) ( send-message "Red 3" "High" "F Count" ) )')
event("Gleaner Arrive Msg", '( when ( has-arrived-delay 2 "Gleaner 1" ) ( send-message "Gleaner 1" "High" "Gleaner Arrive" ) )')
event("Gleaner On Station", '( when ( is-event-true-delay "Start" 130 ) ( send-message "Gleaner 1" "High" "Gleaner Dock" ) )')
event("Bravo Cue", '( when ( is-event-true-delay "Gleaner On Station" 8 ) ( do-nothing ) )')
event("Bravo Msg", '( when ( has-arrived-delay 4 "Bravo" ) ( send-message "Red 2" "High" "S Advanced" ) )')
event("Transfer Done", '( when ( is-event-true-delay "Gleaner On Station" 75 ) ( send-message "Gleaner 1" "High" "Gleaner Done" ) )')
event("Mercy Spool", '( when ( is-event-true-delay "Transfer Done" 4 ) ( send-message "Pilgrim Mercy" "High" "Mercy Spool" ) )')
if not TEST:
    event("Guard Off", '( when ( is-event-true-delay "Mercy Spool" 30 ) ( ship-no-guardian "Pilgrim Mercy" ) )')
event("Charlie Cue", '( when ( is-event-true-delay "Transfer Done" 14 ) ( do-nothing ) )')
event("Charlie Msg", '( when ( has-arrived-delay 4 "Charlie" ) ( send-message "Red 2" "High" "S Heavy" ) )')
event("Pyre Msg", '( when ( has-arrived-delay 3 "Pyre" ) ( send-message "#Command" "High" "HQ Basestar" ) )')
event("Mercy Jump Msg", '( when ( is-event-true-delay "Mercy Spool" 66 ) ( send-message "Pilgrim Mercy" "High" "Mercy Jump" ) )')
event("Win", '( when ( has-departed-delay 3 "Pilgrim Mercy" ) ( send-message "#Command" "High" "HQ Win" ) )')
event("Fade out", '( when ( is-event-true-delay "Win" 7 ) ( fade-out 1000 ) )')
event("Finish", '( when ( is-event-true-delay "Fade out" 2 ) ( end-mission ) )')
event("Mercy Lost", '( when ( is-destroyed-delay 1 "Pilgrim Mercy" ) ( send-message "#Command" "High" "HQ Mercy Lost" ) )')
event("Gleaner Lost", '( when ( is-destroyed-delay 1 "Gleaner 1" ) ( send-message "#Command" "High" "HQ Gleaner Lost" ) )')
event("Fail Fade", '( when ( or ( is-event-true-delay "Mercy Lost" 8 ) ( is-event-true-delay "Gleaner Lost" 8 ) ) ( fade-out 1000 ) )')
event("Fail End", '( when ( is-event-true-delay "Fail Fade" 2 ) ( end-mission ) )')

# wings -------------------------------------------------------------------------------------------------------
wings = [
    dict(name="Red", ships=["Red 1", "Red 2", "Red 3"], arrival="( true )", departure="( false )",
         goals='ai-guard "Pilgrim Mercy" 60', flags='( "no-arrival-music" "no-arrival-message" "no-arrival-warp" )'),
    dict(name="Alpha", ships=["Alpha %d" % i for i in range(1, 5)], arrival='( is-event-true-delay "Alpha Cue" 0 )',
         departure="( false )", goals="ai-chase-any 50", flags='( "no-arrival-music" "no-arrival-message" "no-arrival-warp" )'),
    dict(name="Bravo", ships=["Bravo %d" % i for i in range(1, 4)], arrival='( is-event-true-delay "Bravo Cue" 0 )',
         departure="( false )", goals='ai-chase "Pilgrim Mercy" 70', flags='( "no-arrival-music" "no-arrival-message" "no-arrival-warp" )'),
    dict(name="Charlie", ships=["Charlie %d" % i for i in range(1, 3)], arrival='( is-event-true-delay "Charlie Cue" 0 )',
         departure="( false )", goals='ai-chase "Pilgrim Mercy" 90', flags='( "no-arrival-music" "no-arrival-message" "no-arrival-warp" )'),
]

# --------------------------------------------------------------------------------------------------------------
w("#Mission Info")
w()
w('$Version: 0.10')
w('$Name:  %s' % xstr("Vigil at the Ashen Veil"))
w("$Author: Claude (sample mission for the Diaspora port)")
w("$Created: 11/01/26 at 23:00:00")
w("$Modified: 11/01/26 at 23:00:00")
w("$Notes:")
w("Sample mission generated by tools/make_vigil.py (non-commercial, CC BY-NC-SA with the Diaspora content).")
w("$End Notes:")
w()
w("$Mission Desc:")
w(" %s" % xstr(
    "Eleven hours after the first strikes the refugee ship Pilgrim Mercy, 212 civilians from Gemenon Heights, fell out of FTL inside the "
    "Ashen Veil with a cracked drive. Hold the nebula while the Raptor Gleaner 1 takes the survivors off and the Mercy's engineers "
    "coax the drive back to life."))
w("$end_multi_text")
w()
w("+Game Type Flags: 1")
w()
w("+Flags: 262144")
w("+Fog Near Mult: 1.000000")
w()
w("+Fog Far Mult: 1.000000")
w()
w("+Disallow Support: 1")
w()
w("+Hull Repair Ceiling: 0.000000")
w()
w("+Subsystem Repair Ceiling: 100.000000")
w()
w("+Viewer pos: 0.000000, 0.000000, -3000.000000")
w("+Viewer orient:")
w("\t1.000000, 0.000000, 0.000000,")
w("\t0.000000, 1.000000, 0.000000,")
w("\t0.000000, 0.000000, 1.000000")
w("+SquadReassignName: 72nd Thunderlords")
w("+SquadReassignLogo: thunderlords.pcx")
w()
w('$Starting wing names: ( "Red" )')
w('$Squadron wing names: ( "Red" "Orange" "Violet" "Blue" "Green" )')
w('$Team-versus-team wing names: ( "Red" "Orange" )')
w()
w("$Load Screen 640:\tY_No_1024x768.tga")
w("$Load Screen 1024:\tLoad_SP-R1-M4.tga")
w()
w("$Skybox Model: SkyBox_Starfield_01.pof")
w()
w("$AI Profile: Diaspora_default")
w()
w("#Sexp_variables")
w()
w("$Variables:")
w("(")
w(")")
w()
w("#Cutscenes")
w()
w("#end")
w()
w("#Command Briefing")
w()
w("#Briefing")
w("$start_briefing")
w("$num_stages: 0")
w("$end_briefing")
w()
w("#Debriefing_info")
w()
w("$Num stages: 3")
w()
debriefs = [
    ('( is-event-true-delay "Win" 0 )',
     "Two hundred and twelve people are alive because you held the Veil. Captain Voss has already asked which squadron to thank. "
     "The Pilgrim Mercy reaches the fleet tomorrow, and the Cylon basestar will not be reaching anyone for a while. Well done, Thunderlords.",
     "Raiders go for the engines first. Shoot them off the cruiser's tail before they get a lock."),
    ('( is-event-true-delay "Mercy Lost" 0 )',
     "We lost the Mercy and everyone aboard her. The Cylons knew exactly where she was and they were patient. Learn from it. We cannot afford to lose another one.",
     "Stay between the raiders and the cruiser. Use your missiles on the Heavy Raiders, they absorb a lot of cannon fire."),
    ('( is-event-true-delay "Gleaner Lost" 0 )',
     "Gleaner 1 never made it out and the Mercy is stranded in the Veil without her. The Raptor is the only way those civilians were getting off that ship.",
     "Intercept the first raider wave early, before the Raptor arrives. She has no guns."),
]
for formula, text, rec in debriefs:
    w("$Formula: %s" % formula)
    w("$Multi text")
    w("    %s" % xstr(text))
    w("$end_multi_text")
    w("$Voice: none")
    w("$Recommendation text:")
    w("    %s" % xstr(rec))
    w("$end_multi_text")
    w()
w("#Callsigns:")
for c in ["Shadow", "Flask", "Courier"]:
    w("$Callsign: %s" % c)
w()
w("#end")
w()
w()
w("#Players\t\t;! 1 total")
w()
w("$Starting Shipname: Red 1")
w("$Ship Choices: (")
w(")")
w()
w("+Weaponry Pool: (")
w('\t"MEC-A6"\t26')
w('\t"HD-70 Lightning Javelin"\t112')
w('\t"HD-51 Arbalest"\t32')
w(")")
w()
w("#Objects\t\t;! %d total" % len(objects))
w()
for i, o in enumerate(objects):
    o[0] += "\t\t;! Object #%d" % i
    for l in o:
        w(l)
    w()
w("#Wings\t\t;! %d total" % len(wings))
w()
for wing in wings:
    w("$Name: %s" % wing["name"])
    w("$Waves: 1")
    w("$Wave Threshold: 0")
    w("$Special Ship: 0\t\t;! %s 1" % wing["name"])
    w()
    w("$Arrival Location: Hyperspace")
    w("$Arrival Cue: %s" % wing["arrival"])
    w("$Departure Location: Hyperspace")
    w("$Departure Cue: %s" % wing["departure"])
    w("$Ships: (\t\t;! %d total" % len(wing["ships"]))
    for s in wing["ships"]:
        w('\t"%s"' % s)
    w(")")
    w("$AI Goals: ( goals ( %s ) )" % wing["goals"])
    w("+Flags: %s" % wing["flags"])
    w()
w("#Events\t\t;! %d total" % len(events))
w()
for name, formula, chained in events:
    w("$Formula: %s" % formula)
    w("+Name: %s" % name)
    w("+Repeat Count: 1")
    w("+Interval: 1")
    w()
w("#Goals\t\t;! 3 total")
w()
goals = [
    ("Primary", "Protect Pilgrim Mercy", "Protect the Pilgrim Mercy until she jumps", '( is-event-true-delay "Win" 0 )', 100),
    ("Primary", "Escort Gleaner 1", "Keep Gleaner 1 alive while she loads the survivors", '( is-event-true-delay "Transfer Done" 0 )', 100),
    ("Secondary", "Destroy Raiders", "Destroy the Cylon raiders", '( percent-ships-destroyed 75 "Alpha" "Bravo" "Charlie" )', 50),
]
for typ, name, text, formula, score in goals:
    w("$Type: %s" % typ)
    w("+Name: %s" % name)
    w("$MessageNew:  %s" % xstr(text))
    w("$end_multi_text")
    w("$Formula: %s" % formula)
    w("+Score: %d" % score)
    w()
w("#Waypoints\t\t;! 1 lists total")
w()
w("$Name: Gleaner Run")
w("$List: (\t\t;! 3 points in list")
w("\t( -2000.000000, 150.000000, -2400.000000 )")
w("\t( -900.000000, 60.000000, -900.000000 )")
w("\t( -260.000000, 20.000000, -220.000000 )")
w(")")
w()
w("#Messages\t\t;! %d total" % len(messages))
w()
w("$Command Sender: Theseus")
w()
for name, text in messages:
    w("$Name: %s" % name)
    w("$Team: -1")
    w("$MessageNew:  %s" % xstr(text))
    w("$end_multi_text")
    w()
w("#Reinforcements\t\t;! 0 total")
w()
w()
w("#Background bitmaps\t\t;! 3 total")
w()
w("$Num stars: 0")
w("$Ambient light level: 8947070")
w()
w("$Bitmap List:")
w("$Sun: Stars_Sun_YHaze")
w("+Angles: 0.174533 5.689769 4.014254")
w("+Scale: 8.000000")
for name, angles, sx, sy in [("Stars_Neb_Blue02", "0.000000 5.497783 0.872664", 8, 8),
                             ("Stars_Neb_Blue03", "5.672316 5.916661 1.134463", 8, 6),
                             ("Stars_Neb_Blue01", "0.575958 0.000000 0.733038", 6, 8)]:
    w("$Starbitmap: %s" % name)
    w("+Angles: %s" % angles)
    w("+ScaleX: %f" % sx)
    w("+ScaleY: %f" % sy)
    w("+DivX: 1")
    w("+DivY: 1")
w()
w("#Asteroid Fields")
w()
w("#Music")
w()
w("$Event Music: 10: Children of Humanity")
w("$Briefing Music: Brief11")
w()
w("#End")

with open(args_out[0], "wb") as f:
    f.write((NL.join(out) + NL).encode("latin-1"))
print("wrote", args_out[0], len(objects), "objects", len(events), "events", len(messages), "messages")
