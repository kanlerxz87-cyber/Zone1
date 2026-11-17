#!/usr/bin/env python3
"""Record S39/S40 (read 2026-11-17) in the registers that argued from the URL instead.

The correction is dated and additive everywhere: no earlier pass's observation sentence is
rewritten, because those sentences are records of what a pass concluded on its own date.
"""
import json
from pathlib import Path

ROOT = Path("/home/user/Zone1")


def rw(name, fn):
    p = ROOT / name
    d = json.loads(p.read_text(encoding="utf-8"))
    fn(d)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


CORRECTION = {
    "url_absence_is_not_evidence": (
        "Amazon's own help node, read 2026-11-17 (S39), states that 'it is not necessary for your unique ID to appear in "
        "order for us to track sales made after the initial click through' because the shopping session is tagged on "
        "Amazon's side. The absence of a tag= parameter on an observed landing URL is therefore a null observation, not "
        "a negative one: it cannot be cited as evidence that a link failed to attribute. The positive still has to come "
        "from inside the account — the Tracking ID Summary Report named by S40."
    ),
    "management_screen": (
        "Two official nodes name the same screen (S6, S40): Associates Central > 'Manage your Tracking ID', linked as "
        "https://affiliate-program.amazon.com/home/account/tag/manage. S40 also records a limit of 100 tracking IDs per "
        "associate account and that each ID's data appears in the Tracking ID Summary Report — which is where a click "
        "test is actually read."
    ),
}


def fix_intent(d):
    st = d["selected_tracking_id"]
    st["observation_method_correction"] = dict(CORRECTION)
    st["correction_date"] = "2026-11-17"
    fc = st.setdefault("format_check", {})
    fc["note_2026_11_17"] = CORRECTION["url_absence_is_not_evidence"]
    st["owner_action"]["where_is_documented"] = "S6, S40"
    st["owner_action"]["confirmation_is_read_in"] = "Tracking ID Summary Report (S40)"


def fix_questions(d):
    for q in d["questions"]:
        if q["id"] == "Q-28":
            q["what_we_know"].append(
                "Read the same day: Amazon's help node states that a tracking ID does not need to appear in the click-"
                "through URL for the sale to be attributed, because the session is tagged on Amazon's side (S39). The "
                "clean landing URLs recorded against these links therefore prove nothing either way, and an earlier "
                "pass's reliance on that absence is corrected on the register page rather than edited out of history.")
            q["sources"].append({"label": "Amazon — why a tracking ID need not appear in the click-through URL",
                                 "url": "https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3"})
            q["sources"].append({"label": "Amazon — how multiple tracking IDs are created, and where each ID's data is read",
                                 "url": "https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU"})
            q["how_to_discover"] = (
                "Open Manage your Tracking ID (the screen S6 and S40 both name) and check for shopnow047c-20. Then click "
                "one published product link and confirm the click appears in that ID's Tracking ID Summary Report — the "
                "URL you land on is not the evidence, per S39. Write the date into "
                "associates_central_confirmation_date, cite the screen as the source, and set tagging_gate.state to open.")
        if q["id"] == "Q-04":
            q.setdefault("answer_notes", []).append(
                "2026-11-17 (arena/58cbaaa2): the tracking-ID half of this question was partially answered by the account "
                "holder (shopnow047c-20, recorded as user-provided) and the observation method was corrected by S39 — see "
                "Q-28, which now carries the remaining unknown.")


def fix_suggestions(d):
    for s in d["suggestions"]:
        if s["id"] == "SG-37":
            s["evidence"].append({"label": "Amazon — a tracking ID need not appear in the URL to attribute (S39)",
                                  "url": "https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3"})
            s["evidence"].append({"label": "Amazon — multiple tracking IDs, the 100-ID limit, the summary report (S40)",
                                  "url": "https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU"})
            s["problem"] += (" Two help nodes read on the same day also narrow what this register may claim from a URL: "
                              "Amazon states that the ID need not appear in the click-through URL for attribution to work "
                              "(S39), so the clean landing URLs are not evidence against the links — the confirmation is "
                              "a report row, read in the Tracking ID Summary Report (S40).")


def fix_requirements(d):
    for r in d["requirements"]:
        if r["id"] == "H-02":
            r["sources"] = ["S6", "S2", "S39", "S40"]
            r["why"] += (" Read the same day, S39 corrected the site's own reasoning: because a tracking ID does not need "
                         "to appear in the click-through URL for attribution to work, the register does not cite the clean "
                         "landing URLs as evidence of anything; S40 supplies the screen, the 100-ID limit and the report "
                         "where a click test is read.")
            r["where"] = ["data/product-intent-confirmations.json", "links.html", "build.py", "measurement.html"]


def fix_measurement(d):
    plan = d.get("sub_tag_plan") or {}
    ids = {s["id"] for s in plan.get("sources") or []}
    if "S40" not in ids:
        plan.setdefault("sources", []).append({
            "id": "S40",
            "used_for": ("The screen where additional IDs are created, the 100-IDs-per-account limit, and the "
                         "Tracking ID Summary Report where each ID's data is read — the report that answers Q-28"),
        })
    plan["limit"] = (plan["limit"] + " S40 records a limit of 100 tracking IDs per associate account, so per-channel "
                     "sub-tags are not a scarce resource at this site's scale.")
    d["sub_tag_plan"] = plan
    d["updated"] = "2026-11-17"


def fix_decision(d):
    for k, v in list(d.items()):
        if isinstance(v, str) and "show no tag in their landing URL" in v:
            d[k] = v + (" — and per S39 a URL without a visible tag is not evidence of failed attribution, so that "
                        "observation is recorded as a null one, not as a finding.")


rw("data/product-intent-confirmations.json", fix_intent)
rw("data/questions.json", fix_questions)
rw("data/suggestions.json", fix_suggestions)
rw("data/requirements.json", fix_requirements)
rw("data/measurement.json", fix_measurement)
try:
    rw("data/decision.json", fix_decision)
    print("decision.json touched")
except Exception as exc:                                  # noqa: BLE001
    print("decision.json skipped:", exc)
print("S39/S40 recorded in 5 registers")
