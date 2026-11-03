"""Small FreeSpace Open mission (.fs2) writer for the Diaspora overlay missions.

Extracted from make_vigil.py so several missions can share it. Only the parts of the format these missions use are
covered: ships, wings, events, goals, waypoints, messages, debriefing and a background. Missions written with it load in
the Diaspora engine build (same sections and field order as XM-Vigil.fs2).
"""
import math

NL = "\r\n"

# standard loadouts
VIPER_GUNS = ["MEC-A6", "MEC-A6"]
VIPER_MISSILES = ["HD-70 Lightning Javelin", "HD-70 Lightning Javelin"]
WING_FLAGS = '( "no-arrival-music" "no-arrival-message" "no-arrival-warp" )'
CYLON_FLAGS = '( "no-shields" "no-arrival-warp" )'


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


def offset(p, dx=0.0, dy=0.0, dz=0.0):
    return (p[0] + dx, p[1] + dy, p[2] + dz)


class Mission:
    def __init__(self, name, desc, test=False):
        self.name = name
        self.desc = desc
        self.test = test
        self.objects = []
        self.wings = []
        self.events = []
        self.goals = []
        self.waypoints = []
        self.messages = []
        self.debriefs = []
        self.callsigns = []
        self.waves = {}		# message name -> voice file (voice_manifest.json)
        self.weapon_pool = [("MEC-A6", 26), ("HD-70 Lightning Javelin", 112), ("HD-51 Arbalest", 32)]
        self.background = dict(sun="Stars_Sun_YHaze", sun_angles="0.174533 5.689769 4.014254", sun_scale=8.0,
                               bitmaps=[("Stars_Neb_Blue02", "0.000000 5.497783 0.872664", 8, 8),
                                        ("Stars_Neb_Blue03", "5.672316 5.916661 1.134463", 8, 6),
                                        ("Stars_Neb_Blue01", "0.575958 0.000000 0.733038", 6, 8)],
                               ambient=8947070)
        self.load_screen = "Load_SP-R1-M4.tga"
        self.music = "10: Children of Humanity"

    # ---- content -----------------------------------------------------------------------------------------------
    def ship(self, name, cls, team, pos, face, arrival="( false )", departure="( false )", ai_goals=None,
             flags='( "cargo-known" )', flags2="( )", hull=100, shields=100, callsign=None, ai_class=None,
             velocity=None, primaries=None, secondaries=None, score=10, cargo="Nothing"):
        o = ["$Name: %s" % name, "$Class: %s" % cls]
        if callsign:
            o += ["$Callsign: %s" % callsign, ""]
            if callsign not in self.callsigns:
                self.callsigns.append(callsign)
        o.append("$Team: %s" % team)
        o.append("$Location: %s" % fmt3(pos))
        r, u, f = orient(pos, face)
        o += ["$Orientation:", "\t%s," % fmt3(r), "\t%s," % fmt3(u), "\t%s" % fmt3(f)]
        o.append("$AI Behavior: None")
        if ai_class:
            o.append("+AI Class: %s" % ai_class)
        if ai_goals:
            o.append("$AI Goals: ( goals ( %s ) )" % ai_goals)
        o.append('$Cargo 1:  %s' % ('XSTR("Nothing", 150)' if cargo == "Nothing" else xstr(cargo)))
        if velocity:
            o.append("+Initial Velocity: %d" % velocity)
        o += ["+Initial Hull: %d" % hull, "+Initial Shields: %d" % shields, "+Subsystem: Pilot"]
        if primaries:
            o.append("+Primary Banks: ( %s )" % " ".join('"%s"' % p for p in primaries))
        if secondaries:
            o.append("+Secondary Banks: ( %s )" % " ".join('"%s"' % p for p in secondaries))
        o += ["$Arrival Location: Hyperspace", "$Arrival Cue: %s" % arrival,
              "$Departure Location: Hyperspace", "$Departure Cue: %s" % departure,
              "$Determination: 10", "+Flags: %s" % flags, "+Flags2: %s" % flags2, "+Respawn priority: 0",
              "+Orders Accepted: 0\t\t;! note that this is a bitfield!!!", "+Group: 0", "+Use Table Score:",
              "+Score: %d" % score]
        self.objects.append(o)

    def player_wing(self, name, start, face, callsigns, guard=None, player_class="Viper Mark VII",
                    player_primaries=None, player_secondaries=None):
        """Player flight: the player is <name> 1 (a Viper unless player_class says otherwise), the wingmen fly Vipers."""
        flags = '( "cargo-known" "player-start" "don\'t-collide-invisible"%s )' % (' "invulnerable"' if self.test else '')
        wing_flags = '( "cargo-known" "don\'t-collide-invisible" )'
        ships = []
        for i in range(len(callsigns) + 1):
            sname = "%s %d" % (name, i + 1)
            pos = offset(start, (i - len(callsigns) / 2.0) * 60.0, 0.0, -10.0 * (i > 0))
            if i == 0:
                self.ship(sname, player_class, "Friendly", pos, face, flags=flags,
                          primaries=player_primaries or VIPER_GUNS, secondaries=player_secondaries or VIPER_MISSILES,
                          score=12)
            else:
                self.ship(sname, "Viper Mark VII", "Friendly", pos, face, flags=wing_flags, callsign=callsigns[i - 1],
                          ai_class="Lieutenant", primaries=VIPER_GUNS, secondaries=VIPER_MISSILES)
            ships.append(sname)
        self.wing(name, ships, "( true )", goals=guard or "ai-chase-any 50", flags=WING_FLAGS)
        return ships

    def cylon_wing(self, name, cls, count, center, face, arrival, goals, spacing=80.0, score=10):
        ships = []
        for i in range(count):
            off = (i - (count - 1) / 2.0) * spacing
            sname = "%s %d" % (name, i + 1)
            self.ship(sname, cls, "Hostile", offset(center, off, 0.0, off * 0.5), face, ai_class="Lieutenant",
                      flags=CYLON_FLAGS, flags2='( "no-ets" )', velocity=33, score=score)
            ships.append(sname)
        self.wing(name, ships, arrival, goals=goals, flags=WING_FLAGS)
        return ships

    def wing(self, name, ships, arrival, departure="( false )", goals="ai-chase-any 50", flags=WING_FLAGS):
        self.wings.append(dict(name=name, ships=ships, arrival=arrival, departure=departure, goals=goals, flags=flags))

    def event(self, name, formula):
        self.events.append((name, formula))

    def goal(self, typ, name, text, formula, score):
        self.goals.append((typ, name, text, formula, score))

    def waypoint_list(self, name, points):
        self.waypoints.append((name, points))

    def message(self, name, text):
        self.messages.append((name, text))

    def debrief(self, formula, text, recommendation):
        self.debriefs.append((formula, text, recommendation))

    # ---- output ------------------------------------------------------------------------------------------------
    def write(self, path, author="Claude (extra missions for the Diaspora port)", created="11/02/26 at 12:00:00"):
        out = []
        w = out.append
        w("#Mission Info")
        w("")
        w('$Version: 0.10')
        w('$Name:  %s' % xstr(self.name))
        w("$Author: %s" % author)
        w("$Created: %s" % created)
        w("$Modified: %s" % created)
        w("$Notes:")
        w("Generated by tools/make_extra_missions.py (non-commercial, CC BY-NC-SA with the Diaspora content).")
        w("$End Notes:")
        w("")
        w("$Mission Desc:")
        w(" %s" % xstr(self.desc))
        w("$end_multi_text")
        w("")
        w("+Game Type Flags: 1")
        w("")
        w("+Flags: 262144")
        w("+Fog Near Mult: 1.000000")
        w("")
        w("+Fog Far Mult: 1.000000")
        w("")
        w("+Disallow Support: 1")
        w("")
        w("+Hull Repair Ceiling: 0.000000")
        w("")
        w("+Subsystem Repair Ceiling: 100.000000")
        w("")
        w("+Viewer pos: 0.000000, 0.000000, -3000.000000")
        w("+Viewer orient:")
        w("\t1.000000, 0.000000, 0.000000,")
        w("\t0.000000, 1.000000, 0.000000,")
        w("\t0.000000, 0.000000, 1.000000")
        w("+SquadReassignName: 72nd Thunderlords")
        w("+SquadReassignLogo: thunderlords.pcx")
        w("")
        w('$Starting wing names: ( "Red" )')
        w('$Squadron wing names: ( "Red" "Orange" "Violet" "Blue" "Green" )')
        w('$Team-versus-team wing names: ( "Red" "Orange" )')
        w("")
        w("$Load Screen 640:\tY_No_1024x768.tga")
        w("$Load Screen 1024:\t%s" % self.load_screen)
        w("")
        w("$Skybox Model: SkyBox_Starfield_01.pof")
        w("")
        w("$AI Profile: Diaspora_default")
        w("")
        w("#Sexp_variables")
        w("")
        w("$Variables:")
        w("(")
        w(")")
        w("")
        w("#Cutscenes")
        w("")
        w("#end")
        w("")
        w("#Command Briefing")
        w("")
        w("#Briefing")
        w("$start_briefing")
        w("$num_stages: 0")
        w("$end_briefing")
        w("")
        w("#Debriefing_info")
        w("")
        w("$Num stages: %d" % len(self.debriefs))
        w("")
        for formula, text, rec in self.debriefs:
            w("$Formula: %s" % formula)
            w("$Multi text")
            w("    %s" % xstr(text))
            w("$end_multi_text")
            w("$Voice: none")
            w("$Recommendation text:")
            w("    %s" % xstr(rec))
            w("$end_multi_text")
            w("")
        w("#Callsigns:")
        for c in self.callsigns:
            w("$Callsign: %s" % c)
        w("")
        w("#end")
        w("")
        w("")
        w("#Players\t\t;! 1 total")
        w("")
        w("$Starting Shipname: Red 1")
        w("$Ship Choices: (")
        w(")")
        w("")
        w("+Weaponry Pool: (")
        for weapon, count in self.weapon_pool:
            w('\t"%s"\t%d' % (weapon, count))
        w(")")
        w("")
        w("#Objects\t\t;! %d total" % len(self.objects))
        w("")
        for i, o in enumerate(self.objects):
            first = o[0] + "\t\t;! Object #%d" % i
            w(first)
            for l in o[1:]:
                w(l)
            w("")
        w("#Wings\t\t;! %d total" % len(self.wings))
        w("")
        for wing in self.wings:
            w("$Name: %s" % wing["name"])
            w("$Waves: 1")
            w("$Wave Threshold: 0")
            w("$Special Ship: 0\t\t;! %s 1" % wing["name"])
            w("")
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
            w("")
        w("#Events\t\t;! %d total" % len(self.events))
        w("")
        for name, formula in self.events:
            w("$Formula: %s" % formula)
            w("+Name: %s" % name)
            w("+Repeat Count: 1")
            w("+Interval: 1")
            w("")
        w("#Goals\t\t;! %d total" % len(self.goals))
        w("")
        for typ, name, text, formula, score in self.goals:
            w("$Type: %s" % typ)
            w("+Name: %s" % name)
            w("$MessageNew:  %s" % xstr(text))
            w("$end_multi_text")
            w("$Formula: %s" % formula)
            w("+Score: %d" % score)
            w("")
        w("#Waypoints\t\t;! %d lists total" % len(self.waypoints))
        w("")
        for name, points in self.waypoints:
            w("$Name: %s" % name)
            w("$List: (\t\t;! %d points in list" % len(points))
            for p in points:
                w("\t( %.6f, %.6f, %.6f )" % p)
            w(")")
            w("")
        w("#Messages\t\t;! %d total" % len(self.messages))
        w("")
        w("$Command Sender: Theseus")
        w("")
        for name, text in self.messages:
            w("$Name: %s" % name)
            w("$Team: -1")
            w("$MessageNew:  %s" % xstr(text))
            w("$end_multi_text")
            if name in self.waves:
                w("+Wave Name: %s" % self.waves[name])
            w("")
        w("#Reinforcements\t\t;! 0 total")
        w("")
        w("")
        bg = self.background
        w("#Background bitmaps\t\t;! %d total" % len(bg["bitmaps"]))
        w("")
        w("$Num stars: 0")
        w("$Ambient light level: %d" % bg["ambient"])
        w("")
        w("$Bitmap List:")
        w("$Sun: %s" % bg["sun"])
        w("+Angles: %s" % bg["sun_angles"])
        w("+Scale: %f" % bg["sun_scale"])
        for name, angles, sx, sy in bg["bitmaps"]:
            w("$Starbitmap: %s" % name)
            w("+Angles: %s" % angles)
            w("+ScaleX: %f" % sx)
            w("+ScaleY: %f" % sy)
            w("+DivX: 1")
            w("+DivY: 1")
        w("")
        w("#Asteroid Fields")
        w("")
        w("#Music")
        w("")
        w("$Event Music: %s" % self.music)
        w("$Briefing Music: Brief11")
        w("")
        w("#End")
        with open(path, "wb") as f:
            f.write((NL.join(out) + NL).encode("latin-1"))
        return "%s: %d objects, %d wings, %d events, %d messages" % (path, len(self.objects), len(self.wings),
                                                                      len(self.events), len(self.messages))
