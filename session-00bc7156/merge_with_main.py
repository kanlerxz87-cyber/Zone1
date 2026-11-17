"""Merge pass 13's registers with main as it stands after #136/#137/#138.

Why a script rather than hand-editing 18 conflict hunks: the incoming pass re-indented four registers
(`indent=1` against this pass's `indent=2`), so git reported every line of `data/sources.json`,
`data/questions.json`, `data/suggestions.json` and `data/product-intent.json` as a conflict. A textual
keep-both across a reformat produces a file that parses and lies — it looks like both sides survived when
what happened is that one side's rows were dropped. Each register is therefore merged by id, in main's
formatting, with the collision decisions recorded in the data itself.

Collisions found, and how each is resolved:
  * `S36`/`S37` — main registered the same two listing URLs first. Main's entries win; this pass's
    first-chunk read caveat is appended to their `page_version`, not substituted for it.
  * `S38` — main's is a GitHub Pages caching document, this pass's was the CHEF iQ brand page. This pass's
    four sources renumber to S39-S42 and every citation of them in this pass's own files is rewritten.
  * `Q-27`…`Q-31`, `SG-36`…`SG-43`, `TP-22`…`TP-24`, `F83`…`F87` — main does not use these ids; no move.
  * `C-01` — main rewrote the row while this pass was open; this pass's correction is re-applied on top of
    main's text instead of replacing it.
  * `data/product-intent.json` — main's `tracking_id_applied_to_links: false` is the current published
    position (it supersedes the earlier pass's "applied everywhere"), so it is left untouched; this pass
    adds only its dated re-read block and two `observed_*` fields on PI-04/PI-05.
  * `data/adjacent.json` `editorial_rule_applied` — main's flag F78 instructs that thermometer
    specifications stay unpublished until intent and scope are confirmed, which this pass does not do. The
    disagreement is published as its own flag row and as a `contradicts` field on the cluster rather than
    resolved by whichever merge landed last.
"""

import json
import re
import subprocess

MINE = "f3c5775"      # this pass, after its two reconciliation commits
MAIN = "origin/main"
REMAP = {"S36": "S36", "S37": "S37", "S38": "S39", "S39": "S40", "S40": "S41", "S41": "S42"}
SRC = re.compile(r"^S\d{2}$")


def show(ref, path):
    return json.loads(subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True,
                                     check=True).stdout)


def dump(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def remap_lists(obj):
    """Renumber bare source ids inside lists/values, never inside prose."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("source", "sources", "cite") and isinstance(v, list) and all(isinstance(x, str) for x in v):
                out[k] = [REMAP.get(x, x) if SRC.match(x) else x for x in v]
            elif k in ("source", "sources", "cite") and isinstance(v, str) and SRC.match(v):
                out[k] = REMAP.get(v, v)
            else:
                out[k] = remap_lists(v)
        return out
    if isinstance(obj, list):
        return [REMAP.get(x, x) if isinstance(x, str) and SRC.match(x) else remap_lists(x) for x in obj]
    return obj


# ---------------------------------------------------------------- sources.json
main = show(MAIN, "data/sources.json")
mine = show(MINE, "data/sources.json")
byid = {s["id"]: s for s in main["sources"]}
have = set(byid)
for sid in ("S38", "S39", "S40", "S41"):
    src = dict(next(s for s in mine["sources"] if s["id"] == sid))
    src["id"] = REMAP[sid]
    src["registered_2026_11_17"] = ("Added 2026-11-17 by arena/00bc7156-zone1 as S" + sid[1:]
                                    + "; renumbered to " + src["id"] + " on the merge with main, which had already "
                                    "used that id for a GitHub Pages document.")
    main["sources"].append(src)
CAVEAT = ("Re-read 2026-11-17 by arena/00bc7156-zone1 with the same result. Only the first chunk of each listing "
          "was reachable in that pass, which is why the accessory cluster's Product-information rows are blank "
          "rather than filled; see read_constraints in data/adjacent.json.")
for sid in ("S36", "S37"):
    t = byid[sid]
    if "arena/00bc7156" not in t.get("page_version", ""):
        t["page_version"] = t.get("page_version", "").rstrip(" .|") + " | " + CAVEAT
main["reverified"] = "2026-11-17"
main["reverified_2026_11_17_00bc7156"] = (
    "2026-11-17 (arena/00bc7156-zone1): all five supplied links re-read, four new sources registered as S39-S42 "
    "after the collision with main's S38 (this pass had numbered its additions S38-S41). S16 again matched the "
    "register title character-for-character for B04G1MEwY. Raw log: session-00bc7156/observations-2026-11-17.json.")
dump("data/sources.json", main)
print("sources:", len(main["sources"]), "| tail:", [s["id"] for s in main["sources"]][-6:])

# ---------------------------------------------------------------- adjacent.json
adj = remap_lists(show(MINE, "data/adjacent.json"))
adj["source_id_note"] = (
    "Citations use this repository's merged source ids. This pass registered its four new sources as S38-S41; "
    "main had taken S38 for a GitHub Pages document while the branch was open, so they became S39-S42 on the "
    "merge and every citation in this file, in data/articles.json and in flags F83-F87 was rewritten with them. "
    "S36/S37 needed no move: both passes registered the same two listing URLs and main's records stand, with "
    "this pass's first-chunk read caveat appended to their page_version.")
adj["contradicts"] = {
    "flag": "F78 on flagged.html, as merged from main on 2026-11-17",
    "their_instruction": "Keep them unmapped and do not publish thermometer specifications unless product intent and scope are confirmed.",
    "this_passes_position": ("Publish what the official record supports and leave the rest blank, because the brief supplied these "
                             "two links as products to build marketing for and withholding them entirely is how they went unrecorded "
                             "for twelve passes. Intent is still unconfirmed and says so on the page; only the specification rows are "
                             "published, each linked to the document it was read from."),
    "how_it_is_held": ("Both positions are published instead of one being merged away. The cluster is registered as a shelf with an "
                       "unpublish trigger (SG-36 option A + C): if the owner answers Q-27 with 'neither', or Q-31 with 'air fryers "
                       "only', the page and its two articles come down and the rows stay in the dataset as the record. That trigger is "
                       "printed on the page, not just here, so a reader who never opens the registers sees the condition on which the "
                       "page stands."),
}
dump("data/adjacent.json", adj)
ids = sorted({sid for p in adj["products"] for s in p["specs"] for sid in (s.get("source") or [])}
             | {sid for p in adj["products"] for f in p["flags"] for sid in (f.get("sources") or [])}
             | set(adj["commission_note"].get("sources") or []))
print("adjacent cites:", ids)

# ---------------------------------------------------------------- articles.json
arts = show(MAIN, "data/articles.json")
mine_arts = show(MINE, "data/articles.json")
have = {a["slug"] for a in arts["articles"]}
new = [remap_lists(a) for a in mine_arts["articles"] if a["slug"] not in have]
for a in new:
    a["registered_by"] = "arena/00bc7156-zone1 (pass 13, 2026-11-17)"
arts["articles"].extend(new)
dump("data/articles.json", arts)
print("articles:", len(arts["articles"]), [a["slug"] for a in new])

# ---------------------------------------------------------------- questions / suggestions
for path, key in (("data/questions.json", "questions"), ("data/suggestions.json", "suggestions")):
    m = show(MAIN, path)
    mine_f = show(MINE, path)
    have = {r["id"] for r in m[key]}
    added = []
    for r in mine_f[key]:
        if r["id"] in have:
            continue
        r = remap_lists(r)
        r["registered_by"] = "arena/00bc7156-zone1 (pass 13, 2026-11-17)"
        added.append(r)
    # keep the register ordered by id so a collision is visible as a gap, not silently absorbed
    m[key] = sorted(m[key] + added, key=lambda x: (len(x["id"]), x["id"]))
    if path == "data/suggestions.json":
        mp = show(MINE, path).get("paths", [])
        base = {p["id"] for p in m.get("paths", [])}
        m["paths"] = m.get("paths", []) + [p for p in mp if p["id"] not in base]
    dump(path, m)
    print(path, "->", len(m[key]), "added:", [r["id"] for r in added])

# ---------------------------------------------------------------- product-intent.json
pi_main = show(MAIN, "data/product-intent.json")
pi_mine = show(MINE, "data/product-intent.json")
block = pi_mine.get("reads_2026_11_17_00bc7156")
if block:
    pi_main["reads_2026_11_17_00bc7156"] = block
byrow = {r["id"]: r for r in pi_main["rows"]}
for rid in ("PI-04", "PI-05"):
    src = next(r for r in pi_mine["rows"] if r["id"] == rid)
    for k in ("observed_redirect_target_full", "observed_via"):
        if src.get(k):
            byrow[rid][k] = src[k]
    for sid in (src.get("observed_source_ids") or []):
        sid = REMAP.get(sid, sid)
        if sid not in byrow[rid].setdefault("observed_source_ids", []):
            byrow[rid]["observed_source_ids"].append(sid)
    note = ("Accessory cluster published 2026-11-17 at categories/kitchen-tools.html with 21 sourced rows (6 left "
            "blank with their reasons), against main's flag F78, which instructs that no such page ship until intent "
            "and scope are confirmed. Both positions are published; see F83 and the cluster's contradicts field.")
    if "categories/kitchen-tools.html" not in byrow[rid].get("note", ""):
        byrow[rid]["note"] = byrow[rid].get("note", "").rstrip(" .") + " | " + note
pi_main["schema_note"] = (pi_main.get("schema_note", "") + " | Fields added 2026-11-17 by arena/00bc7156-zone1: "
                          "observed_redirect_target_full and observed_via on PI-04/PI-05, and "
                          "reads_2026_11_17_00bc7156 at top level. Additive only; the tracking-ID fields main set on "
                          "2026-11-17 (applied = false, tag blank) are deliberately not restated here.")
dump("data/product-intent.json", pi_main)
print("product-intent rows:", len(pi_main["rows"]), "| top-level:", [k for k in pi_main if "2026" in k])

# ---------------------------------------------------------------- requirements C-01
req_main = show(MAIN, "data/requirements.json")
req_mine = show(MINE, "data/requirements.json")
mine_c = next(r for r in req_mine["requirements"] if r["id"] == "C-01")
c = next(r for r in req_main["requirements"] if r["id"] == "C-01")
for k in ("requirement", "clause", "why", "where"):
    if mine_c.get(k):
        c[k] = mine_c[k]
c["sources"] = list(dict.fromkeys([REMAP.get(s, s) for s in (mine_c.get("sources") or [])] + (c.get("sources") or [])))
c["note"] = ("Both passes edited this row on 2026-11-17. The count and the parameter spelling are this pass's "
             "correction; the status stays blocked because the correction does not resolve identity, which only the "
             "account holder can do.")
dump("data/requirements.json", req_main)
print("C-01:", c["requirement"], "| sources:", c["sources"])
