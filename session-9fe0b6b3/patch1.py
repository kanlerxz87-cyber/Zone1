"""Pass 13, patch 1: loads, the privacy-preserving counter, the footer notice."""
import re
import sys

P = "build.py"
s = open(P, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"expected {count} occurrence(s), found {n} of:\n{old[:200]}")
    s = s.replace(old, new)


# ---------------------------------------------------------------- loads ----
sub(
    'DESIGN_PROMPT = load("design-prompt.json")\n',
    'DESIGN_PROMPT = load("design-prompt.json")\n'
    '# Product-link register (added 2026-11-17, arena/9fe0b6b3). One row per supplied link,\n'
    '# holding two kinds of statement in separate blocks: what the account holder says the\n'
    '# link is for (intent) and what the link actually did when followed (observation).\n'
    '# They are never merged, and a build guard fails if they are.\n'
    'LINK_INTENT = load("link-intent.json")\n'
    '# Measurement contract (added 2026-11-17, arena/9fe0b6b3): five defined events, the\n'
    '# endpoint they are sent to, and the privacy rules the collector must follow.\n'
    'ANALYTICS = load("analytics.json")\n'
    '# Campaign ledger (added 2026-11-17, arena/9fe0b6b3): empty by design, fixed columns.\n'
    'LEDGER = load("ledger.json")\n'
    '# Site configuration - holds the Associates tracking ID supplied by the account holder.\n'
    'CONFIG = load("config.json")\n'
    'ASSOCIATE_TAG = (CONFIG.get("associate_tag") or "").strip()\n'
    'ANALYTICS_ENDPOINT = ((ANALYTICS.get("endpoint") or {}).get("url") or "").strip()\n'
    'ANALYTICS_EVENTS = ANALYTICS.get("events") or []\n'
    'LINK_ROWS = LINK_INTENT.get("links") or []\n',
)

# ------------------------------------------------- footer privacy notice ----
sub(
    '      <p>This site sets no cookies itself, runs no analytics, and has no comment forms or accounts. '
    'Following an Amazon link takes you to Amazon, whose own privacy notice and cookie practices apply from '
    'that point. No data you enter here is collected, because there is nowhere to enter it.</p>\n'
    '      <p class="tiny">Amazon\'s Program Policies §3(e) require an accurate statement of cookie and '
    'third-party technology use on Associate sites. This notice satisfies that requirement for the current '
    'build; it must be updated the moment any analytics, embeds or affiliate-network script is added.</p>\n',
    '      <p>{privacy_statement}</p>\n'
    '      <p class="tiny">Amazon\'s Program Policies §3(e) require an accurate statement of cookie and '
    'third-party technology use on Associate sites. {privacy_note}</p>\n',
)

# Compute the statement inside layout(), before the html f-string.
sub(
    '    desc = f\'<meta name="description" content="{e(description)}">\' if description else ""\n',
    '    desc = f\'<meta name="description" content="{e(description)}">\' if description else ""\n'
    '\n'
    '    # The privacy statement is generated from data/analytics.json rather than typed here.\n'
    '    # Program Policies §3(e) require an accurate statement of cookie and third-party\n'
    '    # technology use, and a hand-written sentence goes stale the moment collection is\n'
    '    # switched on - which is the one moment it matters. check_analytics_disclosure_realism()\n'
    '    # fails the build if the two ever disagree.\n'
    '    if ANALYTICS_ENDPOINT:\n'
    '        privacy_statement = (\n'
    '            "This site sets no cookies and has no comment forms or accounts. It sends five "\n'
    '            "anonymous event counts - page views, guides read to the end, chooser "\n'
    '            "completions, outbound product clicks and feed opens - to its own endpoint. "\n'
    '            "No name, email address, IP address, user-agent string or cross-site identifier "\n'
    '            "is stored, so two visits are indistinguishable. Following an Amazon link takes "\n'
    '            "you to Amazon, whose own privacy notice and cookie practices apply from that "\n'
    '            "point.")\n'
    '        privacy_note = (\n'
    '            "This notice is generated from the measurement configuration, so it changes in "\n'
    '            "the same commit that turns collection on.")\n'
    '    else:\n'
    '        privacy_statement = (\n'
    '            "This site sets no cookies itself, runs no analytics, and has no comment forms "\n'
    '            "or accounts. The outbound-click counter on these pages counts clicks in the "\n'
    '            "browser\'s own memory for the current visit and sends nothing anywhere, because "\n'
    '            "no endpoint is configured yet. Following an Amazon link takes you to Amazon, "\n'
    '            "whose own privacy notice and cookie practices apply from that point. No data "\n'
    '            "you enter here is collected, because there is nowhere to enter it.")\n'
    '        privacy_note = (\n'
    '            "This notice satisfies that requirement for the current build; it updates "\n'
    '            "automatically the moment an analytics endpoint is configured.")\n'
    '            "automatically the moment an analytics endpoint is configured.")\n',
)

# ------------------------------------------------------- measure.js tag ----
sub(
    '<script src="{prefix}assets/app.js"></script>\n',
    '<script src="{prefix}assets/measure.js" defer></script>\n'
    '<script src="{prefix}assets/app.js"></script>\n',
)

open(P, "w", encoding="utf-8").write(s)
print("patch 1 applied")
