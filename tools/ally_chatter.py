#!/usr/bin/env python3
"""In-flight ally chatter: celebrations, death screams, tail warnings, friendly fire, low health, swarms. Written as a Lua
script table (overlay tables/ally_chatter-sct.tbm) that plays voice lines the game's own persona system does not have, plus
the voice jobs for them (F5-TTS from the original persona recordings, see make_voices.py).

usage: ally_chatter.py jobs OUT.json            write the synthesis jobs for tools/make_voices.py post
       ally_chatter.py table DATA_DIR            write scripts/ally_chatter.lua and tables/ally_chatter-sct.tbm
"""
import json, os, sys

POOLS = {
    "kill": ["Splash one!", "Got him!", "Tango down!", "That's a kill!", "Toaster down, nice and clean!", "He's scrap, next!",
             "One less Cylon in the sky.", "Burn, you toaster!"],
    "praise": ["Nice shooting, lead!", "Good kill, lead!", "That one was beautiful, lead.", "Lead's on fire today!", "Great shot, keep it up."],
    "death": ["I'm hit! I'm hit! Ejecting!", "Gods, no, no, no!", "Mayday, mayday, I'm going down!", "Tell my family I'm sorry!", "Aaaargh! Hull breach, I'm gone!"],
    "tail": ["Lead, you've got one on your six!", "Break, break! Bogey on your tail!", "Check your six, lead, he's right behind you!",
             "You've got a Raider on your tail, shake him!", "Lead, tail gunner, he's closing, break now!"],
    "help": ["I've got one on my tail, I need help!", "Somebody get this toaster off me!", "Can't shake him, a little help here!", "Bogey on my six, I need a hand!"],
    "ff_in": ["Hey, watch your fire, lead!", "You're shooting at me, lead! Friendly!", "Easy on the trigger, I'm on your side!", "Cease fire, cease fire, friendly!"],
    "ff_out": ["Sorry, lead, my bad!", "Oops, I didn't see you there. Sorry!", "Friendly, friendly, sorry lead!", "That was me, lead. Won't happen again."],
    "low_self": ["I'm hurting bad, I need to break off!", "Hull's at the red line, I can't take much more!", "I'm coming apart, requesting cover!", "Hit hard, running on fumes!"],
    "low_player": ["Lead, you're venting air, break off!", "Lead, your hull is almost gone, get out of there!", "You're trailing smoke, lead, disengage!", "Lead, you can't take another hit, pull back!"],
    "swarm": ["Look at all those bogeys!", "Gods, there are a lot of them!", "They keep coming, I count over a dozen!", "That's a lot of toasters, let's thin them out.", "The sky is full of Raiders, stay sharp!"],
}
PER_VOICE = {"kill": 3, "praise": 2, "death": 2, "tail": 3, "help": 2, "ff_in": 2, "ff_out": 2, "low_self": 2, "low_player": 2, "swarm": 2}
VOICES = ["shadow", "flask", "turbo", "crispy", "hammer", "harridan", "rapt", "gen1", "gen3", "gen4", "gen5", "gen6"]
SPEED = 1.0


def clips():
    """voice -> event -> [(file name, text)]: each voice gets its own slice of every pool, so two wingmen rarely say the same thing."""
    out = {}
    for vi, v in enumerate(VOICES):
        out[v] = {}
        for ev, pool in POOLS.items():
            n = PER_VOICE[ev]
            picks = [pool[(vi * 2 + k) % len(pool)] for k in range(n)]
            out[v][ev] = [("AC-%s-%s-%d.ogg" % (v, ev, k + 1), t) for k, t in enumerate(dict.fromkeys(picks))]
    return out


def write_jobs(path):
    meta = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice_refs", "meta.json")))
    lines = []
    for v, evs in clips().items():
        for ev, items in evs.items():
            for fname, text in items:
                lines.append({"id": fname[:-4], "mission": "AC.fs2", "message": fname[:-4], "voice": v, "speed": 0.97, "text": text})
    json.dump({"refs": {v: {"wav": meta[v]["wav"], "text": meta[v]["text"]} for v in VOICES}, "lines": lines}, open(path, "w"), indent=1)
    print(len(lines), "clips")


LUA = r'''
local LINES = %(lines)s
local VOICES = %(voices)s
local NAMED = { ["Red 2"] = "shadow", ["Red 3"] = "flask", ["Blue 1"] = "turbo", ["Blue 2"] = "crispy",
                ["Nightjar 2"] = "shadow", ["Nightjar 3"] = "flask" }
local DEBUG = %(debug)s
local function dbg(msg)
  if not DEBUG then return end
  pcall(function()
    local f = cf.openFile("ac_debug.txt", "a", "data/players")
    if f:isValid() then f:write(msg .. "\\n") f:close() end
  end)
end
dbg("loaded")
local cool = {}
local sunk = {}          -- ships already reported low on hull / dead

local function now() return mn.getMissionTime() end

local function ready(key, gap)
  local t = now()
  if cool[key] and t - cool[key] < gap then return false end
  cool[key] = t
  return true
end

local function voice_of(name)
  if NAMED[name] then return NAMED[name] end
  local h = 0
  for i = 1, #name do h = (h * 31 + string.byte(name, i)) %% 9973 end
  return VOICES[h %% #VOICES + 1]
end

local function say(name, event)
  local v = voice_of(name)
  local pool = LINES[v] and LINES[v][event]
  if not pool or #pool == 0 then return end
  local pick = pool[math.random(#pool)]
  local ok = pcall(function()
    local st = ad.openAudioStream(pick[1], AUDIOSTREAM_VOICE)
    if st:isValid() then st:play(1.0) end
  end)
  pcall(function() mn.sendPlainMessage(name .. ": " .. pick[2]) end)
  dbg("say " .. event .. " " .. name .. ": " .. pick[2])
end

local function player_ship()
  local p = mn.Ships["Red 1"]
  if p ~= nil and p:isValid() then return p end
  p = mn.Ships["Nightjar 1"]
  if p ~= nil and p:isValid() then return p end
  return nil
end

local function is_friendly_fighter(s)
  return s:isValid() and s.Team.Name == "Friendly" and string.find(s.Class.Name, "Viper") ~= nil
end

local function is_hostile_fighter(s)
  return s:isValid() and s.Team.Name == "Hostile" and string.find(s.Class.Name, "Raider") ~= nil
end

-- a friendly fighter other than the player, preferably close to the player
local function pick_ally(player, skip)
  local best, bd = nil, 1e9
  for i = 1, #mn.Ships do
    local s = mn.Ships[i]
    if s:isValid() and s ~= player and s.Name ~= skip and is_friendly_fighter(s) and s.HitpointsLeft > 0 then
      local d = player.Position:getDistance(s.Position)
      if d < bd then best, bd = s, d end
    end
  end
  return best
end

local function ship_at(pos, team)
  for i = 1, #mn.Ships do
    local s = mn.Ships[i]
    if s:isValid() and (team == nil or s.Team.Name == team) and s.Position:getDistance(pos) < 30 then return s end
  end
  return nil
end

-- celebration and death scream
engine_death = function(ship, killer)
  dbg("death " .. tostring(ship:isValid() and ship.Name))
  local player = player_ship()
  if player == nil or not ship:isValid() then return end
  if is_friendly_fighter(ship) and ship ~= player and not sunk[ship.Name .. "d"] then
    sunk[ship.Name .. "d"] = true
    say(ship.Name, "death")
    return
  end
  if is_hostile_fighter(ship) and killer ~= nil and killer:isValid() then
    local kb = killer:getBreedName()
    local ks = nil
    if kb == "Ship" then
      ks = ship_at(killer.Position, nil)
    elseif kb == "Weapon" then
      local p = killer.Parent
      if p ~= nil and p:isValid() and p:getBreedName() == "Ship" then ks = ship_at(p.Position, nil) end
    end
    if ks ~= nil and ks == player then
      if ready("praise", 9) then local a = pick_ally(player); if a then say(a.Name, "praise") end end
    elseif ks ~= nil and is_friendly_fighter(ks) then
      if ready("kill", 6) and math.random() < 0.6 then say(ks.Name, "kill") end
    end
  end
end

-- friendly fire: the player shot an ally (the ally complains) or an ally shot the player (the ally apologises)
engine_hit = function(target, weapon)
  local player = player_ship()
  if player == nil or target == nil or weapon == nil then return end
  if not (target:isValid() and weapon:isValid()) then return end
  if target:getBreedName() ~= "Ship" then return end
  local parent = weapon.Parent
  if parent == nil or not parent:isValid() or parent:getBreedName() ~= "Ship" then return end
  local victim, shooter = ship_at(target.Position, nil), ship_at(parent.Position, nil)
  if victim == nil or shooter == nil or victim == shooter then return end
  if shooter == player and is_friendly_fighter(victim) then
    if ready("ff_in" .. victim.Name, 12) then say(victim.Name, "ff_in") end
  elseif victim == player and is_friendly_fighter(shooter) then
    if ready("ff_out" .. shooter.Name, 12) then say(shooter.Name, "ff_out") end
  end
end

-- once a second: tails, low hull, swarms
local last_tick = 0
engine_tick = function()
  local t = now()
  if t - last_tick < 1.0 then return end
  last_tick = t
  local player = player_ship()
  if math.floor(t) %% 60 == 0 then dbg("tick " .. tostring(player ~= nil) .. " t=" .. math.floor(t)) end
  if player == nil or not player:isValid() then return end
  local fwd = player.Orientation:getFvec()
  local close, hostile, behind = 0, 0, false
  for i = 1, #mn.Ships do
    local s = mn.Ships[i]
    if s:isValid() and is_hostile_fighter(s) then
      local d = player.Position:getDistance(s.Position)
      if d < 3500 then close = close + 1 end
      if d < 900 then
        local v = s.Position - player.Position
        v:normalize()
        if v:getDotProduct(fwd) < -0.55 then behind = true end
      end
    elseif s:isValid() and is_friendly_fighter(s) and s ~= player then
      local pct = s.HitpointsLeft / math.max(1, s.HitpointsMax)
      if pct < 0.25 and not sunk[s.Name .. "l"] and s.HitpointsLeft > 0 then
        sunk[s.Name .. "l"] = true
        if ready("low_self", 8) then say(s.Name, "low_self") end
      end
      -- an ally with a Raider on its six calls for help
      if ready("help" .. s.Name, 30) then
        for j = 1, #mn.Ships do
          local h = mn.Ships[j]
          if h:isValid() and is_hostile_fighter(h) and s.Position:getDistance(h.Position) < 500 then
            local hv = h.Position - s.Position
            hv:normalize()
            if hv:getDotProduct(s.Orientation:getFvec()) < -0.6 then say(s.Name, "help") break end
          end
        end
      end
    end
  end
  if behind and ready("tail", 14) then
    local a = pick_ally(player)
    if a then say(a.Name, "tail") end
  end
  local pct = player.HitpointsLeft / math.max(1, player.HitpointsMax)
  if pct < 0.25 and ready("low_player", 40) then
    local a = pick_ally(player)
    if a then say(a.Name, "low_player") end
  end
  if close >= 8 and ready("swarm", 90) then
    local a = pick_ally(player)
    if a then say(a.Name, "swarm") end
  end
end
'''


def write_table(data_dir):
    """data_dir is the overlay data folder: tables/ally_chatter-sct.tbm and scripts/ally_chatter.lua."""
    lines = {v: {ev: [[f, t] for f, t in items] for ev, items in evs.items()} for v, evs in clips().items()}

    def lua_table(x):
        if isinstance(x, dict):
            return "{ " + ", ".join("[%s] = %s" % (json.dumps(k), lua_table(v)) for k, v in x.items()) + " }"
        if isinstance(x, list):
            return "{ " + ", ".join(lua_table(v) for v in x) + " }"
        return json.dumps(x)
    code = LUA % {"lines": lua_table(lines), "voices": lua_table(VOICES), "debug": "true" if os.environ.get("AC_DEBUG") else "false"}
    os.makedirs(os.path.join(data_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "tables"), exist_ok=True)
    open(os.path.join(data_dir, "scripts", "ally_chatter.lua"), "w").write(code)
    tbm = "#Conditional Hooks\n\n$Application: FS2_Open\n\n$On Mission Start: [[ally_chatter.lua]]\n\n"
    tbm += "$On Simulation: [\n  if engine_tick then pcall(engine_tick) end\n]\n\n"
    tbm += "$On Ship Death Started: [\n  if engine_death then pcall(engine_death, hv.Ship, hv.Killer) end\n]\n\n"
    tbm += "$On Weapon Collision: [\n  if engine_hit then pcall(engine_hit, hv.Self, hv.Weapon) end\n]\n\n#End\n"
    open(os.path.join(data_dir, "tables", "ally_chatter-sct.tbm"), "w").write(tbm)
    print("wrote ally_chatter.lua (%d bytes) and ally_chatter-sct.tbm" % len(code))


if __name__ == "__main__":
    if sys.argv[1] == "jobs":
        write_jobs(sys.argv[2])
    elif sys.argv[1] == "table":
        write_table(sys.argv[2])
