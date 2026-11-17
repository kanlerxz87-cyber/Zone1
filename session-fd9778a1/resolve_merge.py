"""Resolve the pass-13 merge collision between arena/fd9778a1-zone1 and origin/main.

Both sessions numbered their new rows off the same base (913d0ab), so ids collided:
main took SG-36..SG-38, Q-27..Q-28, S38..S42, TP-22..TP-23 and flags F83..F84 first,
and main is already merged. This script keeps main's rows at the ids they published
under and shifts *this* session's rows up, everywhere the id appears - including inside
prose and cross-reference arrays - so no reference silently points at another session's
row. Nothing is deleted.

Run from the repository root with the merge in progress.
"""
import json
import re
import sys

SG_SHIFT, Q_SHIFT, TP_SHIFT, F_SHIFT = 3, 2, 2, 2
MY_SG = [f"SG-{i:02d}" for i in range(36, 46)]          # SG-36 .. SG-45
MY_Q = [f"Q-{i:02d}" for i in range(27, 38)]             # Q-27  .. Q-37
MY_TP = ["TP-22", "TP-23", "TP-24"]
MY_F = [f"F{i}" for i in range(83, 88)]                  # F83 .. F87
MY_SOURCE = ("S38", "S43")

SG_MAP = {old: f"SG-{int(old[3:]) + SG_SHIFT:02d}" for old in MY_SG}
Q_MAP = {old: f"Q-{int(old[2:]) + Q_SHIFT:02d}" for old in MY_Q}
TP_MAP = {old: f"TP-{int(old[3:]) + TP_SHIFT:02d}" for old in MY_TP}
F_MAP = {old: f"F{int(old[1:]) + F_SHIFT}" for old in MY_F}


ALL_MAP = {}
ALL_MAP.update(SG_MAP)
ALL_MAP.update(Q_MAP)
ALL_MAP.update(TP_MAP)
ALL_MAP.update(F_MAP)
ALL_MAP[MY_SOURCE[0]] = MY_SOURCE[1]
# One pass, longest id first: applying one substitution after another would re-hit an id the
# previous rule just produced (Q-27 -> Q-29 -> Q-31), which silently invents a third row.
_ID = re.compile(r"\b(" + "|".join(sorted((re.escape(k) for k in ALL_MAP), key=len, reverse=True)) + r")\b(?![0-9])")


def remap_text(s):
    """Shift every reference to a row this session added, wherever it appears."""
    return _ID.sub(lambda m: ALL_MAP[m.group(1)], s)


def remap(obj):
    if isinstance(obj, str):
        return remap_text(obj)
    if isinstance(obj, list):
        return [remap(x) for x in obj]
    if isinstance(obj, dict):
        # ids appear as strings wherever they are used - as a row's own id, inside an id
        # array, inside a sentence - so one text rule covers all of them and cannot shift
        # anything twice.
        return {k: remap(v) for k, v in obj.items()}
    return obj


def load(where, name):
    with open(f"session-fd9778a1/{where}/{name}.json") as fh:
        return json.load(fh)


def save(name, obj):
    path = f"data/{name}.json"
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def by_id(rows):
    return {r["id"]: r for r in rows}


def report(label, *parts):
    print(f"{label}: " + " | ".join(str(p) for p in parts))


# ---------------------------------------------------------------- suggestions
base, main, mine = (load(w, "suggestions") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main))                      # main's meta + 37 rows
added = [remap(r) for r in mine["suggestions"] if r["id"] in SG_MAP]
out["suggestions"].extend(added)
# this session's path (drafted as P6) becomes P7, after main's money-path P6
my_path = [remap(p) for p in mine.get("paths", []) if p["id"] == "P6"]
for p in my_path:
    p["id"] = "P7"
out.setdefault("paths", []).extend(my_path)
# F87's lede repair, re-applied on main's meta (main did not change how_to_read[0])
if mine["how_to_read"][0] != base["how_to_read"][0]:
    out["how_to_read"][0] = mine["how_to_read"][0]
out["pass"] = (out.get("pass", "") + " | pass 13 shopfront + decision desk (arena/fd9778a1-zone1): "
               "SG-39…SG-48, path P7, numbered after the merged 2026-11-17 rows so no id collides.")
save("suggestions", out)
report("suggestions", len(out["suggestions"]), "rows",
       "paths", [p["id"] for p in out["paths"]], "new ids", [r["id"] for r in added])

# ---------------------------------------------------------------- questions
base_q, main_q, mine_q = (load(w, "questions") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main_q))
added = [remap(r) for r in mine_q["questions"] if r["id"] in Q_MAP]
out["questions"].extend(added)
for key in ("legend", "note", "how_to_read", "scoring_note"):
    if isinstance(mine_q.get(key), str) and mine_q[key] != base_q.get(key) and key in out:
        out[key] = mine_q[key]
save("questions", out)
report("questions", len(out["questions"]), "rows", "new ids", [r["id"] for r in added])

# ---------------------------------------------------------------- sources
base_s, main_s, mine_s = (load(w, "sources") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main_s))
new_src = remap([r for r in mine_s["sources"] if r["id"] == MY_SOURCE[0]][0])
new_src["id"] = MY_SOURCE[1]
out["sources"].append(new_src)
# my dated re-read stamps were appended to page_version; main did not touch those four rows
bmap, mmap = by_id(base_s["sources"]), by_id(main_s["sources"])
for r in mine_s["sources"]:
    if r["id"] not in ("S10", "S12", "S14", "S33"):
        continue
    was, now = bmap[r["id"]]["page_version"], mmap[r["id"]]["page_version"]
    delta = r["page_version"][len(was):] if r["page_version"].startswith(was) else " | " + r["page_version"]
    for tgt in out["sources"]:
        if tgt["id"] == r["id"]:
            tgt["page_version"] = (now + delta).strip()
            report("source stamp", r["id"], "+%d chars" % len(delta))
save("sources", out)
report("sources", len(out["sources"]), "rows", "new id", new_src["id"])

# ---------------------------------------------------------------- topics
base_t, main_t, mine_t = (load(w, "topics") for w in ("basereg", "mainreg", "minereg"))
out = json.loads(json.dumps(main_t))
# TP-21 is shared: main's row stays, this session's status/slug fields are applied on top
mmine = by_id(mine_t["topics"])
for tgt in out["topics"]:
    if tgt["id"] == "TP-21" and "TP-21" in mmine:
        for k, v in mmine["TP-21"].items():
            tgt[k] = v
        report("topics", "TP-21 fields taken from this session:", sorted(set(mmine["TP-21"]) - set(by_id(base_t["topics"])["TP-21"])))
out["topics"].extend(remap(r) for r in mine_t["topics"] if r["id"] in TP_MAP)
save("topics", out)
report("topics", len(out["topics"]), "rows", "ids", [t["id"] for t in out["topics"]][-6:])

# ---------------------------------------------------------------- requirements
base_r, main_r, mine_r = (load(w, "requirements") for w in ("basereg", "mainreg", "minereg"))
bmap, mmap, mmime = by_id(base_r["requirements"]), by_id(main_r["requirements"]), by_id(mine_r["requirements"])
out = json.loads(json.dumps(main_r))
touched = []
for tgt in out["requirements"]:
    rid = tgt["id"]
    if rid not in mmime:
        continue
    mine_row, main_row, base_row = mmime[rid], mmap[rid], bmap.get(rid, {})
    for field, val in mine_row.items():
        if field == "id":
            continue
        base_val = base_row.get(field)
        if val == base_val:
            continue                                     # only main changed it
        if main_row.get(field) == base_val:
            tgt[field] = remap(val) if isinstance(val, str) else remap(val)
            touched.append(f"{rid}.{field}")
        elif isinstance(val, list) and isinstance(main_row.get(field), list):
            keep = list(tgt[field])                       # both changed a list: union, main first
            for item in val:
                if item not in keep:
                    keep.append(remap(item))
            tgt[field] = keep
            touched.append(f"{rid}.{field} (union)")
        elif isinstance(val, str) and val != main_row.get(field):
            merged = main_row[field] if val.strip() in main_row[field] else main_row[field].rstrip(". ") + ". " + remap_text(val)
            tgt[field] = merged
            touched.append(f"{rid}.{field} (merged prose)")
save("requirements", out)
report("requirements", len(out["requirements"]), "rows", "fields applied", touched)

# ---------------------------------------------------------------- decision log + design prompt
merged = json.load(open("data/decision-log.json"))
keep, seen = [], set()
for row in merged.get("implemented", []):
    if row.get("session") == "arena/fd9778a1-zone1":
        row = remap(row)
    key = (row.get("id"), row.get("session"), row.get("date"))
    if key in seen:
        continue
    seen.add(key)
    keep.append(row)
merged["implemented"] = keep
report("decision-log", "implemented", [(r.get("id"), r.get("session")) for r in keep])

# design-prompt: main added no rows to any of the four lists (verified against origin/main),
# so the auto-merged file is correct except that prose inside *this session's* rows still
# names ids that have moved. Remap those rows, and the paste-ready prompt, and nothing else.
dp, mine_dp = json.load(open("data/design-prompt.json")), load("minereg", "design-prompt")
base_dp = load("basereg", "design-prompt")
for key in ("design", "tactics", "voice_rules", "decisions"):
    base_ids = {r["id"] for r in base_dp.get(key, [])}
    mine_ids = {r["id"] for r in mine_dp.get(key, [])}
    n = 0
    for i, r in enumerate(dp[key]):
        if r["id"] in base_ids or r["id"] not in mine_ids:
            continue
        dp[key][i] = remap(r)
        n += 1
    report("design-prompt", key, len(dp[key]), "rows remapped", n)
if dp.get("design_prompt") != base_dp.get("design_prompt"):
    dp["design_prompt"] = remap_text(dp["design_prompt"])
    report("design-prompt", "design_prompt", "remapped", len(dp["design_prompt"]), "chars")
save("design-prompt", dp)

# articles: not conflicted, but this session's three rows carry ids/sources that moved
art = json.load(open("data/articles.json"))
base_art = load("basereg", "articles")
mine_slugs = {a["slug"] for a in load("minereg", "articles")["articles"]} - {a["slug"] for a in base_art["articles"]}
n = 0
for i, a in enumerate(art["articles"]):
    if a["slug"] not in mine_slugs:
        continue
    b = next((x for x in base_art["articles"] if x["slug"] == a["slug"]), None)
    art["articles"][i] = remap(a) if b is None else a   # new rows: remap; unchanged rows: leave
    n += art["articles"][i] is not a
save("articles", art)
report("articles", len(art["articles"]), "rows", "this session's rows", sorted(mine_slugs), "remapped", n)

# ---------------------------------------------------------------- markdown evidence file
p = "reports/verification-2026-11-17-fd9778a1.md"
text = open(p).read()
open(p, "w").write(remap_text(text))
report("report", "ids remapped in place")
