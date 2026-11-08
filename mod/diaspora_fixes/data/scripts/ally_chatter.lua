
local LINES = { ["shadow"] = { ["kill"] = { { "AC-shadow-kill-1.ogg", "Splash one!" }, { "AC-shadow-kill-2.ogg", "Got him!" }, { "AC-shadow-kill-3.ogg", "Tango down!" } }, ["praise"] = { { "AC-shadow-praise-1.ogg", "Nice shooting, lead!" }, { "AC-shadow-praise-2.ogg", "Good kill, lead!" } }, ["death"] = { { "AC-shadow-death-1.ogg", "I'm hit! I'm hit! Ejecting!" }, { "AC-shadow-death-2.ogg", "Gods, no, no, no!" } }, ["tail"] = { { "AC-shadow-tail-1.ogg", "Lead, you've got one on your six!" }, { "AC-shadow-tail-2.ogg", "Break, break! Bogey on your tail!" }, { "AC-shadow-tail-3.ogg", "Check your six, lead, he's right behind you!" } }, ["help"] = { { "AC-shadow-help-1.ogg", "I've got one on my tail, I need help!" }, { "AC-shadow-help-2.ogg", "Somebody get this toaster off me!" } }, ["ff_in"] = { { "AC-shadow-ff_in-1.ogg", "Hey, watch your fire, lead!" }, { "AC-shadow-ff_in-2.ogg", "You're shooting at me, lead! Friendly!" } }, ["ff_out"] = { { "AC-shadow-ff_out-1.ogg", "Sorry, lead, my bad!" }, { "AC-shadow-ff_out-2.ogg", "Oops, I didn't see you there. Sorry!" } }, ["low_self"] = { { "AC-shadow-low_self-1.ogg", "I'm hurting bad, I need to break off!" }, { "AC-shadow-low_self-2.ogg", "Hull's at the red line, I can't take much more!" } }, ["low_player"] = { { "AC-shadow-low_player-1.ogg", "Lead, you're venting air, break off!" }, { "AC-shadow-low_player-2.ogg", "Lead, your hull is almost gone, get out of there!" } }, ["swarm"] = { { "AC-shadow-swarm-1.ogg", "Look at all those bogeys!" }, { "AC-shadow-swarm-2.ogg", "Gods, there are a lot of them!" } } }, ["flask"] = { ["kill"] = { { "AC-flask-kill-1.ogg", "Tango down!" }, { "AC-flask-kill-2.ogg", "That's a kill!" }, { "AC-flask-kill-3.ogg", "Toaster down, nice and clean!" } }, ["praise"] = { { "AC-flask-praise-1.ogg", "That one was beautiful, lead." }, { "AC-flask-praise-2.ogg", "Lead's on fire today!" } }, ["death"] = { { "AC-flask-death-1.ogg", "Mayday, mayday, I'm going down!" }, { "AC-flask-death-2.ogg", "Tell my family I'm sorry!" } }, ["tail"] = { { "AC-flask-tail-1.ogg", "Check your six, lead, he's right behind you!" }, { "AC-flask-tail-2.ogg", "You've got a Raider on your tail, shake him!" }, { "AC-flask-tail-3.ogg", "Lead, tail gunner, he's closing, break now!" } }, ["help"] = { { "AC-flask-help-1.ogg", "Can't shake him, a little help here!" }, { "AC-flask-help-2.ogg", "Bogey on my six, I need a hand!" } }, ["ff_in"] = { { "AC-flask-ff_in-1.ogg", "Easy on the trigger, I'm on your side!" }, { "AC-flask-ff_in-2.ogg", "Cease fire, cease fire, friendly!" } }, ["ff_out"] = { { "AC-flask-ff_out-1.ogg", "Friendly, friendly, sorry lead!" }, { "AC-flask-ff_out-2.ogg", "That was me, lead. Won't happen again." } }, ["low_self"] = { { "AC-flask-low_self-1.ogg", "I'm coming apart, requesting cover!" }, { "AC-flask-low_self-2.ogg", "Hit hard, running on fumes!" } }, ["low_player"] = { { "AC-flask-low_player-1.ogg", "You're trailing smoke, lead, disengage!" }, { "AC-flask-low_player-2.ogg", "Lead, you can't take another hit, pull back!" } }, ["swarm"] = { { "AC-flask-swarm-1.ogg", "They keep coming, I count over a dozen!" }, { "AC-flask-swarm-2.ogg", "That's a lot of toasters, let's thin them out." } } }, ["turbo"] = { ["kill"] = { { "AC-turbo-kill-1.ogg", "Toaster down, nice and clean!" }, { "AC-turbo-kill-2.ogg", "He's scrap, next!" }, { "AC-turbo-kill-3.ogg", "One less Cylon in the sky." } }, ["praise"] = { { "AC-turbo-praise-1.ogg", "Great shot, keep it up." }, { "AC-turbo-praise-2.ogg", "Nice shooting, lead!" } }, ["death"] = { { "AC-turbo-death-1.ogg", "Aaaargh! Hull breach, I'm gone!" }, { "AC-turbo-death-2.ogg", "I'm hit! I'm hit! Ejecting!" } }, ["tail"] = { { "AC-turbo-tail-1.ogg", "Lead, tail gunner, he's closing, break now!" }, { "AC-turbo-tail-2.ogg", "Lead, you've got one on your six!" }, { "AC-turbo-tail-3.ogg", "Break, break! Bogey on your tail!" } }, ["help"] = { { "AC-turbo-help-1.ogg", "I've got one on my tail, I need help!" }, { "AC-turbo-help-2.ogg", "Somebody get this toaster off me!" } }, ["ff_in"] = { { "AC-turbo-ff_in-1.ogg", "Hey, watch your fire, lead!" }, { "AC-turbo-ff_in-2.ogg", "You're shooting at me, lead! Friendly!" } }, ["ff_out"] = { { "AC-turbo-ff_out-1.ogg", "Sorry, lead, my bad!" }, { "AC-turbo-ff_out-2.ogg", "Oops, I didn't see you there. Sorry!" } }, ["low_self"] = { { "AC-turbo-low_self-1.ogg", "I'm hurting bad, I need to break off!" }, { "AC-turbo-low_self-2.ogg", "Hull's at the red line, I can't take much more!" } }, ["low_player"] = { { "AC-turbo-low_player-1.ogg", "Lead, you're venting air, break off!" }, { "AC-turbo-low_player-2.ogg", "Lead, your hull is almost gone, get out of there!" } }, ["swarm"] = { { "AC-turbo-swarm-1.ogg", "The sky is full of Raiders, stay sharp!" }, { "AC-turbo-swarm-2.ogg", "Look at all those bogeys!" } } }, ["crispy"] = { ["kill"] = { { "AC-crispy-kill-1.ogg", "One less Cylon in the sky." }, { "AC-crispy-kill-2.ogg", "Burn, you toaster!" }, { "AC-crispy-kill-3.ogg", "Splash one!" } }, ["praise"] = { { "AC-crispy-praise-1.ogg", "Good kill, lead!" }, { "AC-crispy-praise-2.ogg", "That one was beautiful, lead." } }, ["death"] = { { "AC-crispy-death-1.ogg", "Gods, no, no, no!" }, { "AC-crispy-death-2.ogg", "Mayday, mayday, I'm going down!" } }, ["tail"] = { { "AC-crispy-tail-1.ogg", "Break, break! Bogey on your tail!" }, { "AC-crispy-tail-2.ogg", "Check your six, lead, he's right behind you!" }, { "AC-crispy-tail-3.ogg", "You've got a Raider on your tail, shake him!" } }, ["help"] = { { "AC-crispy-help-1.ogg", "Can't shake him, a little help here!" }, { "AC-crispy-help-2.ogg", "Bogey on my six, I need a hand!" } }, ["ff_in"] = { { "AC-crispy-ff_in-1.ogg", "Easy on the trigger, I'm on your side!" }, { "AC-crispy-ff_in-2.ogg", "Cease fire, cease fire, friendly!" } }, ["ff_out"] = { { "AC-crispy-ff_out-1.ogg", "Friendly, friendly, sorry lead!" }, { "AC-crispy-ff_out-2.ogg", "That was me, lead. Won't happen again." } }, ["low_self"] = { { "AC-crispy-low_self-1.ogg", "I'm coming apart, requesting cover!" }, { "AC-crispy-low_self-2.ogg", "Hit hard, running on fumes!" } }, ["low_player"] = { { "AC-crispy-low_player-1.ogg", "You're trailing smoke, lead, disengage!" }, { "AC-crispy-low_player-2.ogg", "Lead, you can't take another hit, pull back!" } }, ["swarm"] = { { "AC-crispy-swarm-1.ogg", "Gods, there are a lot of them!" }, { "AC-crispy-swarm-2.ogg", "They keep coming, I count over a dozen!" } } }, ["hammer"] = { ["kill"] = { { "AC-hammer-kill-1.ogg", "Splash one!" }, { "AC-hammer-kill-2.ogg", "Got him!" }, { "AC-hammer-kill-3.ogg", "Tango down!" } }, ["praise"] = { { "AC-hammer-praise-1.ogg", "Lead's on fire today!" }, { "AC-hammer-praise-2.ogg", "Great shot, keep it up." } }, ["death"] = { { "AC-hammer-death-1.ogg", "Tell my family I'm sorry!" }, { "AC-hammer-death-2.ogg", "Aaaargh! Hull breach, I'm gone!" } }, ["tail"] = { { "AC-hammer-tail-1.ogg", "You've got a Raider on your tail, shake him!" }, { "AC-hammer-tail-2.ogg", "Lead, tail gunner, he's closing, break now!" }, { "AC-hammer-tail-3.ogg", "Lead, you've got one on your six!" } }, ["help"] = { { "AC-hammer-help-1.ogg", "I've got one on my tail, I need help!" }, { "AC-hammer-help-2.ogg", "Somebody get this toaster off me!" } }, ["ff_in"] = { { "AC-hammer-ff_in-1.ogg", "Hey, watch your fire, lead!" }, { "AC-hammer-ff_in-2.ogg", "You're shooting at me, lead! Friendly!" } }, ["ff_out"] = { { "AC-hammer-ff_out-1.ogg", "Sorry, lead, my bad!" }, { "AC-hammer-ff_out-2.ogg", "Oops, I didn't see you there. Sorry!" } }, ["low_self"] = { { "AC-hammer-low_self-1.ogg", "I'm hurting bad, I need to break off!" }, { "AC-hammer-low_self-2.ogg", "Hull's at the red line, I can't take much more!" } }, ["low_player"] = { { "AC-hammer-low_player-1.ogg", "Lead, you're venting air, break off!" }, { "AC-hammer-low_player-2.ogg", "Lead, your hull is almost gone, get out of there!" } }, ["swarm"] = { { "AC-hammer-swarm-1.ogg", "That's a lot of toasters, let's thin them out." }, { "AC-hammer-swarm-2.ogg", "The sky is full of Raiders, stay sharp!" } } }, ["harridan"] = { ["kill"] = { { "AC-harridan-kill-1.ogg", "Tango down!" }, { "AC-harridan-kill-2.ogg", "That's a kill!" }, { "AC-harridan-kill-3.ogg", "Toaster down, nice and clean!" } }, ["praise"] = { { "AC-harridan-praise-1.ogg", "Nice shooting, lead!" }, { "AC-harridan-praise-2.ogg", "Good kill, lead!" } }, ["death"] = { { "AC-harridan-death-1.ogg", "I'm hit! I'm hit! Ejecting!" }, { "AC-harridan-death-2.ogg", "Gods, no, no, no!" } }, ["tail"] = { { "AC-harridan-tail-1.ogg", "Lead, you've got one on your six!" }, { "AC-harridan-tail-2.ogg", "Break, break! Bogey on your tail!" }, { "AC-harridan-tail-3.ogg", "Check your six, lead, he's right behind you!" } }, ["help"] = { { "AC-harridan-help-1.ogg", "Can't shake him, a little help here!" }, { "AC-harridan-help-2.ogg", "Bogey on my six, I need a hand!" } }, ["ff_in"] = { { "AC-harridan-ff_in-1.ogg", "Easy on the trigger, I'm on your side!" }, { "AC-harridan-ff_in-2.ogg", "Cease fire, cease fire, friendly!" } }, ["ff_out"] = { { "AC-harridan-ff_out-1.ogg", "Friendly, friendly, sorry lead!" }, { "AC-harridan-ff_out-2.ogg", "That was me, lead. Won't happen again." } }, ["low_self"] = { { "AC-harridan-low_self-1.ogg", "I'm coming apart, requesting cover!" }, { "AC-harridan-low_self-2.ogg", "Hit hard, running on fumes!" } }, ["low_player"] = { { "AC-harridan-low_player-1.ogg", "You're trailing smoke, lead, disengage!" }, { "AC-harridan-low_player-2.ogg", "Lead, you can't take another hit, pull back!" } }, ["swarm"] = { { "AC-harridan-swarm-1.ogg", "Look at all those bogeys!" }, { "AC-harridan-swarm-2.ogg", "Gods, there are a lot of them!" } } }, ["rapt"] = { ["kill"] = { { "AC-rapt-kill-1.ogg", "Toaster down, nice and clean!" }, { "AC-rapt-kill-2.ogg", "He's scrap, next!" }, { "AC-rapt-kill-3.ogg", "One less Cylon in the sky." } }, ["praise"] = { { "AC-rapt-praise-1.ogg", "That one was beautiful, lead." }, { "AC-rapt-praise-2.ogg", "Lead's on fire today!" } }, ["death"] = { { "AC-rapt-death-1.ogg", "Mayday, mayday, I'm going down!" }, { "AC-rapt-death-2.ogg", "Tell my family I'm sorry!" } }, ["tail"] = { { "AC-rapt-tail-1.ogg", "Check your six, lead, he's right behind you!" }, { "AC-rapt-tail-2.ogg", "You've got a Raider on your tail, shake him!" }, { "AC-rapt-tail-3.ogg", "Lead, tail gunner, he's closing, break now!" } }, ["help"] = { { "AC-rapt-help-1.ogg", "I've got one on my tail, I need help!" }, { "AC-rapt-help-2.ogg", "Somebody get this toaster off me!" } }, ["ff_in"] = { { "AC-rapt-ff_in-1.ogg", "Hey, watch your fire, lead!" }, { "AC-rapt-ff_in-2.ogg", "You're shooting at me, lead! Friendly!" } }, ["ff_out"] = { { "AC-rapt-ff_out-1.ogg", "Sorry, lead, my bad!" }, { "AC-rapt-ff_out-2.ogg", "Oops, I didn't see you there. Sorry!" } }, ["low_self"] = { { "AC-rapt-low_self-1.ogg", "I'm hurting bad, I need to break off!" }, { "AC-rapt-low_self-2.ogg", "Hull's at the red line, I can't take much more!" } }, ["low_player"] = { { "AC-rapt-low_player-1.ogg", "Lead, you're venting air, break off!" }, { "AC-rapt-low_player-2.ogg", "Lead, your hull is almost gone, get out of there!" } }, ["swarm"] = { { "AC-rapt-swarm-1.ogg", "They keep coming, I count over a dozen!" }, { "AC-rapt-swarm-2.ogg", "That's a lot of toasters, let's thin them out." } } }, ["gen1"] = { ["kill"] = { { "AC-gen1-kill-1.ogg", "One less Cylon in the sky." }, { "AC-gen1-kill-2.ogg", "Burn, you toaster!" }, { "AC-gen1-kill-3.ogg", "Splash one!" } }, ["praise"] = { { "AC-gen1-praise-1.ogg", "Great shot, keep it up." }, { "AC-gen1-praise-2.ogg", "Nice shooting, lead!" } }, ["death"] = { { "AC-gen1-death-1.ogg", "Aaaargh! Hull breach, I'm gone!" }, { "AC-gen1-death-2.ogg", "I'm hit! I'm hit! Ejecting!" } }, ["tail"] = { { "AC-gen1-tail-1.ogg", "Lead, tail gunner, he's closing, break now!" }, { "AC-gen1-tail-2.ogg", "Lead, you've got one on your six!" }, { "AC-gen1-tail-3.ogg", "Break, break! Bogey on your tail!" } }, ["help"] = { { "AC-gen1-help-1.ogg", "Can't shake him, a little help here!" }, { "AC-gen1-help-2.ogg", "Bogey on my six, I need a hand!" } }, ["ff_in"] = { { "AC-gen1-ff_in-1.ogg", "Easy on the trigger, I'm on your side!" }, { "AC-gen1-ff_in-2.ogg", "Cease fire, cease fire, friendly!" } }, ["ff_out"] = { { "AC-gen1-ff_out-1.ogg", "Friendly, friendly, sorry lead!" }, { "AC-gen1-ff_out-2.ogg", "That was me, lead. Won't happen again." } }, ["low_self"] = { { "AC-gen1-low_self-1.ogg", "I'm coming apart, requesting cover!" }, { "AC-gen1-low_self-2.ogg", "Hit hard, running on fumes!" } }, ["low_player"] = { { "AC-gen1-low_player-1.ogg", "You're trailing smoke, lead, disengage!" }, { "AC-gen1-low_player-2.ogg", "Lead, you can't take another hit, pull back!" } }, ["swarm"] = { { "AC-gen1-swarm-1.ogg", "The sky is full of Raiders, stay sharp!" }, { "AC-gen1-swarm-2.ogg", "Look at all those bogeys!" } } }, ["gen3"] = { ["kill"] = { { "AC-gen3-kill-1.ogg", "Splash one!" }, { "AC-gen3-kill-2.ogg", "Got him!" }, { "AC-gen3-kill-3.ogg", "Tango down!" } }, ["praise"] = { { "AC-gen3-praise-1.ogg", "Good kill, lead!" }, { "AC-gen3-praise-2.ogg", "That one was beautiful, lead." } }, ["death"] = { { "AC-gen3-death-1.ogg", "Gods, no, no, no!" }, { "AC-gen3-death-2.ogg", "Mayday, mayday, I'm going down!" } }, ["tail"] = { { "AC-gen3-tail-1.ogg", "Break, break! Bogey on your tail!" }, { "AC-gen3-tail-2.ogg", "Check your six, lead, he's right behind you!" }, { "AC-gen3-tail-3.ogg", "You've got a Raider on your tail, shake him!" } }, ["help"] = { { "AC-gen3-help-1.ogg", "I've got one on my tail, I need help!" }, { "AC-gen3-help-2.ogg", "Somebody get this toaster off me!" } }, ["ff_in"] = { { "AC-gen3-ff_in-1.ogg", "Hey, watch your fire, lead!" }, { "AC-gen3-ff_in-2.ogg", "You're shooting at me, lead! Friendly!" } }, ["ff_out"] = { { "AC-gen3-ff_out-1.ogg", "Sorry, lead, my bad!" }, { "AC-gen3-ff_out-2.ogg", "Oops, I didn't see you there. Sorry!" } }, ["low_self"] = { { "AC-gen3-low_self-1.ogg", "I'm hurting bad, I need to break off!" }, { "AC-gen3-low_self-2.ogg", "Hull's at the red line, I can't take much more!" } }, ["low_player"] = { { "AC-gen3-low_player-1.ogg", "Lead, you're venting air, break off!" }, { "AC-gen3-low_player-2.ogg", "Lead, your hull is almost gone, get out of there!" } }, ["swarm"] = { { "AC-gen3-swarm-1.ogg", "Gods, there are a lot of them!" }, { "AC-gen3-swarm-2.ogg", "They keep coming, I count over a dozen!" } } }, ["gen4"] = { ["kill"] = { { "AC-gen4-kill-1.ogg", "Tango down!" }, { "AC-gen4-kill-2.ogg", "That's a kill!" }, { "AC-gen4-kill-3.ogg", "Toaster down, nice and clean!" } }, ["praise"] = { { "AC-gen4-praise-1.ogg", "Lead's on fire today!" }, { "AC-gen4-praise-2.ogg", "Great shot, keep it up." } }, ["death"] = { { "AC-gen4-death-1.ogg", "Tell my family I'm sorry!" }, { "AC-gen4-death-2.ogg", "Aaaargh! Hull breach, I'm gone!" } }, ["tail"] = { { "AC-gen4-tail-1.ogg", "You've got a Raider on your tail, shake him!" }, { "AC-gen4-tail-2.ogg", "Lead, tail gunner, he's closing, break now!" }, { "AC-gen4-tail-3.ogg", "Lead, you've got one on your six!" } }, ["help"] = { { "AC-gen4-help-1.ogg", "Can't shake him, a little help here!" }, { "AC-gen4-help-2.ogg", "Bogey on my six, I need a hand!" } }, ["ff_in"] = { { "AC-gen4-ff_in-1.ogg", "Easy on the trigger, I'm on your side!" }, { "AC-gen4-ff_in-2.ogg", "Cease fire, cease fire, friendly!" } }, ["ff_out"] = { { "AC-gen4-ff_out-1.ogg", "Friendly, friendly, sorry lead!" }, { "AC-gen4-ff_out-2.ogg", "That was me, lead. Won't happen again." } }, ["low_self"] = { { "AC-gen4-low_self-1.ogg", "I'm coming apart, requesting cover!" }, { "AC-gen4-low_self-2.ogg", "Hit hard, running on fumes!" } }, ["low_player"] = { { "AC-gen4-low_player-1.ogg", "You're trailing smoke, lead, disengage!" }, { "AC-gen4-low_player-2.ogg", "Lead, you can't take another hit, pull back!" } }, ["swarm"] = { { "AC-gen4-swarm-1.ogg", "That's a lot of toasters, let's thin them out." }, { "AC-gen4-swarm-2.ogg", "The sky is full of Raiders, stay sharp!" } } }, ["gen5"] = { ["kill"] = { { "AC-gen5-kill-1.ogg", "Toaster down, nice and clean!" }, { "AC-gen5-kill-2.ogg", "He's scrap, next!" }, { "AC-gen5-kill-3.ogg", "One less Cylon in the sky." } }, ["praise"] = { { "AC-gen5-praise-1.ogg", "Nice shooting, lead!" }, { "AC-gen5-praise-2.ogg", "Good kill, lead!" } }, ["death"] = { { "AC-gen5-death-1.ogg", "I'm hit! I'm hit! Ejecting!" }, { "AC-gen5-death-2.ogg", "Gods, no, no, no!" } }, ["tail"] = { { "AC-gen5-tail-1.ogg", "Lead, you've got one on your six!" }, { "AC-gen5-tail-2.ogg", "Break, break! Bogey on your tail!" }, { "AC-gen5-tail-3.ogg", "Check your six, lead, he's right behind you!" } }, ["help"] = { { "AC-gen5-help-1.ogg", "I've got one on my tail, I need help!" }, { "AC-gen5-help-2.ogg", "Somebody get this toaster off me!" } }, ["ff_in"] = { { "AC-gen5-ff_in-1.ogg", "Hey, watch your fire, lead!" }, { "AC-gen5-ff_in-2.ogg", "You're shooting at me, lead! Friendly!" } }, ["ff_out"] = { { "AC-gen5-ff_out-1.ogg", "Sorry, lead, my bad!" }, { "AC-gen5-ff_out-2.ogg", "Oops, I didn't see you there. Sorry!" } }, ["low_self"] = { { "AC-gen5-low_self-1.ogg", "I'm hurting bad, I need to break off!" }, { "AC-gen5-low_self-2.ogg", "Hull's at the red line, I can't take much more!" } }, ["low_player"] = { { "AC-gen5-low_player-1.ogg", "Lead, you're venting air, break off!" }, { "AC-gen5-low_player-2.ogg", "Lead, your hull is almost gone, get out of there!" } }, ["swarm"] = { { "AC-gen5-swarm-1.ogg", "Look at all those bogeys!" }, { "AC-gen5-swarm-2.ogg", "Gods, there are a lot of them!" } } }, ["gen6"] = { ["kill"] = { { "AC-gen6-kill-1.ogg", "One less Cylon in the sky." }, { "AC-gen6-kill-2.ogg", "Burn, you toaster!" }, { "AC-gen6-kill-3.ogg", "Splash one!" } }, ["praise"] = { { "AC-gen6-praise-1.ogg", "That one was beautiful, lead." }, { "AC-gen6-praise-2.ogg", "Lead's on fire today!" } }, ["death"] = { { "AC-gen6-death-1.ogg", "Mayday, mayday, I'm going down!" }, { "AC-gen6-death-2.ogg", "Tell my family I'm sorry!" } }, ["tail"] = { { "AC-gen6-tail-1.ogg", "Check your six, lead, he's right behind you!" }, { "AC-gen6-tail-2.ogg", "You've got a Raider on your tail, shake him!" }, { "AC-gen6-tail-3.ogg", "Lead, tail gunner, he's closing, break now!" } }, ["help"] = { { "AC-gen6-help-1.ogg", "Can't shake him, a little help here!" }, { "AC-gen6-help-2.ogg", "Bogey on my six, I need a hand!" } }, ["ff_in"] = { { "AC-gen6-ff_in-1.ogg", "Easy on the trigger, I'm on your side!" }, { "AC-gen6-ff_in-2.ogg", "Cease fire, cease fire, friendly!" } }, ["ff_out"] = { { "AC-gen6-ff_out-1.ogg", "Friendly, friendly, sorry lead!" }, { "AC-gen6-ff_out-2.ogg", "That was me, lead. Won't happen again." } }, ["low_self"] = { { "AC-gen6-low_self-1.ogg", "I'm coming apart, requesting cover!" }, { "AC-gen6-low_self-2.ogg", "Hit hard, running on fumes!" } }, ["low_player"] = { { "AC-gen6-low_player-1.ogg", "You're trailing smoke, lead, disengage!" }, { "AC-gen6-low_player-2.ogg", "Lead, you can't take another hit, pull back!" } }, ["swarm"] = { { "AC-gen6-swarm-1.ogg", "They keep coming, I count over a dozen!" }, { "AC-gen6-swarm-2.ogg", "That's a lot of toasters, let's thin them out." } } } }
local VOICES = { "shadow", "flask", "turbo", "crispy", "hammer", "harridan", "rapt", "gen1", "gen3", "gen4", "gen5", "gen6" }
local NAMED = { ["Red 2"] = "shadow", ["Red 3"] = "flask", ["Blue 1"] = "turbo", ["Blue 2"] = "crispy",
                ["Nightjar 2"] = "shadow", ["Nightjar 3"] = "flask" }
local DEBUG = false
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
  for i = 1, #name do h = (h * 31 + string.byte(name, i)) % 9973 end
  return VOICES[h % #VOICES + 1]
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
  if math.floor(t) % 60 == 0 then dbg("tick " .. tostring(player ~= nil) .. " t=" .. math.floor(t)) end
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
