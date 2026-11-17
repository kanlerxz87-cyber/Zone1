"""Second merge of pass 13 with `main` (2026-11-17) - a real three-way merge, row by row.

`main`'s newest sessions (arena/79743fd2, arena/16adefc5) re-serialised the register files and
claimed Q-29 for a measurement question, so a textual merge is unreadable and this pass has to
renumber once more. Inputs, all read from git so the run is repeatable:

  BASE  272da81            the common ancestor (origin/main before their two new PRs)
  MINE  HEAD               this branch, first merge result - holds this pass's rows and edits
  MAIN  origin/main        the published state, which wins whenever it changed a row itself

Per row: main unchanged -> this branch's version (its edits survive); this branch unchanged ->
main's version; both changed -> main's version, and the row is printed for a human to re-read,
never silently blended. Rows only one side has are kept by both rules, so nothing is dropped.
This pass's question rows, and every place this pass names them, then shift Q-29..Q-39 ->
Q-30..Q-40 in ONE substitution pass (a sequential per-id replace re-hits what it just produced).
"""
import json
import re
import subprocess

BASE, MINE, MAIN = "272da81", "HEAD", "origin/main"
MY_Q = [f"Q-{i}" for i in range(29, 40)]
Q_MAP = {old: f"Q-{int(old[2:]) + 1}" for old in MY_Q}
ID = re.compile(r"\b(" + "|".join(sorted(map(re.escape, Q_MAP), key=len, reverse=True)) + r")\b(?![0-9])")
shift = lambda s: ID.sub(lambda m: Q_MAP[m.group(1)], s)
remap = lambda o: ([remap(x) for x in o] if isinstance(o, list) else
                   {k: remap(v) for k, v in o.items()} if isinstance(o, dict) else
                   shift(o) if isinstance(o, str) else o)
dump = lambda o: json.dumps(o, sort_keys=True)


def show(rev, name):
    return json.loads(subprocess.run(["git", "show", f"{rev}:data/{name}.json"],
                                     capture_output=True, text=True, check=True).stdout)


def key(row):
    return row.get("id") or row.get("slug") or dump(row)[:60]


LIST = {"questions": "questions", "suggestions": "suggestions", "requirements": "requirements",
        "articles": "articles", "topics": "topics", "sources": "sources",
        "decision-log": "implemented", "design-prompt": None}
contested = []
merged_files = {}
for name, lst in LIST.items():
    objs = {}
    for rev in (BASE, MINE, MAIN):
        try:
            objs[rev] = show(rev, name)
        except subprocess.CalledProcessError:
            objs[rev] = {}
    def rows(doc):
        if lst is None:
            return None
        return doc.get(lst, []) if name == "decision-log" else doc.get(lst, [])
    b, m, n = (rows(objs[r]) for r in (BASE, MINE, MAIN))
    if name == "questions":
        # this pass's question rows are renumbered *before* the row-level comparison, so the
        # row main claims as Q-29 is not mistaken for this pass's Q-29 and dropped as a collision.
        m = [remap(r) for r in m]
    if b is None:                       # design-prompt: several lists, merged below
        merged_files[name] = None
        continue
    bb = {key(r): r for r in b}
    mb = {key(r): r for r in m}
    nb = {key(r): r for r in n}
    out_rows, seen = [], set()
    for k in [key(r) for r in n] + [key(r) for r in m if key(r) not in nb]:
        if k in seen:
            continue
        seen.add(k)
        if k in nb and k in mb and k in bb:
            if dump(nb[k]) == dump(bb[k]):
                out_rows.append(mb[k])                      # main untouched -> this branch's edit
            elif dump(mb[k]) == dump(bb[k]):
                out_rows.append(nb[k])                      # branch untouched -> main's edit
            else:
                out_rows.append(nb[k])                      # both changed -> main wins, reported
                contested.append(f"{name}:{k}")
        elif k in nb:
            out_rows.append(nb[k])
        else:
            out_rows.append(mb[k])          # already shifted, once, above
    doc = json.loads(json.dumps(objs[MAIN]))                # main's top-level meta wins
    if name == "decision-log":
        doc[lst] = out_rows
    else:
        doc[lst] = out_rows
    merged_files[name] = doc
    print(f"{name:14s} base {len(bb):3d} main {len(nb):3d} branch {len(mb):3d} -> merged {len(out_rows):3d}")

# ------------------------------------------------------------------- design-prompt (list of lists)
dp_b, dp_m, dp_n = (show(r, "design-prompt") for r in (BASE, MINE, MAIN))
doc = json.loads(json.dumps(dp_n))
for lst in ("design", "tactics", "voice_rules", "decisions", "topics"):
    bb = {r["id"]: r for r in dp_b.get(lst, [])}
    mb = {r["id"]: r for r in dp_m.get(lst, [])}
    nb = {r["id"]: r for r in dp_n.get(lst, [])}
    rows = []
    for k in list(nb) + [k for k in mb if k not in nb]:
        if k in nb and k in mb and dump(nb[k]) != dump(bb.get(k)) and dump(mb[k]) != dump(bb.get(k)):
            contested.append(f"design-prompt:{lst}:{k}")
            rows.append(nb[k])
        elif k in nb and dump(nb[k]) != dump(bb.get(k)):
            rows.append(nb[k])
        elif k in mb:
            rows.append(mb[k])
        else:
            rows.append(nb[k])
    doc[lst] = rows
for field in ("design_prompt", "topics_note", "voice_rules_note", "lede", "note"):
    if dump(dp_m.get(field)) != dump(dp_b.get(field)) and dp_m.get(field) is not None:
        doc[field] = remap(dp_m[field])
merged_files["design-prompt"] = doc
print("design-prompt   design", len(doc["design"]), "tactics", len(doc["tactics"]),
      "voice", len(doc["voice_rules"]), "decisions", len(doc["decisions"]), "topics", len(doc["topics"]))

# ------------------------------------------------------------------- write, then shift this pass's rows
MY_SG = {f"SG-{i}" for i in range(39, 49)}
MY_TP = {"TP-24", "TP-25", "TP-26"}
MY_SLUGS = {"chefman-vs-emeril-air-fryer", "ninety-eight-percent-less-oil-claim",
            "questions-before-buying-a-multifunction-appliance"}
MY_REQ = {"A-02", "A-03", "A-04", "A-05", "B-01", "B-08", "D-01"}
for doc in merged_files.values():
    if doc is None:
        continue
    for lst in ("suggestions", "requirements", "topics", "articles", "implemented"):
        rows = doc.get(lst)
        if not rows:
            continue
        for i, r in enumerate(rows):
            k = key(r)
            hit = ((lst == "suggestions" and k in MY_SG) or (lst == "topics" and k in MY_TP)
                   or (lst == "articles" and k in MY_SLUGS)
                   or (lst == "implemented" and r.get("session") == "arena/fd9778a1-zone1"))
            if lst == "requirements" and k in MY_REQ and dump(r) != dump(
                    {x["id"]: x for x in show(BASE, "requirements")["requirements"]}.get(k, {})):
                hit = dump(r) != dump({x["id"]: x for x in show(MAIN, "requirements")["requirements"]}.get(k))
            if hit:
                rows[i] = remap(r)
for name, doc in merged_files.items():
    if doc is None:
        continue
    with open(f"data/{name}.json", "w") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# build.py: the five flag rows this pass added name its questions.
src = open("build.py", encoding="utf-8").read()
head_src = show("HEAD", "build.py") if False else subprocess.run(
    ["git", "show", "HEAD:build.py"], capture_output=True, text=True, check=True).stdout
START_MARK = '    ("F85", "The article set is tracked'
END_MARK = '    ("F8", "IP License'
hs, he = head_src.index(START_MARK), head_src.index(END_MARK, head_src.index(START_MARK))
bs, be = src.index(START_MARK), src.index(END_MARK, src.index(START_MARK))
block = head_src[hs:he]                       # pristine, then shifted exactly once
src = src[:bs] + shift(block) + src[be:]
open("build.py", "w", encoding="utf-8").write(src)
print("build.py flag rows:", len(ID.findall(block)), "tokens shifted (from the branch copy)")

# the verification report, and the questions' own ids are already shifted above
p = "reports/verification-2026-11-17-fd9778a1.md"
t = subprocess.run(["git", "show", f"HEAD:{p}"], capture_output=True, text=True, check=True).stdout
open(p, "w", encoding="utf-8").write(shift(t))
print("report:", len(ID.findall(t)), "tokens shifted")

# COORDINATION.md is append-only: keep both sides, main's record first.
txt = open("COORDINATION.md", encoding="utf-8").read()
pat = re.compile(r"<<<<<<< [^\n]*\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n", re.S)
while True:
    m = pat.search(txt)
    if not m:
        break
    txt = txt[:m.start()] + m.group(2).rstrip("\n") + "\n\n" + m.group(1).strip("\n") + "\n" + txt[m.end():]
open("COORDINATION.md", "w", encoding="utf-8").write(txt)
print("COORDINATION.md markers left:", txt.count("<<<<<<<"))

# ------------------------------------------------------------------- prove nothing dangles
pools = {"SG": {r["id"] for r in json.load(open("data/suggestions.json"))["suggestions"]},
         "Q": {r["id"] for r in json.load(open("data/questions.json"))["questions"]},
         "TP": {r["id"] for r in json.load(open("data/topics.json"))["topics"]}}
srcs = {r["id"] for r in json.load(open("data/sources.json"))["sources"]}
flags = set(re.findall(r'^\s*\("(F\d+)"', open("build.py").read(), re.M))
dangling = []
for f in list(LIST) + ["products", "config", "measurement", "marketing"]:
    try:
        doc = json.dumps(json.load(open(f"data/{f}.json")))
    except (FileNotFoundError, json.JSONDecodeError):
        continue
    for m in re.finditer(r'"((?:SG|Q|TP)-\d{2}|S\d{1,2})"', doc):
        tok = m.group(1)
        pool = pools.get(tok.split("-")[0], srcs)
        if tok not in pool:
            dangling.append((f, tok))
for m in re.finditer(r'^\s*\("(F\d+)"', open("build.py").read(), re.M):
    pass
print("CONTESTED rows (main won, worth a re-read):", contested or "none")
print("dangling references:", sorted(set(dangling)) or "none")
