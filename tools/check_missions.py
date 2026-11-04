#!/usr/bin/env python3
"""Static check of generated missions: python3 -I tools/check_missions.py DIR  (operators + argument counts from the engine's
sexp.cpp, every referenced name exists, ship classes exist, no duplicate event names)."""
import glob, re, sys, os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
src = open(root + "/fs2open/code/parse/sexp.cpp", encoding="latin-1").read()
arity = {m.group(1): (int(m.group(2)), int(m.group(3))) for m in re.finditer(r'\{\s*"([^"]+)",\s*OP_\w+,\s*(-?\d+),\s*(-?\d+)', src)}
inf = {m.group(1): int(m.group(2)) for m in re.finditer(r'\{\s*"([^"]+)",\s*OP_\w+,\s*(-?\d+),\s*INT_MAX', src)}
classes = set(re.findall(r'^\$Name:[ \t]*(.+?)\s*$', open(root + "/extracted/R1.1_Patch/data/tables/ships.tbl", encoding="latin-1").read(), re.M))
import glob as _glob
for _tbm in _glob.glob(root + "/overlay/diaspora_fixes/data/tables/*-shp.tbm"):
    classes |= set(re.findall(r'^\$Name:[ \t]*(.+?)\s*$', open(_tbm, encoding="latin-1").read(), re.M))


def parse(t, i):
    i += 1; items = []
    while t[i] != ')':
        if t[i] == '(':
            n, i = parse(t, i); items.append(n)
        else:
            items.append(t[i]); i += 1
    return items, i + 1


allok = True
for f in sorted(glob.glob(sys.argv[1] + "/*.fs2")):
    s = open(f, encoding="latin-1").read()
    sec = lambda name: s.split('#' + name)[1].split('\n#')[0]
    names = lambda sect, key: re.findall(r'^\%s: ([^\t\r\n]+)' % key, sec(sect), re.M)
    known = set(names('Objects', '$Name')) | set(names('Wings', '$Name')) | set(names('Events', '+Name')) | set(names('Messages', '$Name')) | set(names('Waypoints', '$Name')) | {'#Command', 'High', 'Low', 'Normal'}
    ev = names('Events', '+Name'); dup = sorted({e for e in ev if ev.count(e) > 1})
    bad, unres = [], set()
    for line in s.split('\n'):
        if not line.startswith(('$Formula:', '$Arrival Cue:', '$Departure Cue:', '$AI Goals:')):
            continue
        body = line.split(':', 1)[1]
        unres |= {r for r in re.findall(r'"([^"]+)"', body) if r not in known and not re.fullmatch(r'(.+):\d+', r) or
                  (re.fullmatch(r'(.+):\d+', r) and re.fullmatch(r'(.+):\d+', r).group(1) not in known)}
        if line.startswith('$AI Goals:'):
            continue
        tree, _ = parse(re.findall(r'\(|\)|"[^"]*"|[^\s()]+', body), 0)
        def walk(n):
            if isinstance(n, list) and n and isinstance(n[0], str) and not n[0].startswith('"'):
                op, args = n[0], n[1:]
                if op in arity and not (arity[op][0] <= len(args) <= arity[op][1]): bad.append((op, len(args)))
                elif op in inf and len(args) < inf[op]: bad.append((op, len(args)))
                elif op not in arity and op not in inf: bad.append(('UNKNOWN ' + op,))
                for a in args: walk(a)
            elif isinstance(n, list):
                for a in n: walk(a)
        walk(tree)
    cls = set(re.findall(r'^\$Class: ([^\r\n]+)', s, re.M)) - classes
    ok = not (bad or unres or cls or dup); allok &= ok
    if not ok: print(os.path.basename(f), bad, sorted(unres), sorted(cls), dup)
print("ALL OK" if allok else "FIX NEEDED")
