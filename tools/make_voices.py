#!/usr/bin/env python3
"""Voice lines for the extra missions: zero-shot voice cloning (F5-TTS, run on the GPU container) from the original
Diaspora recordings + a radio effect, written as .ogg into the overlay mod.

  prepare MISSIONDIR JOBS.json [--only XM-DeepLook]   collect messages + senders, write the synthesis job list
  post    MISSIONDIR WAVDIR OUTDIR                    radio effect + Vorbis, writes OUTDIR/*.ogg and voice_manifest.json

The manifest (mission file -> message name -> wave name) is read by make_extra_missions.py, which then writes
`+Wave Name:` into the messages. The voices are cloned from the Diaspora actors' recordings: keep the generated
audio out of public repos unless the actors agree (the overlay mod on the Wolf install only).
"""
import glob
import json
import os
import re
import subprocess
import sys

# who sends the message (as used in send-message) -> reference voice
VOICE = {
    "#Command": "command", "Theseus": "command",
    "Red 1": "lantern",
    "Red 2": "shadow", "Blue 1": "turbo",
    "Red 3": "flask", "Blue 2": "crispy",
    "Halyard": "captain", "Bulwark": "lantern", "Sentry": "captain",
    "Cassia": "hauler", "Keplaw": "hauler", "Kestrel": "gen3", "Pilgrim Mercy": "gen4", "Hesper": "gen5",
    "Allsop": "gen6", "Pixie": "gen1", "Gull": "gen6", "Petrel": "gen3", "Briony": "gen5", "Tern": "hammer", "Aster": "rapt",
    "Lantern 1": "civilian", "Lantern 2": "obit", "Lantern 3": "harridan", "Gleaner 1": "obit",
    "Mender 1": "gen1", "Lifeline 1": "rapt",
    # the Nightjar cell (guerrilla campaign)
    "Roost": "harridan", "Nightjar 2": "shadow", "Nightjar 3": "flask", "Nightjar 4": "turbo",
}
DULL = {"flask"}	# voices whose reference recording is muffled (see post())
SPEED = {"briefing": 0.95, "turbo": 0.97, "obit": 0.95, "hammer": 0.97, "crispy": 0.97, "harridan": 0.95, "rapt": 0.97, "gen1": 0.97, "gen3": 0.97, "gen4": 0.97, "gen5": 0.97, "gen6": 0.97, "command": 0.95, "captain": 0.95, "hauler": 0.95, "civilian": 0.92, "lantern": 0.95, "shadow": 0.97, "flask": 0.97, "ghost": 0.97, "rook": 0.97}
SHORT = {"XM-DeepLook": "DL", "XM-Tylium": "TY", "XM-Hollow": "HR", "XM-Shepherd": "IS", "XM-Station": "SK",
         "XM-Reckoning": "DR", "XM-Firebreak": "FB", "XM-Hunter": "HM", "XM-Anvil": "HA", "XM-Vigil": "VG"}

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " and " + num_words(n % 100))
    return str(n)


def spoken(text):
    """Digits as words (the TTS stumbles over them): 'Lantern 3' -> 'Lantern three', '212' -> 'two hundred and twelve'."""
    text = re.sub(r"\bTYPE\b", "type", text)
    text = re.sub(r"(\d+)\s*km\b", lambda m: num_words(int(m.group(1))) + " kilometers", text)
    text = re.sub(r"\b(\d+)\b", lambda m: num_words(int(m.group(1))), text)
    return text



def read_messages(path):
    s = open(path, encoding="latin-1").read().replace("\r\n", "\n")
    msec = s.split("#Messages")[1].split("\n#")[0]
    msgs = {}
    for blk in re.split(r"\n\$Name: ", msec)[1:]:
        name = blk.split("\n", 1)[0].strip()
        t = re.search(r'XSTR\("(.*?)", -?\d+\)', blk, re.S)
        if t:
            msgs[name] = re.sub(r"\s+", " ", t.group(1)).strip()
    events = s.split("#Events")[1].split("\n#Goals")[0]
    senders = {}
    for sender, msg in re.findall(r'\(\s*send-message\s+"([^"]+)"\s+"[^"]+"\s+"([^"]+)"', events):
        senders.setdefault(msg, sender)
    return msgs, senders


def prepare(mdir, jobs_path, only=None):
    meta = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice_refs", "meta.json")))
    lines, used = [], set()
    for f in sorted(glob.glob(os.path.join(mdir, "XM-*.fs2"))):
        base = os.path.basename(f)[:-4]
        if only and base != only:
            continue
        msgs, senders = read_messages(f)
        n = 0
        for name, text in msgs.items():
            sender = senders.get(name)
            if sender not in VOICE:
                continue
            n += 1
            voice = VOICE[sender]
            used.add(voice)
            lines.append({"id": "%s-%02d" % (base, n), "mission": base + ".fs2", "message": name, "voice": voice,
                          "speed": SPEED[voice], "text": spoken(text)})
    refs = {v: {"wav": meta[v]["wav"], "text": meta[v]["text"]} for v in used}
    json.dump({"refs": refs, "lines": lines}, open(jobs_path, "w"), indent=1)
    print("%d lines, voices: %s" % (len(lines), ", ".join(sorted(used))))


RADIO = ("highpass=f=280,lowpass=f=3900,acompressor=threshold=-22dB:ratio=3:attack=5:release=80,"
         "acrusher=bits=12:mode=log:aa=1:mix=0.18,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=44100")


def post(mdir, wavdir, outdir):
    jobs = json.load(open(os.path.join(wavdir, "jobs.json")))
    os.makedirs(outdir, exist_ok=True)
    manifest = {}
    for ln in jobs["lines"]:
        src = os.path.join(wavdir, ln["id"] + ".wav")
        if not os.path.exists(src):
            print("missing", src)
            continue
        wave = ln["id"] + ".ogg"
        dst = os.path.join(outdir, wave)
        # squelch click before and after, band-limited voice in between, 44.1 kHz stereo Vorbis like the original lines
        click = "anoisesrc=d=0.045:c=white:a=0.05:r=44100,highpass=f=1500,lowpass=f=5000,afade=t=out:d=0.045"
        # voices cloned from a muffled source recording (flask) lack the radio presence band and hiss the others inherit:
        # boost it and add a band-limited static bed so every voice sounds like it is on the same channel
        dull = ln["voice"] in DULL
        pre = ",equalizer=f=3000:t=q:w=0.9:g=15,equalizer=f=1800:t=q:w=1:g=7" if dull else ""
        inputs = ["-i", src, "-f", "lavfi", "-i", click, "-f", "lavfi", "-i", click]
        if dull:
            inputs += ["-f", "lavfi", "-i", "anoisesrc=d=40:c=pink:a=0.08:r=44100"]
            graph = ("[0:a]aresample=44100%s,%s[v];[v]apad=pad_dur=0.1[v2];[3:a]highpass=f=1500,lowpass=f=3900[bed];"
                     "[v2][bed]amix=inputs=2:duration=first:normalize=0[vb];[1:a][vb][2:a]concat=n=3:v=0:a=1,aformat=channel_layouts=stereo[out]") % (pre, RADIO)
        else:
            graph = "[0:a]aresample=44100,%s[v];[v]apad=pad_dur=0.1[v2];[1:a][v2][2:a]concat=n=3:v=0:a=1,aformat=channel_layouts=stereo[out]" % RADIO
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                        "-c:a", "libvorbis", "-q:a", "4", dst], check=True)
        manifest.setdefault(ln["mission"], {})[ln["message"]] = wave
    json.dump(manifest, open(os.path.join(outdir, "voice_manifest.json"), "w"), indent=1)
    print("wrote %d ogg files" % sum(len(v) for v in manifest.values()))


def prepare_brief(mdir, jobs_path):
    """One job per mission briefing (the text of its first briefing stage); the Nightjar cell briefs with the Roost voice."""
    meta = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice_refs", "meta.json")))
    lines, used = [], set()
    for f in sorted(glob.glob(os.path.join(mdir, "XM-*.fs2"))):
        base = os.path.basename(f)[:-4]
        s = open(f, encoding="latin-1").read().replace("\r\n", "\n")
        m = re.search(r"#Briefing\n\$start_briefing\n\$num_stages: 1\n\$start_stage\n\$multi_text\n XSTR\(\"(.*?)\", -1\)", s, re.S)
        if not m:
            continue
        voice = "briefing"   # the briefing officer of the original campaign (SP-04-B-03) for every mission
        used.add(voice)
        lines.append({"id": base + "-B-01", "mission": base + ".fs2", "message": "briefing", "voice": voice, "speed": SPEED[voice],
                      "text": spoken(re.sub(r"\s+", " ", m.group(1)))})
    json.dump({"refs": {v: {"wav": meta[v]["wav"], "text": meta[v]["text"]} for v in used}, "lines": lines}, open(jobs_path, "w"), indent=1)
    print("%d briefings" % len(lines))


def post_brief(wavdir, outdir):
    """Briefings are narration, not radio: loudness only, 44.1 kHz stereo Vorbis like the original briefing audio."""
    os.makedirs(outdir, exist_ok=True)
    for src in sorted(glob.glob(os.path.join(wavdir, "*-B-01.wav"))):
        dst = os.path.join(outdir, os.path.basename(src)[:-4] + ".ogg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", "aresample=44100,loudnorm=I=-18:TP=-1.5:LRA=9,apad=pad_dur=0.2",
                        "-ac", "2", "-c:a", "libvorbis", "-q:a", "5", dst], check=True)
    print("wrote", len(glob.glob(os.path.join(outdir, "*.ogg"))), "briefings")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prepare":
        only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
        prepare(sys.argv[2], sys.argv[3], only)
    elif cmd == "prepare-brief":
        prepare_brief(sys.argv[2], sys.argv[3])
    elif cmd == "post-brief":
        post_brief(sys.argv[2], sys.argv[3])
    elif cmd == "post":
        post(sys.argv[2], sys.argv[3], sys.argv[4])
