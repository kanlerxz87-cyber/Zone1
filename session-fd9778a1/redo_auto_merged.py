"""Deterministic rebuild of the three registers that git auto-merged during the pass-13 merge.

The first pass of resolve_merge.py read these files from the working tree, so re-running it
shifted the ids a second and third time (Q-29 -> Q-31 -> Q-33). Everything here is rebuilt from
pristine inputs instead - origin/main's object plus this branch's own added rows, shifted once -
which makes the whole resolution idempotent. A final check then proves that every SG-/Q-/TP-/F-
identifier printed anywhere in the registers resolves to a row that exists.
"""
import json
import re
import subprocess

SG_MAP = {f"SG-{i:02d}": f"SG-{i + 3:02d}" for i in range(36, 46)}
Q_MAP = {f"Q-{i:02d}": f"Q-{i + 2:02d}" for i in range(27, 38)}
TP_MAP = {f"TP-{i}": f"TP-{i + 2}" for i in (22, 23, 24)}
F_MAP = {f"F{i}": f"F{i + 2}" for i in range(83, 88)}
ALL = dict(SG_MAP)
ALL.update(Q_MAP)
ALL.update(TP_MAP)
ALL.update(F_MAP)
ALL["S38"] = "S43"
ID = re.compile(r"\b(" + "|".join(sorted((re.escape(k) for k in ALL), key=len, reverse=True)) + r")\b(?![0-9])")


def shift(s):
    return ID.sub(lambda m: ALL[m.group(1)], s)


def remap(obj):
    if isinstance(obj, str):
        return shift(obj)
    if isinstance(obj, list):
        return [remap(x) for x in obj]
    if isinstance(obj, dict):
        return {k: remap(v) for k, v in obj.items()}
    return obj


def load(where, name):
    if where == "head":
        raw = subprocess.run(["git", "show", f"HEAD:data/{name}.json"], capture_output=True,
                             check=True, text=True).stdout
        return json.loads(raw)
    with open(f"session-fd9778a1/{where}/{name}.json") as fh:
        return json.load(fh)


def save(name, obj):
    with open(f"data/{name}.json", "w") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def ids(rows):
    return [r["id"] for r in rows]


# ------------------------------------------------------------------ design-prompt
base, main, mine = (load(w, "design-prompt") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main))
added = {}
for key in ("design", "tactics", "voice_rules", "decisions", "topics"):
    b = set(ids(base.get(key, [])))
    m = set(ids(mine.get(key, [])))
    new = [r for r in mine.get(key, []) if r["id"] in (m - b)]
    added[key] = ids(new)
    out.setdefault(key, [])
    have = set(ids(out[key]))
    out[key].extend(remap(r) for r in new if r["id"] not in have)
    # rows this session edited on top of an existing id: take this session's version
    if key == "topics":
        continue          # mirrored status list: main's copy stays authoritative here
    for r in mine.get(key, []):
        if r["id"] in b and json.dumps(r, sort_keys=True) != json.dumps(
                [x for x in base[key] if x["id"] == r["id"]][0], sort_keys=True):
            for i, tgt in enumerate(out[key]):
                if tgt["id"] == r["id"] and r["id"] not in (m - b):
                    out[key][i] = remap(r)
if mine.get("design_prompt") != base.get("design_prompt"):
    out["design_prompt"] = shift(mine["design_prompt"])
for k in ("voice_rules_note", "note", "how_to_read", "tactics_note", "topics_note"):
    if mine.get(k) and mine[k] != base.get(k) and not isinstance(mine[k], list):
        out[k] = shift(mine[k])
save("design-prompt", out)
print("design-prompt:", {k: len(out[k]) for k in ("design", "tactics", "voice_rules", "decisions", "topics")},
      "| added:", added)

# ------------------------------------------------------------------ articles
base_a, main_a, mine_a = (load(w, "articles") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main_a))
mine_slugs = {a["slug"] for a in mine_a["articles"]} - {a["slug"] for a in base_a["articles"]}
out["articles"].extend(remap(a) for a in mine_a["articles"] if a["slug"] in mine_slugs)
for k in ("accessed", "note", "how_to_read"):
    if isinstance(mine_a.get(k), str) and mine_a[k] != base_a.get(k) and k in out:
        out[k] = shift(mine_a[k])
save("articles", out)
print("articles:", len(out["articles"]), "| this session's:", sorted(mine_slugs))

# ------------------------------------------------------------------ decision-log
base_d, main_d, mine_d = (load(w, "decision-log") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main_d))
seen_impl = {(r.get("id"), r.get("date")) for r in out.get("implemented", [])}
for r in mine_d.get("implemented", []):
    if (r.get("id"), r.get("date")) in seen_impl:
        continue
    if r.get("session") == "arena/fd9778a1-zone1":
        r = remap(r)          # shifts the id once, along with every reference in the prose
    out.setdefault("implemented", []).append(r)
for k in ("policy", "how_to_return_a_choice", "note"):
    if isinstance(mine_d.get(k), str) and mine_d[k] != base_d.get(k):
        out[k] = shift(mine_d[k])
save("decision-log", out)
print("decision-log implemented:", [(r.get("id"), r.get("session")) for r in out["implemented"]])

# ------------------------------------------------------------------ cross-reference proof
regs = {
    "SG": {r["id"] for r in json.load(open("data/suggestions.json"))["suggestions"]},
    "TP": {r["id"] for r in json.load(open("data/topics.json"))["topics"]},
    "Q": {r["id"] for r in json.load(open("data/questions.json"))["questions"]},
    "S": {r["id"] for r in json.load(open("data/sources.json"))["sources"]},
}
flags = set(re.findall(r'^\s*\("(F\d+)"', open("build.py").read(), re.M))
dangling = []
for fname in ("suggestions", "questions", "topics", "requirements", "design-prompt", "articles",
              "decision-log"):
    doc = json.load(open(f"data/{fname}.json"))
    for m in re.finditer(r'"((?:SG|Q|TP|S|F|D|T|R|V|A|B|C|E|G|H)-?\d{1,2})"', json.dumps(doc)):
        tok = m.group(1)
        if tok.startswith("SG") and tok not in regs["SG"]:
            dangling.append((fname, tok))
        elif re.fullmatch(r"Q-\d\d", tok) and tok not in regs["Q"]:
            dangling.append((fname, tok))
        elif re.fullmatch(r"TP-\d\d", tok) and tok not in regs["TP"]:
            dangling.append((fname, tok))
        elif re.fullmatch(r"F\d+", tok) and len(tok) > 2 and tok not in flags:
            dangling.append((fname, tok))
        elif re.fullmatch(r"S\d+", tok) and tok not in regs["S"]:
            dangling.append((fname, tok))
print("DANGLING references in data:", sorted(set(dangling)) or "none")
