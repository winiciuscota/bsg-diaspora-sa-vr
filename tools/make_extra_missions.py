#!/usr/bin/env python3
"""Generates the extra single-player missions of the Diaspora overlay mod (invented for the port, set in the
Diaspora fleet after the first strikes) and the "Thunderlords Patrol Log" campaign that strings them together
with the sample mission XM-Vigil.

  XM-Tylium.fs2     Tylium Run       escort a fuel convoy (Prometheus tanker + Gemenon freighter, Bolitho escort)
  XM-Hollow.fs2     Hollow Rock      find a mining mover in an asteroid field and stop the Cylon boarding party
  XM-Shepherd.fs2   Iron Shepherd    escort the Bolitho frigate Halyard and two refugee liners through an asteroid belt
  XM-Reckoning.fs2  Dead Reckoning   scan drifting cargo pods for antibiotics, protect the Raptor that recovers it
  XM-Station.fs2    Station Keeping  the Halyard guards three Colonial Movers evacuating the Armistice Station
  XM-DeepLook.fs2   Deep Look        fly a Raptor in to scan a dormant basestar and get out when it wakes up
  XM-Firebreak.fs2  Firebreak        hold the line while Theseus repairs her FTL, a basestar joins late
  XM-Hunter.fs2     Hunter's Moon    the Halyard is bait for a Cylon raiding group, Red flight springs the trap
  XM-Fleet.fs2      Fleet Anchorage  peaceful free flight around the fleet (invulnerable, nothing to fail)
  XM-Anvil.fs2      Hammer and Anvil with the Halyard as the anvil, kill six nuke-armed Heavy Raiders before they jump

Usage: python3 -I tools/make_extra_missions.py OUTDIR [--test]   (--test makes the player invulnerable)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fsmission import Mission, offset, CYLON_FLAGS  # noqa: E402

TEST = "--test" in sys.argv
OUT = [a for a in sys.argv[1:] if not a.startswith("--")][0]
CIVIL_FLAGS = '( "cargo-known" "no-shields" "escort" "no-arrival-warp" "don\'t-collide-invisible" )'
CAPITAL_FLAGS = '( "cargo-known" "no-shields" "escort" "no-arrival-warp" "don\'t-collide-invisible" )'


def fail_end(m, events):
    """Fade out and end the mission a few seconds after any of the given events."""
    conds = ['( is-event-true-delay "%s" 8 )' % e for e in events]
    cond = conds[0] if len(conds) == 1 else "( or %s )" % " ".join(conds)    # "or" needs at least two arguments
    m.event("Fail Fade", "( when %s ( fade-out 1000 ) )" % cond)
    m.event("Fail End", '( when ( is-event-true-delay "Fail Fade" 2 ) ( end-mission ) )')


def win_end(m, after):
    m.event("Fade out", '( when ( is-event-true-delay "%s" 7 ) ( fade-out 1000 ) )' % after)
    m.event("Finish", '( when ( is-event-true-delay "Fade out" 2 ) ( end-mission ) )')


# ==============================================================================================================
def tylium_run():
    m = Mission("Tylium Run",
                "The fleet is down to its last reserves of tylium. The tanker Cassia and the freighter Hesper are bringing "
                "refined fuel from the Ragnar refinery to the jump point, with the frigate Halyard riding shotgun. "
                "Red flight escorts them across the last nine kilometres. The Cylons know what that fuel means.",
                TEST)
    m.load_screen = "Load_SP-R1-M5.tga"
    CASSIA, HESPER, HALYARD = (0.0, 0.0, 0.0), (-450.0, 120.0, -300.0), (350.0, -80.0, -600.0)
    END = (300.0, 200.0, 9000.0)
    m.player_wing("Red", (0.0, 300.0, -1800.0), END, ["Shadow", "Flask"], guard='ai-guard "Cassia" 60')

    jump = '( is-event-true-delay "Convoy Jump" 12 )'
    m.ship("Cassia", "Prometheus", "Friendly", CASSIA, END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Convoy Lane" 90', flags=CIVIL_FLAGS, hull=100, shields=0, score=400,
           cargo="Tylium")
    m.ship("Hesper", "Gemenon Freighter", "Friendly", HESPER, END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Convoy Lane" 90', flags=CIVIL_FLAGS, hull=100, shields=0, score=300,
           cargo="Tylium")
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", HALYARD, END, arrival="( true )", departure=jump,
           ai_goals='ai-guard "Cassia" 80', flags=CAPITAL_FLAGS, shields=0, score=500)
    m.waypoint_list("Convoy Lane", [(0.0, 0.0, 1500.0), (500.0, 150.0, 4500.0), (300.0, 200.0, 8500.0)])

    m.cylon_wing("Jackal", "Raider", 4, (3200.0, 400.0, 2200.0), CASSIA, '( is-event-true-delay "Jackal Cue" 0 )',
                 'ai-chase "Cassia" 60')
    m.cylon_wing("Hound", "Advanced Raider", 3, (-3500.0, -300.0, 4200.0), CASSIA,
                 '( is-event-true-delay "Hound Cue" 0 )', "ai-chase-any 60", score=20)
    m.cylon_wing("Mauler", "Heavy Raider", 2, (2600.0, 900.0, 7000.0), CASSIA,
                 '( is-event-true-delay "Mauler Cue" 0 )', 'ai-chase "Cassia" 90', spacing=140.0, score=35)
    m.cylon_wing("Jackal B", "Raider", 3, (-2800.0, 600.0, 7600.0), HESPER,
                 '( is-event-true-delay "Mauler Cue" 6 )', 'ai-chase "Hesper" 60')

    m.message("HQ Orders", "Red flight, Theseus. The tanker Cassia and the freighter Hesper are carrying every drop of tylium "
              "the Ragnar refinery could give us. Get them to the jump point. The fleet runs dry in four days without that fuel.")
    m.message("Cassia Hail", "Red Leader, Cassia. We're heavy and we're slow, so don't wander off. Halyard has our backs, "
              "but she can't turn fast enough to catch a Raider.")
    m.message("S Jackals", "Raiders, three o'clock low! Four of them, going straight for the tanker.")
    m.message("F Hounds", "More coming in on the left. Advanced models. They're faster than us on the straight.")
    m.message("Halyard Flak", "Halyard here, flak is up. Keep the bandits inside our umbrella and we'll help you thin them out.")
    m.message("S Maulers", "Heavy Raiders ahead of the convoy! They're lining up on the Cassia. If those torpedoes hit "
              "a tylium tanker, there won't be a tanker.")
    m.message("Cassia Spool", "Cassia spooling FTL. Twelve seconds. Hesper, Halyard, stay on my jump coordinates.")
    m.message("HQ Win", "Cassia and Hesper are clear and on their way to the fleet. That fuel buys us weeks. Good work, Red flight.")
    m.message("HQ Cassia Lost", "The Cassia is gone. We just lost half the fleet's fuel. Get what's left home, Red flight.")
    m.message("HQ Hesper Lost", "Hesper is down. Keep the Cassia alive, she's all we have left.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Cassia" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 3 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Cassia Msg", '( when ( is-event-true-delay "Orders Msg" 16 ) ( send-message "Cassia" "High" "Cassia Hail" ) )')
    m.event("Jackal Cue", '( when ( is-event-true-delay "Cassia Msg" 10 ) ( do-nothing ) )')
    m.event("Jackal Msg", '( when ( has-arrived-delay 3 "Jackal" ) ( send-message "Red 2" "High" "S Jackals" ) )')
    m.event("Hound Cue", '( when ( is-event-true-delay "Jackal Cue" 70 ) ( do-nothing ) )')
    m.event("Hound Msg", '( when ( has-arrived-delay 3 "Hound" ) ( send-message "Red 3" "High" "F Hounds" ) )')
    m.event("Halyard Msg", '( when ( has-arrived-delay 12 "Hound" ) ( send-message "Halyard" "High" "Halyard Flak" ) )')
    m.event("Mauler Cue", '( when ( is-event-true-delay "Hound Cue" 75 ) ( do-nothing ) )')
    m.event("Mauler Msg", '( when ( has-arrived-delay 3 "Mauler" ) ( send-message "Red 2" "High" "S Maulers" ) )')
    if not TEST:
        m.event("Guard Off", '( when ( is-event-true-delay "Mauler Cue" 20 ) ( ship-no-guardian "Cassia" ) )')
    m.event("Convoy Jump", '( when ( is-event-true-delay "Mauler Cue" 80 ) ( send-message "Cassia" "High" "Cassia Spool" ) )')
    m.event("Win", '( when ( has-departed-delay 3 "Cassia" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Cassia Lost", '( when ( is-destroyed-delay 1 "Cassia" ) ( send-message "#Command" "High" "HQ Cassia Lost" ) )')
    m.event("Hesper Lost", '( when ( is-destroyed-delay 1 "Hesper" ) ( send-message "#Command" "High" "HQ Hesper Lost" ) )')
    fail_end(m, ["Cassia Lost"])

    m.goal("Primary", "Protect Cassia", "Get the tanker Cassia to the jump point", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Secondary", "Protect Hesper", "Keep the freighter Hesper alive", '( has-departed-delay 0 "Hesper" )', 50)
    m.goal("Bonus", "Stop the Maulers", "Destroy both Heavy Raiders", '( is-destroyed-delay 0 "Mauler 1" "Mauler 2" )', 30)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "The tylium is aboard the fleet's tankers and the Viper squadrons will fly another month. The Cylons tried to "
              "starve us and you said no. Well flown, Thunderlords.",
              "Heavy Raiders carry torpedoes. Kill them before they reach firing range of the convoy.")
    m.debrief('( is-event-true-delay "Cassia Lost" 0 )',
              "The Cassia blew apart with three thousand tonnes of fuel aboard. The fleet will have to ration flight hours. "
              "We cannot afford another loss like that.",
              "Stay close to the tanker. The Maulers arrive late and from ahead of the convoy.")
    return m


# ==============================================================================================================
def hollow_rock():
    m = Mission("Hollow Rock",
                "The mining mover Kestrel stopped answering six hours ago inside the Hollow Rock field. Her beacon is still "
                "pinging. Red flight goes in to find her and bring her crew home, and Theseus suspects the Cylons are "
                "using the rocks to hide.",
                TEST)
    m.load_screen = "Load_SP-R1-M3.tga"
    m.background["sun_angles"] = "5.900000 1.200000 0.300000"
    KESTREL = (0.0, 0.0, 0.0)
    START = (0.0, 250.0, -4600.0)
    m.player_wing("Red", START, KESTREL, ["Shadow", "Flask"], guard='ai-guard "Kestrel" 60')
    m.ship("Kestrel", "Colonial Mover", "Friendly", KESTREL, (800.0, 0.0, 300.0), arrival="( true )",
           departure='( is-event-true-delay "Kestrel Jump" 10 )', ai_goals="ai-play-dead 100", hull=55, shields=0,
           flags=CIVIL_FLAGS, score=300, cargo="Miners")
    m.ship("Lantern 2", "Raptor", "Friendly", (-1800.0, 200.0, -1500.0), KESTREL,
           arrival='( is-event-true-delay "Brutes Down" 6 )', departure='( is-event-true-delay "Kestrel Jump" 10 )',
           ai_goals='ai-guard "Kestrel" 80', ai_class="Lieutenant", flags='( "cargo-known" "no-arrival-message" )',
           score=50, velocity=60)
    rock_flags = ('( "protect-ship" "no-shields" "invulnerable" "hidden-from-sensors" "stealth" '
                  '"friendly-stealth-invisible" "don\'t-collide-invisible" )')
    for i, pos in enumerate([(-900.0, 300.0, -2600.0), (700.0, -200.0, -3100.0), (1500.0, 400.0, -1200.0),
                             (-1600.0, -350.0, -700.0), (-500.0, 600.0, 900.0), (1200.0, -500.0, 1500.0),
                             (300.0, 900.0, -1800.0), (-2100.0, 100.0, 1900.0)]):
        m.ship("Rock %d" % (i + 1), "Asteroid R1", "Friendly", pos, offset(pos, 1.0, 0.3, 0.7), arrival="( true )",
               flags=rock_flags, score=0)

    m.cylon_wing("Shale", "Raider", 4, (1600.0, 450.0, -1300.0), START, '( is-event-true-delay "Ambush" 0 )',
                 "ai-chase-any 60")
    m.cylon_wing("Flint", "Advanced Raider", 2, (2800.0, -300.0, 3800.0), KESTREL,
                 '( is-event-true-delay "Boarders" 0 )', "ai-chase-any 60", score=20)
    m.cylon_wing("Brute", "Heavy Raider", 2, (3200.0, -500.0, 4200.0), KESTREL,
                 '( is-event-true-delay "Boarders" 0 )', 'ai-chase "Kestrel" 90', spacing=150.0, score=40)

    m.message("HQ Orders", "Red flight, the Kestrel's beacon is coming from the middle of Hollow Rock. Go in slow. "
              "If she's adrift, Lantern 2 will come and take her crew off.")
    m.message("F Rocks", "Lot of rocks out here, Red Leader. A whole basestar could hide in this.")
    m.message("Kestrel Hail", "Viper flight, Viper flight, this is Kestrel! Engines dead, eleven aboard. There's something "
              "moving in the rocks, it's been circling us for hours.")
    m.message("S Ambush", "Raiders! They were sitting in the rocks! It's a trap, break, break!")
    m.message("HQ Boarders", "Red flight, DRADIS has Heavy Raiders inbound to the Kestrel. Those are boarding craft. "
              "Do not let them reach that mover.")
    m.message("F Brutes", "Two Heavies with escorts. Take the Heavies, the escorts can wait.")
    m.message("Lantern Arrive", "Lantern 2 inbound. Kestrel, get your people to the airlock, we're taking you home.")
    m.message("Kestrel Spool", "Our jump drive just came back! Lantern, we'll follow you out. Thank you, Thunderlords.")
    m.message("HQ Win", "Kestrel and Lantern 2 are clear of Hollow Rock. Eleven miners coming home. Bring it in, Red flight.")
    m.message("HQ Boarded", "The Cylons have boarded the Kestrel. We've lost her. Break off and return to Theseus.")
    m.message("HQ Kestrel Lost", "Kestrel is gone. Gods. Return to Theseus, Red flight.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 25 "Kestrel" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 3 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Rocks Msg", '( when ( is-event-true-delay "Orders Msg" 14 ) ( send-message "Red 3" "High" "F Rocks" ) )')
    m.event("Kestrel Msg", '( when ( is-event-true-delay "Rocks Msg" 10 ) ( send-message "Kestrel" "High" "Kestrel Hail" ) )')
    m.event("Ambush", '( when ( is-event-true-delay "Kestrel Msg" 8 ) ( do-nothing ) )')
    m.event("Ambush Msg", '( when ( has-arrived-delay 2 "Shale" ) ( send-message "Red 2" "High" "S Ambush" ) )')
    m.event("Boarders", '( when ( is-event-true-delay "Ambush" 65 ) ( do-nothing ) )')
    m.event("Boarders Msg", '( when ( has-arrived-delay 3 "Brute" ) ( send-message "#Command" "High" "HQ Boarders" ) )')
    m.event("Brutes Msg", '( when ( has-arrived-delay 10 "Brute" ) ( send-message "Red 3" "High" "F Brutes" ) )')
    m.event("Brutes Down", '( when ( is-destroyed-delay 1 "Brute 1" "Brute 2" ) ( do-nothing ) )')
    m.event("Lantern Msg", '( when ( has-arrived-delay 2 "Lantern 2" ) ( send-message "Lantern 2" "High" "Lantern Arrive" ) )')
    m.event("Kestrel Jump", '( when ( is-event-true-delay "Brutes Down" 40 ) ( send-message "Kestrel" "High" "Kestrel Spool" ) )')
    m.event("Win", '( when ( has-departed-delay 3 "Kestrel" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Boarded", '( when ( or ( < ( distance "Brute 1" "Kestrel" ) 180 ) ( < ( distance "Brute 2" "Kestrel" ) 180 ) ) '
                       '( send-message "#Command" "High" "HQ Boarded" ) )')
    m.event("Kestrel Lost", '( when ( is-destroyed-delay 1 "Kestrel" ) ( send-message "#Command" "High" "HQ Kestrel Lost" ) )')
    fail_end(m, ["Boarded", "Kestrel Lost"])

    m.goal("Primary", "Save the Kestrel", "Get the Kestrel and her crew out of Hollow Rock", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Stop the boarders", "Destroy the Heavy Raiders before they reach the Kestrel",
           '( is-event-true-delay "Brutes Down" 0 )', 100)
    m.goal("Secondary", "Clear the ambush", "Destroy the Raiders hiding in the rocks",
           '( percent-ships-destroyed 75 "Shale" "Flint" )', 50)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "Eleven miners are eating real food aboard Theseus tonight. The Cylons were using Hollow Rock as a hunting blind, "
              "and you turned it into a graveyard. Good work.",
              "Heavy Raiders inside the rocks are boarding craft. They don't need to win the fight, only to reach their target.")
    m.debrief('( or ( is-event-true-delay "Boarded" 0 ) ( is-event-true-delay "Kestrel Lost" 0 ) )',
              "We lost the Kestrel. Whatever the Cylons wanted with eleven miners, they have it now.",
              "Ignore the escorts when the Heavy Raiders show up and go straight for the boarding craft.")
    return m


# ==============================================================================================================
def firebreak():
    m = Mission("Firebreak",
                "A Cylon missile cracked Theseus' FTL coolant lines during the last jump. Engineering needs four minutes "
                "to bypass them, and the Cylons have found us. Red and Blue flights hold the line until the battlestar can jump.",
                TEST)
    m.load_screen = "Load_SP-R1-M6.tga"
    m.background["sun_angles"] = "0.400000 2.600000 1.900000"
    THESEUS = (0.0, 0.0, 0.0)
    m.player_wing("Red", (0.0, 200.0, 1600.0), (0.0, 300.0, 9000.0), ["Shadow", "Flask"], guard='ai-guard "Theseus" 60')
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", THESEUS, (0.0, 0.0, 5000.0), arrival="( true )",
           departure='( is-event-true-delay "FTL Ready" 12 )', flags=CAPITAL_FLAGS, shields=0, score=2000)
    m.ship("Blue 1", "Viper Mark VII", "Friendly", (-400.0, 100.0, 1200.0), (0.0, 0.0, 9000.0), arrival="( true )",
           flags='( "cargo-known" "don\'t-collide-invisible" )', callsign="Ghost", ai_class="Lieutenant",
           primaries=["MEC-A6", "MEC-A6"], secondaries=["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"])
    m.ship("Blue 2", "Viper Mark VII", "Friendly", (-460.0, 100.0, 1190.0), (0.0, 0.0, 9000.0), arrival="( true )",
           flags='( "cargo-known" "don\'t-collide-invisible" )', callsign="Rook", ai_class="Lieutenant",
           primaries=["MEC-A6", "MEC-A6"], secondaries=["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"])
    m.wing("Blue", ["Blue 1", "Blue 2"], "( true )", goals="ai-chase-any 60")

    m.cylon_wing("Ember", "Raider", 4, (500.0, 600.0, 7500.0), THESEUS, '( is-event-true-delay "Ember Cue" 0 )',
                 "ai-chase-any 60")
    m.cylon_wing("Soot", "Advanced Raider", 3, (-4000.0, 400.0, 6000.0), THESEUS, '( is-event-true-delay "Cinder Cue" 0 )',
                 "ai-chase-any 60", score=20)
    m.cylon_wing("Cinder", "Heavy Raider", 3, (3800.0, -700.0, 6500.0), THESEUS, '( is-event-true-delay "Cinder Cue" 4 )',
                 'ai-chase "Theseus" 90', spacing=160.0, score=35)
    m.ship("Ashfall", "Basestar", "Hostile", (6000.0, 900.0, 11000.0), THESEUS,
           arrival='( is-event-true-delay "Basestar Cue" 0 )', ai_goals='ai-chase "Theseus" 80', ai_class="Lieutenant",
           flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Slag", "Raider", 4, (5200.0, 700.0, 9800.0), THESEUS, '( is-event-true-delay "Basestar Cue" 10 )',
                 "ai-chase-any 60")

    m.message("HQ Orders", "All Vipers, Theseus Actual. Our FTL is down for four minutes. Raiders are inbound. "
              "Red and Blue flights, you are the firebreak. Nothing gets to this ship.")
    m.message("Ghost Hail", "Ghost here. Blue flight takes the left side, Red Leader. Let's make this quick.")
    m.message("S Embers", "First wave, dead ahead! Four Raiders.")
    m.message("HQ Cinder", "Heavy Raiders with torpedoes on the starboard approach. Kill them before they launch!")
    m.message("F Soot", "And their escorts on the port side. Blue flight, you've got company.")
    m.message("HQ Basestar", "DRADIS contact, basestar! Ten kilometres and closing. Engineering, I need that FTL!")
    m.message("S Slag", "It's launching more Raiders. Hold the line, Thunderlords!")
    m.message("HQ FTL", "FTL is green. All Vipers, we jump in twelve seconds. Get clear of the hull!")
    m.message("HQ Win", "Jump complete. Theseus is clear and every Viper came with us. That was a firebreak, people.")
    m.message("HQ Lost", "Theseus is breaking up. All Vipers, scatter and jump to the fleet rendezvous.")

    m.event("Orders Msg", '( when ( true ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Ghost Msg", '( when ( is-event-true-delay "Orders Msg" 14 ) ( send-message "Blue 1" "High" "Ghost Hail" ) )')
    m.event("Ember Cue", '( when ( is-event-true-delay "Ghost Msg" 6 ) ( do-nothing ) )')
    m.event("Ember Msg", '( when ( has-arrived-delay 3 "Ember" ) ( send-message "Red 2" "High" "S Embers" ) )')
    m.event("Cinder Cue", '( when ( is-event-true-delay "Ember Cue" 70 ) ( do-nothing ) )')
    m.event("Cinder Msg", '( when ( has-arrived-delay 3 "Cinder" ) ( send-message "#Command" "High" "HQ Cinder" ) )')
    m.event("Soot Msg", '( when ( has-arrived-delay 9 "Soot" ) ( send-message "Red 3" "High" "F Soot" ) )')
    m.event("Basestar Cue", '( when ( is-event-true-delay "Cinder Cue" 75 ) ( do-nothing ) )')
    m.event("Basestar Msg", '( when ( has-arrived-delay 3 "Ashfall" ) ( send-message "#Command" "High" "HQ Basestar" ) )')
    m.event("Slag Msg", '( when ( has-arrived-delay 4 "Slag" ) ( send-message "Red 2" "High" "S Slag" ) )')
    m.event("FTL Ready", '( when ( is-event-true-delay "Basestar Cue" 80 ) ( send-message "#Command" "High" "HQ FTL" ) )')
    m.event("Win", '( when ( has-departed-delay 2 "Theseus" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Theseus Lost", '( when ( is-destroyed-delay 1 "Theseus" ) ( send-message "#Command" "High" "HQ Lost" ) )')
    fail_end(m, ["Theseus Lost"])

    m.goal("Primary", "Protect Theseus", "Hold the line until Theseus jumps", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Secondary", "Stop the torpedo runs", "Destroy the Heavy Raiders",
           '( is-destroyed-delay 0 "Cinder 1" "Cinder 2" "Cinder 3" )', 50)
    m.goal("Bonus", "Firebreak", "Destroy most of the Raiders", '( percent-ships-destroyed 75 "Ember" "Soot" "Slag" )', 30)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "Theseus jumped with her whole air group aboard and the Cylons got nothing but wreckage. The engineers bought "
              "four minutes and you made them count.",
              "Heavy Raiders carry torpedoes. They come in from the flank while the Raiders keep you busy.")
    m.debrief('( is-event-true-delay "Theseus Lost" 0 )',
              "Theseus is gone. That should not be possible, and yet here we are.",
              "Stay near the battlestar. The torpedo carriers are the only real threat to her.")
    return m


# ==============================================================================================================
def iron_shepherd():
    m = Mission("Iron Shepherd",
                "The frigate Halyard is shepherding two liners full of refugees from Picon's moon to the fleet. Their route "
                "runs through the Tessaly belt, and the Cylons have been hunting in it. Red flight flies cover for the Halyard "
                "and her flock until they reach the jump point.",
                TEST)
    m.load_screen = "Load_SP-R1-M4.tga"
    m.background["sun_angles"] = "5.200000 0.700000 2.300000"
    HALYARD, END = (0.0, 0.0, 0.0), (-400.0, 300.0, 9500.0)
    m.player_wing("Red", (300.0, 250.0, -1600.0), END, ["Shadow", "Flask"], guard='ai-guard "Halyard" 60')
    jump = '( is-event-true-delay "Flock Jump" 12 )'
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", HALYARD, END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Belt Lane" 90', flags=CAPITAL_FLAGS, shields=0, score=600)
    m.ship("Aster", "Gemenon Traveler", "Friendly", (-500.0, 100.0, 400.0), END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Belt Lane" 90', flags=CIVIL_FLAGS, shields=0, score=300, cargo="Refugees")
    m.ship("Briony", "Gemenon Traveler", "Friendly", (500.0, -100.0, 300.0), END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Belt Lane" 90', flags=CIVIL_FLAGS, shields=0, score=300, cargo="Refugees")
    m.waypoint_list("Belt Lane", [(0.0, 0.0, 2000.0), (-600.0, 200.0, 5000.0), (-400.0, 300.0, 9000.0)])
    rock_flags = ('( "protect-ship" "no-shields" "invulnerable" "hidden-from-sensors" "stealth" '
                  '"friendly-stealth-invisible" "don\'t-collide-invisible" )')
    for i, pos in enumerate([(-2200.0, 400.0, 2500.0), (1900.0, -300.0, 3200.0), (-1500.0, -600.0, 5600.0),
                             (2300.0, 700.0, 6200.0), (900.0, 1100.0, 4100.0), (-2600.0, 200.0, 7600.0)]):
        m.ship("Belt Rock %d" % (i + 1), "Asteroid R1", "Friendly", pos, offset(pos, 0.4, 1.0, 0.2), arrival="( true )",
               flags=rock_flags, score=0)

    m.cylon_wing("Wolf", "Raider", 4, (2600.0, 500.0, 3600.0), HALYARD, '( is-event-true-delay "Wolf Cue" 0 )',
                 'ai-chase "Aster" 60')
    m.cylon_wing("Jackal", "Advanced Raider", 3, (-2900.0, -400.0, 5200.0), HALYARD, '( is-event-true-delay "Jackal Cue" 0 )',
                 'ai-chase "Briony" 60', score=20)
    m.cylon_wing("Ram", "Heavy Raider", 2, (300.0, 1300.0, 8200.0), HALYARD, '( is-event-true-delay "Ram Cue" 0 )',
                 'ai-chase "Halyard" 90', spacing=150.0, score=35)

    m.message("HQ Orders", "Red flight, Theseus. Halyard is bringing two liners through the Tessaly belt. Stay with her. "
              "The Cylons like to hunt in the rocks.")
    m.message("Halyard Hail", "Red Leader, Commander Ostrava, Halyard. My flak will keep anything big off us, but Raiders "
              "are too quick for my gunners. Keep them off the liners and I'll handle the rest.")
    m.message("S Wolves", "Raiders out of the rocks, they're going for the Aster!")
    m.message("Halyard Flak", "Halyard, all batteries, flak barrage on my port side. Red flight, drive them into it!")
    m.message("F Jackals", "Second group, advanced models on the Briony! I'm on them.")
    m.message("S Rams", "Heavy Raiders ahead, lining up on the Halyard!")
    m.message("Halyard Torps", "They're making torpedo runs on us. I can take a few hits, but kill those Heavies!")
    m.message("Halyard Jump", "Jump point reached. Flock, on my coordinates. Red flight, thank you, we'll see you at the fleet.")
    m.message("HQ Win", "Halyard and both liners are clear. Nine hundred people just reached the fleet. Good work, Red flight.")
    m.message("HQ Liner Lost", "We've lost one of the liners. Gods. Keep the other one alive, Red flight.")
    m.message("HQ Halyard Lost", "Halyard is gone. Without her the liners don't stand a chance. Break off, Red flight.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 3 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Halyard Msg", '( when ( is-event-true-delay "Orders Msg" 15 ) ( send-message "Halyard" "High" "Halyard Hail" ) )')
    m.event("Wolf Cue", '( when ( is-event-true-delay "Halyard Msg" 10 ) ( do-nothing ) )')
    m.event("Wolf Msg", '( when ( has-arrived-delay 3 "Wolf" ) ( send-message "Red 2" "High" "S Wolves" ) )')
    m.event("Flak Msg", '( when ( has-arrived-delay 12 "Wolf" ) ( send-message "Halyard" "High" "Halyard Flak" ) )')
    m.event("Jackal Cue", '( when ( is-event-true-delay "Wolf Cue" 65 ) ( do-nothing ) )')
    m.event("Jackal Msg", '( when ( has-arrived-delay 3 "Jackal" ) ( send-message "Red 3" "High" "F Jackals" ) )')
    m.event("Ram Cue", '( when ( is-event-true-delay "Jackal Cue" 70 ) ( do-nothing ) )')
    m.event("Ram Msg", '( when ( has-arrived-delay 3 "Ram" ) ( send-message "Red 2" "High" "S Rams" ) )')
    m.event("Torp Msg", '( when ( has-arrived-delay 15 "Ram" ) ( send-message "Halyard" "High" "Halyard Torps" ) )')
    if not TEST:
        m.event("Guard Off", '( when ( is-event-true-delay "Ram Cue" 25 ) ( ship-no-guardian "Halyard" ) )')
    m.event("Flock Jump", '( when ( is-event-true-delay "Ram Cue" 80 ) ( send-message "Halyard" "High" "Halyard Jump" ) )')
    m.event("Win", '( when ( has-departed-delay 3 "Halyard" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Liner Lost", '( when ( or ( is-destroyed-delay 1 "Aster" ) ( is-destroyed-delay 1 "Briony" ) ) '
                          '( send-message "#Command" "High" "HQ Liner Lost" ) )')
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    m.event("Both Liners Lost", '( when ( is-destroyed-delay 1 "Aster" "Briony" ) ( do-nothing ) )')
    fail_end(m, ["Halyard Lost", "Both Liners Lost"])

    m.goal("Primary", "Shepherd the Halyard", "Get the frigate Halyard to the jump point", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Protect the liners", "Get at least one liner to the jump point",
           '( or ( has-departed-delay 0 "Aster" ) ( has-departed-delay 0 "Briony" ) )', 50)
    m.goal("Secondary", "Every last refugee", "Get both liners to the jump point", '( has-departed-delay 0 "Aster" "Briony" )', 50)
    m.goal("Bonus", "Stop the torpedo runs", "Destroy both Heavy Raiders", '( is-destroyed-delay 0 "Ram 1" "Ram 2" )', 30)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "The Halyard brought her flock home. Commander Ostrava sends her thanks and says her gunners owe Red flight "
              "a round. The Tessaly belt is a little quieter tonight.",
              "Drive the Raiders into the Halyard's flak. A frigate's guns do a lot of the work if you let them.")
    m.debrief('( or ( is-event-true-delay "Halyard Lost" 0 ) ( is-event-true-delay "Both Liners Lost" 0 ) )',
              "The flock never reached the fleet. We'll be counting the cost of the Tessaly belt for a long time.",
              "The Heavy Raiders arrive last and go for the frigate. Have missiles left for them.")
    return m


# ==============================================================================================================
def dead_reckoning():
    m = Mission("Dead Reckoning",
                "A Colonial supply convoy was ambushed and scattered. Its cargo pods are drifting near the Anchises relay, "
                "and one of them carries the fleet's last stock of antibiotics. Red flight has to scan the pods and find it "
                "before the Cylons come back for the rest.",
                TEST)
    m.load_screen = "Load_SP-R1-M3.tga"
    m.background["sun_angles"] = "1.100000 4.000000 0.600000"
    POD_AREA = (0.0, 0.0, 0.0)
    m.player_wing("Red", (0.0, 300.0, -3500.0), POD_AREA, ["Shadow", "Flask"], guard="ai-chase-any 50")
    pod_flags = '( "no-shields" "no-arrival-warp" "don\'t-collide-invisible" )'
    pods = [("Pod Alpha", (-900.0, 100.0, -400.0), "Spare parts"), ("Pod Bravo", (700.0, -200.0, 300.0), "Water"),
            ("Pod Charlie", (-200.0, 400.0, 1200.0), "Antibiotics"), ("Pod Delta", (1300.0, 250.0, 1600.0), "Ration packs")]
    for name, pos, cargo in pods:
        m.ship(name, "CM Container1", "Friendly", pos, offset(pos, 0.3, 0.2, 1.0), arrival="( true )",
               flags=pod_flags, shields=0, score=0, cargo=cargo)
    m.ship("Lantern 3", "Raptor", "Friendly", (-2500.0, 200.0, -2500.0), (-200.0, 400.0, 1200.0),
           arrival='( is-event-true-delay "Found" 8 )', departure='( is-event-true-delay "Lantern Out" 0 )',
           ai_goals='ai-waypoints-once "Lantern Run" 90', ai_class="Lieutenant",
           flags='( "cargo-known" "no-arrival-message" )', score=100, velocity=60)
    m.waypoint_list("Lantern Run", [(-1800.0, 250.0, -1200.0), (-700.0, 350.0, 600.0), (-250.0, 420.0, 1100.0)])

    m.cylon_wing("Scav", "Raider", 3, (2500.0, 600.0, 2500.0), POD_AREA, '( is-event-true-delay "Scav Cue" 0 )',
                 "ai-chase-any 60")
    m.cylon_wing("Vulture", "Advanced Raider", 3, (-2800.0, -300.0, 2600.0), (-200.0, 400.0, 1200.0),
                 '( is-event-true-delay "Found" 15 )', 'ai-chase "Lantern 3" 80', score=20)
    m.cylon_wing("Hauler", "Heavy Raider", 2, (3000.0, -600.0, 4000.0), (-200.0, 400.0, 1200.0),
                 '( is-event-true-delay "Found" 45 )', 'ai-chase "Lantern 3" 90', spacing=150.0, score=35)

    m.message("HQ Orders", "Red flight, four cargo pods are drifting at the relay. Fly close to each one and scan it. "
              "We need the antibiotics. When you find them, Lantern 3 will come and haul the pod home.")
    m.message("F Scan", "Scanning takes a few seconds at close range. Target a pod and hold steady next to it.")
    m.message("S Scavs", "Raiders! They're picking over the pods. Clear them off.")
    m.message("F Found", "That's it, Red Leader, Pod Charlie, antibiotics! Calling Lantern 3.")
    m.message("Lantern Hail", "Lantern 3 inbound for Pod Charlie. I'll need about forty seconds to hook it up. Keep them off me.")
    m.message("S Vultures", "Advanced Raiders going for the Raptor!")
    m.message("S Haulers", "Heavy Raiders! They want that pod too!")
    m.message("Lantern Done", "Pod's secure. Jumping out with it now!")
    m.message("HQ Win", "Lantern 3 is back with the antibiotics. That's a lot of fevers that won't kill anyone. Come home, Red flight.")
    m.message("HQ Lantern Lost", "Lantern 3 is down and the pod with her. Gods. Return to Theseus.")
    m.message("HQ Pod Lost", "Pod Charlie is destroyed. The antibiotics are gone. Return to Theseus.")

    m.event("Orders Msg", '( when ( true ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Scan Msg", '( when ( is-event-true-delay "Orders Msg" 14 ) ( send-message "Red 2" "High" "F Scan" ) )')
    m.event("Scav Cue", '( when ( is-event-true-delay "Scan Msg" 25 ) ( do-nothing ) )')
    m.event("Scav Msg", '( when ( has-arrived-delay 3 "Scav" ) ( send-message "Red 3" "High" "S Scavs" ) )')
    m.event("Found", '( when ( is-cargo-known-delay 0 "Pod Charlie" ) ( send-message "Red 2" "High" "F Found" ) )')
    m.event("Lantern Msg", '( when ( has-arrived-delay 2 "Lantern 3" ) ( send-message "Lantern 3" "High" "Lantern Hail" ) )')
    m.event("Vulture Msg", '( when ( has-arrived-delay 3 "Vulture" ) ( send-message "Red 3" "High" "S Vultures" ) )')
    m.event("Hauler Msg", '( when ( has-arrived-delay 3 "Hauler" ) ( send-message "Red 2" "High" "S Haulers" ) )')
    m.event("Lantern Out", '( when ( has-arrived-delay 75 "Lantern 3" ) ( send-message "Lantern 3" "High" "Lantern Done" ) )')
    m.event("Win", '( when ( has-departed-delay 3 "Lantern 3" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Lantern Lost", '( when ( is-destroyed-delay 1 "Lantern 3" ) ( send-message "#Command" "High" "HQ Lantern Lost" ) )')
    m.event("Pod Lost", '( when ( is-destroyed-delay 1 "Pod Charlie" ) ( send-message "#Command" "High" "HQ Pod Lost" ) )')
    fail_end(m, ["Lantern Lost", "Pod Lost"])

    m.goal("Primary", "Find the antibiotics", "Scan the cargo pods and find the antibiotics",
           '( is-cargo-known-delay 0 "Pod Charlie" )', 100)
    m.goal("Primary", "Recover the pod", "Protect Lantern 3 until she jumps out with the pod", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Secondary", "Drive off the raiders", "Destroy most of the Cylon raiders",
           '( percent-ships-destroyed 75 "Scav" "Vulture" "Hauler" )', 50)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "The antibiotics are aboard Theseus and on their way to the fleet's sickbays. The doctors say you just saved "
              "more lives than any dogfight this month. Well done.",
              "Scan the pods quickly. The Cylons send more ships the longer you stay at the relay.")
    m.debrief('( or ( is-event-true-delay "Lantern Lost" 0 ) ( is-event-true-delay "Pod Lost" 0 ) )',
              "We lost the antibiotics. People in the fleet will die of infections we know how to cure.",
              "Stay with the Raptor once she arrives. The Heavy Raiders come late and go straight for her.")
    return m


# ==============================================================================================================
def hammer_and_anvil():
    m = Mission("Hammer and Anvil",
                "Raptor recon caught six Cylon Heavy Raiders massing at the edge of the Ilion system, loaded for a strike on "
                "the fleet. The frigate Halyard will jump into their path as the anvil, Red and Blue flights are the hammer. "
                "Kill the Heavy Raiders before they jump away.",
                TEST)
    m.load_screen = "Load_SP-R1-M6.tga"
    m.background["sun_angles"] = "0.900000 3.300000 2.700000"
    STAGING = (0.0, 0.0, 6000.0)
    m.player_wing("Red", (-600.0, 300.0, 0.0), STAGING, ["Shadow", "Flask"], guard="ai-chase-any 50")
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", (800.0, -200.0, 2500.0), STAGING, arrival="( true )",
           departure='( is-event-true-delay "Strike Over" 15 )', ai_goals='ai-chase-any 70', flags=CAPITAL_FLAGS,
           shields=0, score=600)
    for i, (cs, pos) in enumerate([("Ghost", (-900.0, 300.0, -20.0)), ("Rook", (-960.0, 300.0, -30.0))]):
        m.ship("Blue %d" % (i + 1), "Viper Mark VII", "Friendly", pos, STAGING, arrival="( true )",
               flags='( "cargo-known" "don\'t-collide-invisible" )', callsign=cs, ai_class="Lieutenant",
               primaries=["MEC-A6", "MEC-A6"], secondaries=["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"])
    m.wing("Blue", ["Blue 1", "Blue 2"], "( true )", goals="ai-chase-any 60")

    heavies = []
    for i in range(6):
        pos = offset(STAGING, (i - 2.5) * 220.0, (i % 2) * 150.0, (i % 3) * 120.0)
        name = "Strike %d" % (i + 1)
        m.ship(name, "Heavy Raider", "Hostile", pos, offset(STAGING, 0.0, 0.0, 9000.0), ai_class="Lieutenant",
               flags=CYLON_FLAGS, flags2='( "no-ets" )', score=40, ai_goals='ai-waypoints-once "Strike Lane" 90')
        heavies.append(name)
    m.wing("Strike", heavies, "( true )", departure='( is-event-true-delay "Strike Jump" 0 )',
           goals='ai-waypoints-once "Strike Lane" 90')
    m.waypoint_list("Strike Lane", [offset(STAGING, 0.0, 200.0, 3000.0), offset(STAGING, 400.0, 400.0, 8000.0)])
    m.cylon_wing("Picket", "Raider", 4, offset(STAGING, -800.0, 300.0, -800.0), (-600.0, 300.0, 0.0), "( true )",
                 "ai-chase-any 60")
    m.cylon_wing("Escort", "Advanced Raider", 3, offset(STAGING, 1500.0, -200.0, 1500.0), (800.0, -200.0, 2500.0),
                 '( is-event-true-delay "Escort Cue" 0 )', 'ai-chase "Halyard" 70', score=20)

    m.message("HQ Orders", "Red flight, Blue flight, the Heavy Raiders are refuelling for a strike on the fleet. They're "
              "loaded with nukes. They will jump in about three minutes. Every one that gets away is a ship we lose.")
    m.message("Halyard Hail", "Halyard in position. We're the anvil, gentlemen. Push them into my guns.")
    m.message("S Picket", "Pickets coming at us! Ignore them if you can, the Heavies are the target.")
    m.message("F Moving", "The Heavies are moving out, they're spooling up!")
    m.message("S Escort", "Advanced Raiders on the Halyard!")
    m.message("HQ One Minute", "One minute until they reach jump distance. Hit them now!")
    m.message("HQ Jump", "The surviving Heavy Raiders have jumped.")
    m.message("HQ Win", "That strike force is gone. The fleet sleeps tonight because of you. Bring it home, all flights.")
    m.message("HQ Partial", "Some of them got away. The fleet is on alert. Return to Theseus.")
    m.message("HQ Halyard Lost", "We've lost the Halyard! All flights, break off and return to Theseus.")

    m.event("Orders Msg", '( when ( true ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Halyard Msg", '( when ( is-event-true-delay "Orders Msg" 14 ) ( send-message "Halyard" "High" "Halyard Hail" ) )')
    m.event("Picket Msg", '( when ( is-event-true-delay "Halyard Msg" 6 ) ( send-message "Red 2" "High" "S Picket" ) )')
    m.event("Moving Msg", '( when ( is-event-true-delay "Picket Msg" 20 ) ( send-message "Red 3" "High" "F Moving" ) )')
    m.event("Escort Cue", '( when ( is-event-true-delay "Picket Msg" 55 ) ( do-nothing ) )')
    m.event("Escort Msg", '( when ( has-arrived-delay 3 "Escort" ) ( send-message "Red 2" "High" "S Escort" ) )')
    m.event("One Minute", '( when ( is-event-true-delay "Picket Msg" 120 ) ( send-message "#Command" "High" "HQ One Minute" ) )')
    m.event("Strike Jump", '( when ( is-event-true-delay "One Minute" 60 ) ( send-message "#Command" "High" "HQ Jump" ) )')
    m.event("All Dead", '( when ( is-destroyed-delay 1 "Strike 1" "Strike 2" "Strike 3" "Strike 4" "Strike 5" "Strike 6" ) '
                        '( do-nothing ) )')
    m.event("Strike Over", '( when ( or ( is-event-true-delay "All Dead" 0 ) ( is-event-true-delay "Strike Jump" 3 ) ) ( do-nothing ) )')
    m.event("Win", '( when ( and ( is-event-true-delay "Strike Over" 3 ) ( percent-ships-destroyed 66 "Strike" ) ) '
                   '( send-message "#Command" "High" "HQ Win" ) )')
    m.event("Partial", '( when ( and ( is-event-true-delay "Strike Over" 3 ) ( not ( percent-ships-destroyed 66 "Strike" ) ) ) '
                       '( send-message "#Command" "High" "HQ Partial" ) )')
    m.event("Fade out", '( when ( or ( is-event-true-delay "Win" 9 ) ( is-event-true-delay "Partial" 9 ) ) ( fade-out 1000 ) )')
    m.event("Finish", '( when ( is-event-true-delay "Fade out" 2 ) ( end-mission ) )')
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    m.event("Fail Fade", '( when ( is-event-true-delay "Halyard Lost" 8 ) ( fade-out 1000 ) )')
    m.event("Fail End", '( when ( is-event-true-delay "Fail Fade" 2 ) ( end-mission ) )')

    m.goal("Primary", "Break the strike", "Destroy at least four of the six Heavy Raiders", '( is-event-true-delay "Win" 0 )', 150)
    m.goal("Secondary", "Protect the Halyard", "Keep the frigate Halyard alive",
           '( and ( is-event-true-delay "Strike Over" 0 ) ( not ( is-destroyed-delay 0 "Halyard" ) ) )', 50)
    m.goal("Bonus", "Leave none", "Destroy all six Heavy Raiders", '( is-event-true-delay "All Dead" 0 )', 50)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "The strike never reached the fleet. Six nukes that would have killed thousands are drifting wreckage in the "
              "Ilion system, and the Halyard proved what a frigate can do with good pilots around her.",
              "The pickets are a distraction. Go for the Heavy Raiders first and let the Halyard's guns handle the escorts.")
    m.debrief('( is-event-true-delay "Partial" 0 )',
              "Some of the Heavy Raiders jumped clear. The fleet is moving on emergency coordinates and we are counting "
              "on the Battlestar's guns to stop the rest.",
              "You have about three minutes. Missiles first on the Heavies, guns for whatever is left.")
    m.debrief('( is-event-true-delay "Halyard Lost" 0 )',
              "We lost the Halyard. Without the anvil the hammer had nothing to strike against.",
              "Keep the Advanced Raiders off the frigate when they arrive.")
    return m


# ==============================================================================================================
def deep_look():
    m = Mission("Deep Look",
                "Raptor recon found a basestar drifting dark at the edge of the Kobol debris field. It could be dead, or it "
                "could be waiting. You take Lantern 1, a Raptor, in close enough to scan it, with Shadow and Flask flying "
                "escort. Get the scan and get out.",
                TEST)
    m.load_screen = "Load_SP-R1-M3.tga"
    m.background["sun_angles"] = "4.700000 0.400000 1.100000"
    HECATE = (0.0, 0.0, 0.0)
    START = (0.0, 400.0, -5200.0)
    m.player_wing("Red", START, HECATE, ["Shadow", "Flask"], guard='ai-guard "Red 1" 70',
                  player_class="Raptor", player_primaries=["MEC-A6"], player_secondaries=["HD-51 Arbalest"])
    m.ship("Hecate", "Basestar", "Hostile", HECATE, (2000.0, 0.0, 9000.0), arrival="( true )",
           ai_goals="ai-play-dead 100", flags='( "no-arrival-warp" )', flags2='( "lock-all-turrets" )', score=1500,
           cargo="Cylon Data Core")
    rock_flags = ('( "protect-ship" "no-shields" "invulnerable" "hidden-from-sensors" "stealth" '
                  '"friendly-stealth-invisible" "don\'t-collide-invisible" )')
    for i, pos in enumerate([(-1300.0, 600.0, -3300.0), (1100.0, -400.0, -2700.0), (-700.0, -800.0, -1800.0),
                             (1800.0, 900.0, -1500.0), (-2200.0, 200.0, -900.0)]):
        m.ship("Debris %d" % (i + 1), "Asteroid R1", "Friendly", pos, offset(pos, 0.9, 0.1, 0.3), arrival="( true )",
               flags=rock_flags, score=0)

    m.cylon_wing("Wake", "Raider", 4, (600.0, -300.0, 900.0), START, '( is-event-true-delay "Waking" 4 )',
                 'ai-chase "Red 1" 70')
    m.cylon_wing("Fury", "Advanced Raider", 3, (-900.0, 500.0, 700.0), START, '( is-event-true-delay "Waking" 25 )',
                 'ai-chase "Red 1" 80', score=20)
    m.cylon_wing("Mob", "Raider", 4, (1400.0, 800.0, -400.0), START, '( is-event-true-delay "Waking" 50 )',
                 "ai-chase-any 60")

    m.message("HQ Orders", "Lantern 1, Theseus. That basestar hasn't moved in six hours. Get within scanning range, "
              "target it and hold steady until your DRADIS has the scan. Then turn around and stay alive. Don't fire on it.")
    m.message("Shadow Hail", "Shadow and Flask on your wing, Lantern. You do the looking, we'll do the shooting.")
    m.message("F Close", "Getting close now. Gods, it's big. Nothing moving on the hull.")
    m.message("Scan Done", "Scan complete! I've got their whole... wait. It's powering up. It's powering up!")
    m.message("S Wake", "Raiders launching, they're coming for the Raptor! Lantern, get your nose pointed home!")
    m.message("HQ Run", "Lantern 1, we have your data. Stay alive for one more minute while we plot your jump.")
    m.message("F Fury", "Advanced models! I can't keep them all off you, Lantern!")
    m.message("HQ Jump", "Jump solution sent. Everyone out, now!")
    m.message("HQ Win", "Lantern 1 is home and that data is pure gold. Good flying, all of you.")
    m.message("HQ Lost", "We've lost Lantern 1 and the scan with her. Shadow, Flask, come home.")

    m.event("Orders Msg", '( when ( true ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Shadow Msg", '( when ( is-event-true-delay "Orders Msg" 15 ) ( send-message "Red 2" "High" "Shadow Hail" ) )')
    m.event("Close Msg", '( when ( < ( distance "Red 1" "Hecate" ) 2500 ) ( send-message "Red 1" "High" "F Close" ) )')
    m.event("Waking", '( when ( is-cargo-known-delay 0 "Hecate" ) ( send-message "Red 1" "High" "Scan Done" ) )')
    m.event("Turrets Free", '( when ( is-event-true-delay "Waking" 3 ) ( turret-free-all "Hecate" ) )')
    m.event("Wake Msg", '( when ( has-arrived-delay 2 "Wake" ) ( send-message "Red 2" "High" "S Wake" ) )')
    m.event("Run Msg", '( when ( is-event-true-delay "Waking" 12 ) ( send-message "#Command" "High" "HQ Run" ) )')
    m.event("Fury Msg", '( when ( has-arrived-delay 3 "Fury" ) ( send-message "Red 3" "High" "F Fury" ) )')
    m.event("Jump Msg", '( when ( is-event-true-delay "Waking" 75 ) ( send-message "#Command" "High" "HQ Jump" ) )')
    m.event("Win", '( when ( is-event-true-delay "Jump Msg" 6 ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Lantern Lost", '( when ( is-destroyed-delay 1 "Red 1" ) ( send-message "#Command" "High" "HQ Lost" ) )')
    fail_end(m, ["Lantern Lost"])

    m.goal("Primary", "Scan the basestar", "Fly the Raptor into scanning range and scan the basestar Hecate",
           '( is-cargo-known-delay 0 "Hecate" )', 100)
    m.goal("Primary", "Bring the data home", "Survive until the jump", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Bonus", "Escort's pride", "Shadow and Flask both make it home",
           '( and ( is-event-true-delay "Win" 0 ) ( not ( is-destroyed-delay 0 "Red 2" "Red 3" ) ) )', 30)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "The scan shows the basestar was refitting its raider bays. Theseus is warning the whole fleet. That was a "
              "Raptor crew's job done the way it should be done.",
              "A Raptor is slow and has no shields. Let the Vipers fight, keep moving and use countermeasures.")
    m.debrief('( is-event-true-delay "Lantern Lost" 0 )',
              "Lantern 1 never came back. Whatever was on that basestar stays a mystery.",
              "Once the scan is done, turn away from the basestar at full speed and stay near your escorts.")
    return m


# ==============================================================================================================
def station_keeping():
    m = Mission("Station Keeping",
                "The old Armistice Station is being stripped and abandoned. Three Colonial Movers are taking off the last "
                "technicians while the frigate Halyard stands guard. Red flight flies cover until the last mover jumps.",
                TEST)
    m.load_screen = "Load_SP-R1-M5.tga"
    m.background["sun_angles"] = "2.100000 5.100000 0.800000"
    STATION = (0.0, 0.0, 0.0)
    m.player_wing("Red", (600.0, 400.0, -2600.0), STATION, ["Shadow", "Flask"], guard='ai-guard "Halyard" 60')
    m.ship("Armistice Station", "Armistice Station", "Friendly", STATION, (0.0, 0.0, 5000.0), arrival="( true )",
           flags='( "cargo-known" "no-shields" "no-arrival-warp" "invulnerable" "don\'t-collide-invisible" )',
           flags2='( "no-subspace-drive" )', shields=0, score=0)
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", (-1400.0, 200.0, -900.0), STATION, arrival="( true )",
           departure='( is-event-true-delay "Last Away" 20 )', flags=CAPITAL_FLAGS, shields=0, score=600)
    for name, pos, ev in [("Tern", (900.0, -300.0, -700.0), "Mover 1 Away"), ("Gull", (-600.0, 500.0, 900.0), "Mover 2 Away"),
                          ("Petrel", (800.0, 300.0, 1200.0), "Last Away")]:
        m.ship(name, "Colonial Mover", "Friendly", pos, offset(pos, 0.0, 0.0, 4000.0), arrival="( true )",
               departure='( is-event-true-delay "%s" 4 )' % ev, ai_goals="ai-play-dead 100", flags=CIVIL_FLAGS,
               shields=0, score=200, cargo="Technicians")

    m.cylon_wing("Hound", "Raider", 4, (3000.0, 700.0, 2500.0), STATION, '( is-event-true-delay "Hound Cue" 0 )',
                 'ai-chase "Tern" 60')
    m.cylon_wing("Lancer", "Heavy Raider", 2, (-3200.0, -500.0, 3000.0), STATION, '( is-event-true-delay "Lancer Cue" 0 )',
                 'ai-chase "Gull" 90', spacing=150.0, score=35)
    m.cylon_wing("Fang", "Advanced Raider", 3, (2600.0, -800.0, -2400.0), STATION, '( is-event-true-delay "Lancer Cue" 10 )',
                 'ai-chase "Halyard" 70', score=20)
    m.cylon_wing("Swarm", "Raider", 5, (0.0, 1800.0, 3600.0), STATION, '( is-event-true-delay "Swarm Cue" 0 )',
                 'ai-chase "Petrel" 60')

    m.message("HQ Orders", "Red flight, three movers are loading the last crews off Armistice Station. Each one jumps as soon "
              "as it's full. Keep them alive. Halyard has the station covered.")
    m.message("Halyard Hail", "Halyard here, Red Leader. Ostrava again. We'll keep the big stuff off. Watch the movers.")
    m.message("S Hounds", "Raiders inbound on the Tern!")
    m.message("Tern Away", "Tern is full and jumping. Thirty souls aboard. Thank you, Vipers.")
    m.message("F Lancers", "Heavy Raiders going for the Gull, boarding craft by the look of them!")
    m.message("Gull Away", "Gull loaded and away!")
    m.message("S Swarm", "Big swarm coming in from above, they want the last mover!")
    m.message("Petrel Away", "Petrel jumping, that's everyone off the station!")
    m.message("HQ Win", "All three movers are clear and the Halyard is following them. Armistice Station is empty. Come home, Red flight.")
    m.message("HQ Mover Lost", "We've lost a mover. Gods. Keep the others alive.")
    m.message("HQ Halyard Lost", "The Halyard is gone! Red flight, cover the movers and get them out!")

    m.event("Orders Msg", '( when ( true ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Halyard Msg", '( when ( is-event-true-delay "Orders Msg" 14 ) ( send-message "Halyard" "High" "Halyard Hail" ) )')
    m.event("Hound Cue", '( when ( is-event-true-delay "Halyard Msg" 8 ) ( do-nothing ) )')
    m.event("Hound Msg", '( when ( has-arrived-delay 3 "Hound" ) ( send-message "Red 2" "High" "S Hounds" ) )')
    m.event("Mover 1 Away", '( when ( is-event-true-delay "Hound Cue" 60 ) ( send-message "Tern" "High" "Tern Away" ) )')
    m.event("Lancer Cue", '( when ( is-event-true-delay "Mover 1 Away" 10 ) ( do-nothing ) )')
    m.event("Lancer Msg", '( when ( has-arrived-delay 3 "Lancer" ) ( send-message "Red 3" "High" "F Lancers" ) )')
    m.event("Mover 2 Away", '( when ( is-event-true-delay "Lancer Cue" 65 ) ( send-message "Gull" "High" "Gull Away" ) )')
    m.event("Swarm Cue", '( when ( is-event-true-delay "Mover 2 Away" 10 ) ( do-nothing ) )')
    m.event("Swarm Msg", '( when ( has-arrived-delay 3 "Swarm" ) ( send-message "Red 2" "High" "S Swarm" ) )')
    m.event("Last Away", '( when ( is-event-true-delay "Swarm Cue" 70 ) ( send-message "Petrel" "High" "Petrel Away" ) )')
    m.event("Win", '( when ( has-departed-delay 2 "Halyard" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Mover Lost", '( when ( or ( is-destroyed-delay 1 "Tern" ) ( is-destroyed-delay 1 "Gull" ) ( is-destroyed-delay 1 "Petrel" ) ) '
                          '( send-message "#Command" "High" "HQ Mover Lost" ) )')
    m.event("All Movers Lost", '( when ( is-destroyed-delay 1 "Tern" "Gull" "Petrel" ) ( do-nothing ) )')
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    fail_end(m, ["All Movers Lost"])

    m.goal("Primary", "Evacuate the station", "Get at least two movers away",
           '( or ( has-departed-delay 0 "Tern" "Gull" ) ( has-departed-delay 0 "Tern" "Petrel" ) ( has-departed-delay 0 "Gull" "Petrel" ) )', 100)
    m.goal("Secondary", "Nobody left behind", "Get all three movers away", '( has-departed-delay 0 "Tern" "Gull" "Petrel" )', 50)
    m.goal("Secondary", "Protect the Halyard", "Keep the frigate Halyard alive", '( is-event-true-delay "Win" 0 )', 50)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "Armistice Station is a dead hulk now, but everyone who worked on it is alive. The Halyard's crew have taken "
              "to calling Red flight their lucky charm.",
              "Each wave goes for a different mover. Watch which one they are heading for and get there first.")
    m.debrief('( is-event-true-delay "All Movers Lost" 0 )',
              "None of the movers got away. The station's last crew died with it.",
              "Let the Halyard handle the Advanced Raiders that go for her and stay with the movers.")
    return m


# ==============================================================================================================
def hunters_moon():
    m = Mission("Hunter's Moon",
                "A Cylon raiding group has been picking off fleet stragglers from somewhere near the Erebus asteroid cluster. "
                "The frigate Halyard will sit in the open as bait. When they come for her, Red flight springs the trap.",
                TEST)
    m.load_screen = "Load_SP-R1-M6.tga"
    m.background["sun_angles"] = "3.300000 2.000000 4.900000"
    HALYARD = (0.0, 0.0, 0.0)
    START = (-2500.0, 900.0, -1500.0)
    m.player_wing("Red", START, HALYARD, ["Shadow", "Flask"], guard="ai-chase-any 50")
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", HALYARD, (0.0, 0.0, 5000.0), arrival="( true )",
           departure='( is-event-true-delay "Halyard Jump" 15 )', flags=CAPITAL_FLAGS, shields=0, score=600)
    rock_flags = ('( "protect-ship" "no-shields" "invulnerable" "hidden-from-sensors" "stealth" '
                  '"friendly-stealth-invisible" "don\'t-collide-invisible" )')
    for i, pos in enumerate([(-2300.0, 700.0, -1100.0), (-1800.0, 1100.0, -1900.0), (2400.0, -600.0, 2600.0),
                             (2900.0, 200.0, 1800.0), (-600.0, -1400.0, 3200.0), (1500.0, 1600.0, -2500.0)]):
        m.ship("Erebus %d" % (i + 1), "Asteroid R1", "Friendly", pos, offset(pos, 0.2, 0.8, 0.4), arrival="( true )",
               flags=rock_flags, score=0)

    m.cylon_wing("Stalker", "Raider", 4, (2600.0, -400.0, 2900.0), HALYARD, '( is-event-true-delay "Bait Taken" 0 )',
                 'ai-chase "Halyard" 70')
    m.cylon_wing("Reaver", "Heavy Raider", 3, (-1800.0, -1200.0, 3600.0), HALYARD, '( is-event-true-delay "Reaver Cue" 0 )',
                 'ai-chase "Halyard" 90', spacing=150.0, score=35)
    m.cylon_wing("Shade", "Advanced Raider", 3, (3200.0, 900.0, -900.0), START, '( is-event-true-delay "Reaver Cue" 8 )',
                 "ai-chase-any 70", score=20)
    m.ship("Nemesis", "Basestar", "Hostile", (5000.0, 1200.0, 9000.0), HALYARD, arrival='( is-event-true-delay "Basestar Cue" 0 )',
           ai_goals='ai-chase "Halyard" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Horde", "Raider", 5, (4200.0, 1000.0, 7600.0), HALYARD, '( is-event-true-delay "Basestar Cue" 8 )',
                 "ai-chase-any 60")

    m.message("HQ Orders", "Red flight, stay in the rocks and keep quiet. Halyard is sitting out there with her lights on. "
              "When the raiders go for her, hit them from behind.")
    m.message("Halyard Hail", "Halyard, ready. This is the strangest order I've ever followed. Don't be late, Red Leader.")
    m.message("F Contact", "Contacts! Raiders going for the Halyard. They took the bait!")
    m.message("Halyard Flak", "Taking fire! All batteries, flak! Red flight, they're yours!")
    m.message("S Reavers", "Heavy Raiders from below, torpedo profile! They're going for the frigate!")
    m.message("F Shades", "Advanced Raiders coming after us! Guess they found the trap.")
    m.message("HQ Basestar", "DRADIS, basestar! The raiding group has a mothership after all. Halyard, spool your FTL.")
    m.message("Halyard Spool", "Spooling. Sixty seconds. Keep them off our engines.")
    m.message("HQ Win", "Halyard has jumped. The raiding group is gutted and we know where its basestar hides. Well done, Red flight.")
    m.message("HQ Halyard Lost", "The Halyard is gone. The bait got eaten. Break off, Red flight.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 2 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Halyard Msg", '( when ( is-event-true-delay "Orders Msg" 14 ) ( send-message "Halyard" "High" "Halyard Hail" ) )')
    m.event("Bait Taken", '( when ( is-event-true-delay "Halyard Msg" 20 ) ( do-nothing ) )')
    m.event("Contact Msg", '( when ( has-arrived-delay 3 "Stalker" ) ( send-message "Red 3" "High" "F Contact" ) )')
    m.event("Flak Msg", '( when ( has-arrived-delay 14 "Stalker" ) ( send-message "Halyard" "High" "Halyard Flak" ) )')
    m.event("Reaver Cue", '( when ( is-event-true-delay "Bait Taken" 60 ) ( do-nothing ) )')
    m.event("Reaver Msg", '( when ( has-arrived-delay 3 "Reaver" ) ( send-message "Red 2" "High" "S Reavers" ) )')
    m.event("Shade Msg", '( when ( has-arrived-delay 3 "Shade" ) ( send-message "Red 3" "High" "F Shades" ) )')
    if not TEST:
        m.event("Guard Off", '( when ( is-event-true-delay "Reaver Cue" 20 ) ( ship-no-guardian "Halyard" ) )')
    m.event("Basestar Cue", '( when ( is-event-true-delay "Reaver Cue" 70 ) ( do-nothing ) )')
    m.event("Basestar Msg", '( when ( has-arrived-delay 3 "Nemesis" ) ( send-message "#Command" "High" "HQ Basestar" ) )')
    m.event("Spool Msg", '( when ( is-event-true-delay "Basestar Msg" 6 ) ( send-message "Halyard" "High" "Halyard Spool" ) )')
    m.event("Halyard Jump", '( when ( is-event-true-delay "Spool Msg" 50 ) ( do-nothing ) )')
    m.event("Win", '( when ( has-departed-delay 2 "Halyard" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    fail_end(m, ["Halyard Lost"])

    m.goal("Primary", "Spring the trap", "Protect the Halyard until she jumps", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Gut the raiding group", "Destroy most of the Raiders and Heavy Raiders",
           '( percent-ships-destroyed 70 "Stalker" "Reaver" "Shade" )', 100)
    m.goal("Bonus", "No torpedo hits", "Destroy all three Heavy Raiders",
           '( is-destroyed-delay 0 "Reaver 1" "Reaver 2" "Reaver 3" )', 30)

    m.debrief('( is-event-true-delay "Win" 0 )',
              "The raiders that have been killing stragglers for weeks are wreckage in the Erebus cluster, and we know where "
              "their basestar comes from. The Halyard will want a less exciting job next time.",
              "Hit the Raiders while they are busy with the frigate. They don't watch their backs.")
    m.debrief('( is-event-true-delay "Halyard Lost" 0 )',
              "We lost the Halyard and her crew. The trap was sound, the timing was not.",
              "Come out of the rocks as soon as the Raiders commit to the frigate, and save missiles for the Heavy Raiders.")
    return m


# ==============================================================================================================
def fleet_anchorage():
    """Peaceful free flight around the fleet, for testing the flight controls. No enemies, nothing to fail."""
    m = Mission("Fleet Anchorage",
                "The fleet is at anchor in a quiet system. No enemies, no orders, no clock. Take a Viper out and fly around the "
                "battlestar, the frigate, the tanker and the liners. Leave whenever you like.",
                True)	# True = invulnerable player
    m.load_screen = "Load_SP-R1-M1.tga"
    m.background["sun_angles"] = "2.600000 1.300000 5.300000"
    m.player_wing("Red", (900.0, 150.0, -1800.0), (0.0, 0.0, 0.0), [], guard="ai-chase-any 50")
    idle = "( \"cargo-known\" \"no-shields\" \"no-arrival-warp\" \"don't-collide-invisible\" )"
    still = '( "immobile" )'
    m.ship("Theseus", "Battlestar Sobek Class", "Friendly", (0.0, 0.0, 0.0), (0.0, 0.0, 5000.0), arrival="( true )",
           flags=idle, flags2=still, shields=0, score=0)
    m.ship("Sabazius", "Frigate Bolitho Class", "Friendly", (-1300.0, 250.0, 900.0), (0.0, 0.0, 5000.0), arrival="( true )",
           flags=idle, flags2=still, shields=0, score=0)
    m.ship("Prometheus", "Prometheus", "Friendly", (1500.0, -200.0, 1400.0), (0.0, 0.0, 5000.0), arrival="( true )",
           flags=idle, flags2=still, shields=0, score=0)
    for name, cls, pos in [("Keplaw", "Gemenon Freighter", (-2100.0, -300.0, -700.0)), ("Pixie", "Gemenon Freighter", (2300.0, 400.0, -500.0)),
                           ("Boa's Journey", "Colonial Mover", (400.0, 600.0, 2200.0)), ("Allsop", "Colonial Mover", (-700.0, -500.0, 2600.0)),
                           ("Golden Eagle", "Gemenon Traveler", (-2500.0, 350.0, 1900.0)), ("Pilgrim Mercy", "Intersun Passenger Cruiser", (2800.0, -100.0, 2300.0))]:
        m.ship(name, cls, "Friendly", pos, offset(pos, 0.0, 0.0, 4000.0), arrival="( true )", flags=idle, flags2=still,
               shields=0, score=0)
    rock_flags = ('( "protect-ship" "no-shields" "invulnerable" "hidden-from-sensors" "stealth" '
                  '"friendly-stealth-invisible" "don\'t-collide-invisible" )')
    for i, pos in enumerate([(-3400.0, 500.0, -1500.0), (3500.0, -400.0, -2200.0), (-3000.0, -800.0, 3400.0), (3200.0, 700.0, 3800.0),
                             (0.0, 1500.0, -3300.0), (600.0, -1600.0, 3600.0)]):
        m.ship("Rock %d" % (i + 1), "Asteroid R1", "Friendly", pos, offset(pos, 0.5, 0.3, 0.8), arrival="( true )",
               flags=rock_flags, score=0)
    for i, pos in enumerate([(2900.0, 100.0, -2500.0), (3100.0, 200.0, -2300.0), (3300.0, 0.0, -2100.0), (3500.0, 150.0, -1900.0)]):
        m.ship("Drone %d" % (i + 1), "Cylotron Mark IX Drone", "Neutral", pos, offset(pos, -1.0, 0.0, 1.0), arrival="( true )",
               flags=idle, flags2=still, hull=100, shields=0, score=0)
    m.message("HQ Welcome", "Red 1, Theseus. Nothing on DRADIS and no orders. The fleet is yours to look at. Fly around, "
              "stretch the Viper's legs. Jump out whenever you want.")
    m.event("Welcome Msg", '( when ( true ) ( send-message "#Command" "High" "HQ Welcome" ) )')
    m.goal("Secondary", "Fly around the fleet", "Fly past the battlestar, the frigate and the tanker (optional)",
           '( or ( < ( distance "Red 1" "Theseus" ) 600 ) ( < ( distance "Red 1" "Sabazius" ) 400 ) ( < ( distance "Red 1" "Prometheus" ) 400 ) )', 10)
    m.goal("Secondary", "Target practice", "Shoot the four parked training drones to the east (optional)",
           '( is-destroyed-delay 0 "Drone 1" "Drone 2" "Drone 3" "Drone 4" )', 10)
    m.debrief('( true )', "Quiet flight. The deck crew say the Viper came back without a scratch, as usual.",
              "Nothing to fix. Come back any time you want to test the controls.")
    return m


CAMPAIGN = """$Name: Thunderlords Patrol Log
$Type: single
+Description:
 XSTR("Missions added by the Linux/VR port: Vigil at the Ashen Veil, a fuel convoy, a mining mover lost in an asteroid field, a frigate shepherding refugee liners, the evacuation of Armistice Station, a hunt for lost medicine, a Raptor recon run, a last stand while Theseus repairs her FTL, a frigate used as bait and an ambush on a nuclear strike.", -1)
$end_multi_text
$Flags: 0


+Starting Ships: ( "Viper Mark VII"  "Viper Mark VIIe"  "Assault Raptor" )

+Starting Weapons: ( "MEC-A6"  "Training MEC-A6"  "GBK-6"  "HD-70 Lightning Javelin"  "TM-7 Pyro Javelin"  "HD-51 Arbalest"  "CTD-17 Jester"  "HS-24 Lance"  "HS-48 Spear"  "AGM-41 Whiplash"  "GBU-102 Tercio"  "TGB-102 Petardo"  "N4 Nessus" )

"""

# ==============================================================================================================
# Extra radio chatter: (after event, delay s, sender, text). A line only plays while its sender is alive.
CHATTER = {
    "XM-Tylium.fs2": [
        ("Cassia Msg", 8, "Red 2", "Shadow here. Keep it tight, Flask. Every drop on that tanker is a Viper sortie next month."),
        ("Cassia Msg", 16, "Red 3", "Copy. Funny, my last job before the war was hauling fuel. Never thought I'd miss it."),
        ("Jackal Msg", 25, "Cassia", "Cassia to escort, I can hear them on our hull frequency. Please tell me that's your guns."),
        ("Hound Msg", 20, "Red 2", "These advanced models break hard to port every time. Lead them and they're yours."),
        ("Mauler Msg", 12, "Halyard", "Halyard to Red flight, our flak has the Heavies bracketed. Push them into it."),
        ("Convoy Jump", 4, "Red 3", "Lords, I'll be glad to see the back of that tanker. Nothing personal, Cassia."),
    ],
    "XM-Hollow.fs2": [
        ("Rocks Msg", 6, "Red 2", "DRADIS is useless in here, too much iron in the rocks. Eyes open."),
        ("Kestrel Msg", 6, "Red 3", "Eleven people sitting dark for six hours. I don't know how they kept their heads."),
        ("Ambush Msg", 18, "Kestrel", "We can see your guns from here! Gods bless you, keep shooting!"),
        ("Boarders Msg", 8, "Red 2", "Heavies inbound. Forget the small ones, they want the mover's crew alive."),
        ("Brutes Down", 3, "Red 3", "Splash two boarders! That's the last of them!"),
        ("Lantern Msg", 10, "Kestrel", "Lantern, we're at the airlock. Some of the kids are scared of the noise, go easy."),
    ],
    "XM-Shepherd.fs2": [
        ("Halyard Msg", 8, "Aster", "Liner Aster here. We have four hundred aboard and two working toilets. Please hurry."),
        ("Halyard Msg", 16, "Red 2", "You heard the lady, Red flight. Nobody's dying in Tessaly today."),
        ("Wolf Msg", 15, "Halyard", "Port batteries, track the lead Raider. Red flight, they're turning into your guns."),
        ("Jackal Msg", 14, "Briony", "Briony to Halyard, they're shooting at our engines! We're losing pressure in section four!"),
        ("Ram Msg", 10, "Red 3", "I've got the left Heavy. Shadow, take the right one before it lines up."),
        ("Flock Jump", 4, "Aster", "Thank you, Vipers. We'll tell the children about you."),
    ],
    "XM-Station.fs2": [
        ("Halyard Msg", 8, "Red 2", "Armistice Station. My father worked here when I was a kid. Strange to see it empty."),
        ("Mover 1 Away", 6, "Halyard", "One down, two to go. Ostrava to all movers, load faster, we're not staying for dinner."),
        ("Lancer Msg", 12, "Gull", "Gull here, I can see those Heavies from the bridge! Don't let them dock with us!"),
        ("Mover 2 Away", 8, "Red 3", "Two away. I'm almost out of missiles, switching to guns."),
        ("Swarm Msg", 14, "Petrel", "Petrel, last of the techs coming aboard now. Thirty seconds!"),
        ("Last Away", 6, "Red 2", "Goodbye, old girl. Somebody should have at least turned off the lights."),
    ],
    "XM-Reckoning.fs2": [
        ("Scan Msg", 10, "Red 3", "Four pods and one of them is the medicine. I hate guessing games."),
        ("Scav Msg", 14, "Red 2", "They're stripping the pods! Shoot them off before they take the wrong one!"),
        ("Found", 6, "#Command", "Theseus copies, antibiotics confirmed in Pod Charlie. Protect it at all costs."),
        ("Lantern Msg", 12, "Red 3", "Lantern, I'm on your six. Do your thing."),
        ("Hauler Msg", 10, "Lantern 3", "Halfway hooked up. Whatever you're doing out there, keep doing it!"),
        ("Lantern Out", 2, "Red 2", "That's the one. The sickbay is going to throw us a party."),
    ],
    "XM-DeepLook.fs2": [
        ("Shadow Msg", 12, "Red 3", "Flask here. First time I've ever escorted somebody toward a basestar on purpose."),
        ("Shadow Msg", 22, "Red 1", "Just keep the toasters off me and let me get my pictures."),
        ("Close Msg", 8, "Red 2", "Look at the hull. It's like it's breathing."),
        ("Waking", 7, "Red 3", "Lantern, burn! Don't look back, just burn!"),
        ("Run Msg", 14, "Red 1", "I've got two on my tail! Shadow, Flask, anyone!"),
        ("Fury Msg", 16, "Red 2", "Got him! Lantern, you're clear on the left, keep moving!"),
    ],
    "XM-Firebreak.fs2": [
        ("Ghost Msg", 8, "Blue 2", "Rook here. Four minutes. I've had longer showers."),
        ("Ember Msg", 18, "Red 2", "Splash one! They're coming in pairs, watch your wingman."),
        ("Cinder Msg", 10, "Blue 1", "Ghost to Red, I'm on the Heavy at the bottom. Take the top two."),
        ("Cinder Msg", 24, "#Command", "Damage control reports minor hull breach on deck seven. Keep them off us, pilots."),
        ("Basestar Msg", 8, "Red 3", "A basestar. Of course there's a basestar."),
        ("FTL Ready", 4, "Blue 2", "Rook to all Vipers, last one to the hangar buys the drinks."),
    ],
    "XM-Hunter.fs2": [
        ("Halyard Msg", 8, "Red 2", "Sitting in a rock waiting for Raiders. Feels like hunting with my uncle on Picon."),
        ("Halyard Msg", 16, "Red 3", "Your uncle hunted Cylons?"),
        ("Halyard Msg", 22, "Red 2", "He hunted ridge deer. Same principle. Patience, then everything at once."),
        ("Contact Msg", 8, "Red 2", "Wait for it. Let them commit to the frigate. Now! Go, go!"),
        ("Reaver Msg", 12, "Halyard", "Torpedo in the water, port side! Brace, brace!"),
        ("Spool Msg", 14, "Red 3", "They're throwing everything at her now. Stay on the Halyard!"),
    ],
    "XM-Anvil.fs2": [
        ("Halyard Msg", 8, "Blue 1", "Ghost here. Six nukes. Let's make sure none of them reach the fleet."),
        ("Picket Msg", 14, "Red 3", "Pickets are fast but they're not the target. Stay on the Heavies."),
        ("Moving Msg", 10, "Halyard", "Heavies changing course. Ostrava to all ships, they're running for the jump point."),
        ("Escort Msg", 10, "Blue 2", "Rook to Halyard, I've got two on your stern, coming around."),
        ("One Minute", 6, "Red 2", "One minute! Everyone on the Heavies, missiles if you've got them!"),
        ("One Minute", 30, "Halyard", "Thirty seconds to their jump. Whatever you have left, use it now!"),
    ],
}


def add_chatter(fname, m):
    for n, (after, delay, sender, text) in enumerate(CHATTER.get(fname, []), start=1):
        name = "Chatter %d" % n
        m.message(name, text)
        cond = '( is-event-true-delay "%s" %d )' % (after, delay)
        if not sender.startswith("#"):
            cond = '( and %s ( not ( is-destroyed-delay 0 "%s" ) ) )' % (cond, sender)
        m.event("Chatter %d Msg" % n, '( when %s ( send-message "%s" "Normal" "%s" ) )' % (cond, sender, name))


# ==============================================================================================================
def picket_line():
    m = Mission("Picket Line",
                "The frigate Halyard is holding a picket station at the edge of the fleet. Raiders are probing the line. "
                "Red flight screens her until the probe is over.",
                TEST)
    m.load_screen = "Load_SP-R1-M6.tga"
    m.background["sun_angles"] = "1.900000 4.200000 0.500000"
    HALYARD = (0.0, 0.0, 0.0)
    START = (-1800.0, 400.0, -1300.0)
    m.player_wing("Red", START, HALYARD, ["Shadow", "Flask"], guard="ai-chase-any 50")
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", HALYARD, (0.0, 0.0, 5000.0), arrival="( true )",
           flags=CAPITAL_FLAGS, shields=0, score=600)
    m.cylon_wing("Scout", "Raider", 4, (2600.0, 300.0, 3000.0), HALYARD, '( is-event-true-delay "Scout Cue" 0 )', 'ai-chase "Halyard" 70')
    m.cylon_wing("Spear", "Heavy Raider", 2, (-2400.0, -500.0, 3400.0), HALYARD, '( is-event-true-delay "Scouts Down" 5 )',
                 'ai-chase "Halyard" 90', spacing=150.0, score=35)

    m.message("HQ Orders", "Red flight, Halyard is on picket at the edge of the fleet. Raiders have been testing the line all night. "
              "Stay close to her and answer anything that comes in.")
    m.message("Halyard Hail", "Halyard, on station. Quiet so far. Which usually means it's about to be loud.")
    m.message("Scout Contact", "Four Raiders, bearing zero three zero, coming in fast. They're after the Halyard.")
    m.message("Halyard Guns", "Port battery, firing. Red flight, they're slipping past our flak. Take them.")
    m.message("Spear Contact", "Heavy Raiders, two of them, low and from the stern. They're carrying torpedoes.")
    m.message("HQ Win", "Picket line is clear. The Halyard took a few scratches and the Raiders took the worst of it. Good work.")
    m.message("HQ Halyard Lost", "The Halyard is gone. The picket line is open. Break off and return to the fleet.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 2 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Halyard Msg", '( when ( is-event-true-delay "Orders Msg" 10 ) ( send-message "Halyard" "High" "Halyard Hail" ) )')
    m.event("Scout Cue", '( when ( is-event-true-delay "Halyard Msg" 25 ) ( do-nothing ) )')
    m.event("Contact Msg", '( when ( has-arrived-delay 3 "Scout" ) ( send-message "Red 3" "High" "Scout Contact" ) )')
    m.event("Guns Msg", '( when ( has-arrived-delay 12 "Scout" ) ( send-message "Halyard" "High" "Halyard Guns" ) )')
    m.event("Scouts Down", '( when ( percent-ships-destroyed 75 "Scout" ) ( do-nothing ) )')
    m.event("Spear Msg", '( when ( has-arrived-delay 3 "Spear" ) ( send-message "Red 2" "High" "Spear Contact" ) )')
    m.event("Win", '( when ( and ( is-event-true-delay "Spear Msg" 0 ) ( percent-ships-destroyed 100 "Spear" ) ) '
                   '( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    fail_end(m, ["Halyard Lost"])

    m.goal("Primary", "Hold the picket", "Keep the Halyard alive and destroy the Raiders", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Bonus", "Stop the torpedoes", "Destroy both Heavy Raiders", '( is-destroyed-delay 0 "Spear 1" "Spear 2" )', 30)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "The Raiders that probed the picket are wreckage and the Halyard is still on station. The line held.",
              "Take the Raiders while they are busy with the frigate's flak, then turn on the Heavies before they release.")
    m.debrief('( is-event-true-delay "Halyard Lost" 0 )',
              "We lost the Halyard, and with her the western picket.",
              "Stay inside the frigate's flak and kill the Heavy Raiders before they get a torpedo run.")
    return m


# ==============================================================================================================
def long_tow():
    m = Mission("Long Tow",
                "The mover Pilgrim Mercy lost her FTL drive and is limping to the rendezvous on thrusters. The frigate Halyard rides "
                "alongside. Keep the Cylons off them until the mover can jump.",
                TEST)
    m.load_screen = "Load_SP-R1-M5.tga"
    m.background["sun_angles"] = "0.700000 5.100000 5.800000"
    MOVER, HALYARD = (0.0, 0.0, 0.0), (500.0, -100.0, -500.0)
    END = (150.0, 80.0, 7000.0)
    m.player_wing("Red", (-300.0, 250.0, -1700.0), END, ["Shadow", "Flask"], guard='ai-guard "Pilgrim Mercy" 60')
    jump = '( is-event-true-delay "Tow Jump" 10 )'
    m.ship("Pilgrim Mercy", "Colonial Mover", "Friendly", MOVER, END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Tow Lane" 40', flags=CIVIL_FLAGS, hull=100, shields=0, score=300)
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", HALYARD, END, arrival="( true )", departure=jump,
           ai_goals='ai-waypoints-once "Tow Lane" 40', flags=CAPITAL_FLAGS, shields=0, score=600)
    m.waypoint_list("Tow Lane", [(100.0, 40.0, 2200.0), (150.0, 60.0, 4600.0), END])

    m.cylon_wing("Hawk", "Raider", 4, (2800.0, 200.0, 1500.0), MOVER, '( is-event-true-delay "Hawk Cue" 0 )', 'ai-chase "Pilgrim Mercy" 70')
    m.cylon_wing("Mauler", "Heavy Raider", 2, (-2600.0, -400.0, 3800.0), MOVER, '( is-event-true-delay "Mauler Cue" 0 )',
                 'ai-chase "Pilgrim Mercy" 90', spacing=150.0, score=35)
    m.cylon_wing("Kite", "Advanced Raider", 3, (2400.0, 900.0, 5200.0), MOVER, '( is-event-true-delay "Kite Cue" 0 )',
                 "ai-chase-any 70", score=20)

    m.message("HQ Orders", "Red flight, Pilgrim Mercy has no FTL and she's doing all of nine hundred metres a minute. "
              "The Halyard is riding with her. Keep the Cylons off until the drive comes back.")
    m.message("Mercy Hail", "Pilgrim Mercy. Engineers say ten minutes to bring the drive up. We don't have ten minutes, do we?")
    m.message("Hawk Contact", "Raiders! Four of them, bearing two seven zero. They're going for the mover.")
    m.message("Halyard Cover", "Halyard to Mercy, stay on the lane. Red flight, kill them before they reach her hull.")
    m.message("Mauler Contact", "Heavy Raiders from the stern! They want her engines.")
    m.message("Kite Contact", "Advanced Raiders ahead. They are circling to cut us off.")
    m.message("Mercy Ready", "Drive's up! Jumping in ten seconds. Thank you, Red flight, thank you all.")
    m.message("HQ Win", "Pilgrim Mercy and the Halyard are away. A hundred and forty souls on that mover will remember you.")
    m.message("HQ Mercy Lost", "We lost the Pilgrim Mercy. Break off, Red flight.")
    m.message("HQ Halyard Lost", "The Halyard is gone and the mover is alone. Break off, Red flight.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" "Pilgrim Mercy" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 2 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Mercy Msg", '( when ( is-event-true-delay "Orders Msg" 12 ) ( send-message "Pilgrim Mercy" "High" "Mercy Hail" ) )')
    m.event("Hawk Cue", '( when ( is-event-true-delay "Mercy Msg" 25 ) ( do-nothing ) )')
    m.event("Hawk Msg", '( when ( has-arrived-delay 3 "Hawk" ) ( send-message "Red 3" "High" "Hawk Contact" ) )')
    m.event("Cover Msg", '( when ( has-arrived-delay 14 "Hawk" ) ( send-message "Halyard" "High" "Halyard Cover" ) )')
    m.event("Mauler Cue", '( when ( is-event-true-delay "Hawk Cue" 70 ) ( do-nothing ) )')
    m.event("Mauler Msg", '( when ( has-arrived-delay 3 "Mauler" ) ( send-message "Red 2" "High" "Mauler Contact" ) )')
    m.event("Kite Cue", '( when ( is-event-true-delay "Mauler Cue" 55 ) ( do-nothing ) )')
    m.event("Kite Msg", '( when ( has-arrived-delay 3 "Kite" ) ( send-message "Red 3" "High" "Kite Contact" ) )')
    m.event("Drive Ready", '( when ( is-event-true-delay "Kite Msg" 55 ) ( send-message "Pilgrim Mercy" "High" "Mercy Ready" ) )')
    m.event("Tow Jump", '( when ( is-event-true-delay "Drive Ready" 2 ) ( do-nothing ) )')
    m.event("Win", '( when ( has-departed-delay 2 "Pilgrim Mercy" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Mercy Lost", '( when ( is-destroyed-delay 1 "Pilgrim Mercy" ) ( send-message "#Command" "High" "HQ Mercy Lost" ) )')
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    fail_end(m, ["Mercy Lost", "Halyard Lost"])

    m.goal("Primary", "Get the mover out", "Keep Pilgrim Mercy alive until she jumps", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Keep the Halyard", "The Halyard must survive", '( not ( is-destroyed-delay 0 "Halyard" ) )', 50)
    m.goal("Bonus", "No torpedo hits", "Destroy both Heavy Raiders", '( is-destroyed-delay 0 "Mauler 1" "Mauler 2" )', 30)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "Pilgrim Mercy is through with her passengers and the Halyard is intact. Slow ships win by having a good escort.",
              "Kill the Raiders before they reach the mover, the Heavies are the real threat to her engines.")
    m.debrief('( or ( is-event-true-delay "Mercy Lost" 0 ) ( is-event-true-delay "Halyard Lost" 0 ) )',
              "We lost the tow. Slow ships do not survive slow escorts.",
              "Intercept the Raiders ahead of the mover and keep your eyes on the Heavy Raiders in the stern.")
    return m


# ==============================================================================================================
def ghost_light():
    m = Mission("Ghost Light",
                "The Halyard keeps getting painted by something DRADIS cannot see. A stealthed Advanced Raider is shadowing her and "
                "reporting her position. Red flight has to find it by eye and kill it before it calls the basestar.",
                TEST)
    m.load_screen = "Load_SP-R1-M6.tga"
    m.background["sun_angles"] = "4.400000 1.100000 2.600000"
    HALYARD = (0.0, 0.0, 0.0)
    m.player_wing("Red", (-1500.0, 300.0, -1200.0), HALYARD, ["Shadow", "Flask"], guard="ai-chase-any 50")
    m.ship("Halyard", "Frigate Bolitho Class", "Friendly", HALYARD, (0.0, 0.0, 5000.0), arrival="( true )",
           flags=CAPITAL_FLAGS, shields=0, score=600)
    m.ship("Wraith", "Advanced Raider", "Hostile", (900.0, 300.0, 900.0), HALYARD, arrival="( true )",
           ai_goals='ai-chase "Halyard" 60', flags='( "hidden-from-sensors" "stealth" "no-arrival-message" )', score=100)
    m.ship("Nemesis", "Basestar", "Hostile", (4500.0, 900.0, 8500.0), HALYARD, arrival='( is-event-true-delay "Call Home" 0 )',
           ai_goals='ai-chase "Halyard" 80', ai_class="Lieutenant", flags='( "no-arrival-message" )', score=1500)
    m.cylon_wing("Hound", "Raider", 4, (4000.0, 600.0, 7600.0), HALYARD, '( is-event-true-delay "Call Home" 10 )', 'ai-chase "Halyard" 70')

    m.message("HQ Orders", "Red flight, the Halyard says something is painting her and DRADIS shows nothing. A stealthed scout is shadowing her. "
              "Find it by eye, you have three minutes before it reports her position.")
    m.message("Halyard Hail", "Halyard here. Every few seconds I feel it, a little flicker on our hull. Look for engine glow, Red leader.")
    m.message("Hint One", "Nothing on DRADIS. It has to be close. Look for the engine glow against the stars.")
    m.message("Hint Two", "Sixty seconds. If it calls home, we'll have a basestar on us.")
    m.message("Wraith Found", "Got it! There, low and to port of the Halyard. It's turning away.")
    m.message("HQ Win", "The scout is down and nothing reached the basestar. The Halyard can stop flinching now. Well done.")
    m.message("Called Home", "It jumped a message out. DRADIS, basestar, inbound! Halyard, spool your FTL!")
    m.message("HQ Halyard Lost", "The Halyard is gone. Break off, Red flight.")

    m.event("Start", '( when ( true ) ( ship-guardian-threshold 20 "Halyard" ) )')
    m.event("Orders Msg", '( when ( is-event-true-delay "Start" 2 ) ( send-message "#Command" "High" "HQ Orders" ) )')
    m.event("Halyard Msg", '( when ( is-event-true-delay "Orders Msg" 12 ) ( send-message "Halyard" "High" "Halyard Hail" ) )')
    m.event("Hint One Msg", '( when ( is-event-true-delay "Halyard Msg" 55 ) ( send-message "Red 2" "High" "Hint One" ) )')
    m.event("Hint Two Msg", '( when ( is-event-true-delay "Halyard Msg" 120 ) ( send-message "Red 3" "High" "Hint Two" ) )')
    m.event("Call Home", '( when ( and ( is-event-true-delay "Halyard Msg" 180 ) ( not ( is-destroyed-delay 0 "Wraith" ) ) ) ( send-message "#Command" "High" "Called Home" ) )')
    m.event("Win", '( when ( is-destroyed-delay 2 "Wraith" ) ( send-message "#Command" "High" "HQ Win" ) )')
    win_end(m, "Win")
    m.event("Halyard Lost", '( when ( is-destroyed-delay 1 "Halyard" ) ( send-message "#Command" "High" "HQ Halyard Lost" ) )')
    fail_end(m, ["Halyard Lost"])

    m.goal("Primary", "Find the scout", "Destroy the stealthed Advanced Raider before it calls the basestar", '( is-event-true-delay "Win" 0 )', 100)
    m.goal("Primary", "Keep the Halyard", "The Halyard must survive", '( not ( is-destroyed-delay 0 "Halyard" ) )', 50)
    m.debrief('( is-event-true-delay "Win" 0 )',
              "The scout is wreckage and its report never left the system. The Halyard is safe for now.",
              "Stealth hides a ship from DRADIS, not from your eyes. Look for the engine glow.")
    m.debrief('( is-event-true-delay "Halyard Lost" 0 )',
              "We lost the Halyard. The scout was too well hidden.",
              "Circle the Halyard at a wide radius and watch the stars for engine glow, the scout stays close to her hull.")
    return m


# estimated play time and difficulty, shown in the Mission Simulator
META = {
    "XM-Tylium.fs2": ("~15 min", "Medium"), "XM-Hollow.fs2": ("~12 min", "Medium"), "XM-Shepherd.fs2": ("~14 min", "Medium"),
    "XM-Station.fs2": ("~14 min", "Medium"), "XM-Reckoning.fs2": ("~13 min", "Medium"), "XM-DeepLook.fs2": ("~11 min", "Hard"),
    "XM-Firebreak.fs2": ("~10 min", "Hard"), "XM-Hunter.fs2": ("~13 min", "Medium"), "XM-Anvil.fs2": ("~12 min", "Hard"),
    "XM-Picket.fs2": ("~8 min", "Easy"), "XM-Tow.fs2": ("~11 min", "Medium"), "XM-Ghost.fs2": ("~8 min", "Medium"),
    "XM-Fleet.fs2": ("no time limit", "None"), "XM-Range.fs2": ("~10 min", "Easy"),
    "XM-Watch.fs2": ("~28 min", "Hard"), "XM-Convoy.fs2": ("~25 min", "Hard"), "XM-Hulks.fs2": ("~26 min", "Medium"),
    "XM-Hammerfall.fs2": ("~24 min", "Hard"), "XM-Armistice.fs2": ("~32 min", "Very Hard"),
}

if __name__ == "__main__":
    import long_missions
    long_missions.G.update(TEST=TEST, CIVIL=CIVIL_FLAGS, CAPITAL=CAPITAL_FLAGS, win_end=win_end, fail_end=fail_end)
    missions = [("XM-Tylium.fs2", tylium_run()), ("XM-Hollow.fs2", hollow_rock()), ("XM-Shepherd.fs2", iron_shepherd()),
                ("XM-Station.fs2", station_keeping()), ("XM-Reckoning.fs2", dead_reckoning()), ("XM-DeepLook.fs2", deep_look()),
                ("XM-Firebreak.fs2", firebreak()), ("XM-Hunter.fs2", hunters_moon()), ("XM-Anvil.fs2", hammer_and_anvil()),
                ("XM-Picket.fs2", picket_line()), ("XM-Tow.fs2", long_tow()), ("XM-Ghost.fs2", ghost_light()),
                ("XM-Watch.fs2", long_missions.long_watch()), ("XM-Convoy.fs2", long_missions.cold_convoy()),
                ("XM-Hulks.fs2", long_missions.dead_hulks()), ("XM-Hammerfall.fs2", long_missions.hammerfall()),
                ("XM-Armistice.fs2", long_missions.last_stand()),
                ("XM-Range.fs2", long_missions.gunnery_range()),
                ("XM-Fleet.fs2", fleet_anchorage())]
    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "overlay", "diaspora_fixes", "data", "voice",
                                 "special", "voice_manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    for fname, mission in missions:
        add_chatter(fname, mission)
        if fname in META:
            mission.desc = "[[Duration: %s | Difficulty: %s]] %s" % (META[fname][0], META[fname][1], mission.desc)
        mission.waves = manifest.get(fname, {})
        print(mission.write(os.path.join(OUT, fname)), "| voiced:", len(mission.waves))
    order = ["XM-Vigil.fs2"] + [f for f, _ in missions]
    camp = CAMPAIGN
    for i, fname in enumerate(order):
        nxt = '( end-of-campaign )' if i == len(order) - 1 else '( next-mission "%s" )' % order[i + 1]
        camp += "$Mission: %s\n+Flags: 0\n+Main Hall: 0\n+Formula: ( cond\n   ( ( true ) %s )\n)\n\n+Level: %d\n+Position: 0\n\n" % (
            fname, nxt, i)
    camp += "#End\n"
    with open(os.path.join(OUT, "XM-Thunderlords.fc2"), "wb") as f:
        f.write(camp.replace("\n", "\r\n").encode("latin-1"))
    print("wrote", os.path.join(OUT, "XM-Thunderlords.fc2"), "with", len(order), "missions")
