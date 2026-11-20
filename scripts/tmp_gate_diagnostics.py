#!/usr/bin/env python3
"""TEMPORARY (arena/915c51ea-zone1). Echo browser-gate failure text into check-run annotations.

The Actions log and the `browser-gate-evidence` artifact are served from hosts that are not
reachable from the session sandbox, so a failing browser job cannot be read from there at all
(it is perfectly readable in the web UI). Annotations ARE reachable through the REST API, so
this script turns the same evidence into annotations and always exits 0. Delete once green.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def encode(text: str) -> str:
    return (text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A"))


def emit(label: str, text: str) -> None:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return
    print(f"::error::{encode(label)} :: {encode(text[:900])}")


def playwright_json() -> None:
    f = ROOT / "test-results" / "browser-results.json"
    if not f.exists():
        emit("playwright", "no test-results/browser-results.json produced")
        return
    data = json.loads(f.read_text(encoding="utf-8"))
    shown = 0

    def walk(node, trail):
        nonlocal shown
        for spec in node.get("specs", []):
            for test in spec.get("tests", []):
                for res in test.get("results", []):
                    errs = res.get("errors") or []
                    if res.get("status") in ("passed", "skipped") and not errs:
                        continue
                    title = " > ".join([x for x in (trail, spec.get("title")) if x])
                    detail = " | ".join((e.get("message") or e.get("value") or "") for e in errs)
                    emit("playwright:" + title, (detail or res.get("status", "?"))[:1200])
                    shown += 1
        for child in node.get("suites", []):
            walk(child, (trail + " > " + child.get("title", "")).strip(" >"))

    for suite in data.get("suites", []):
        walk(suite, "")
    if not shown:
        emit("playwright", "json reporter shows no failing test")


def evidence_files() -> None:
    for path in sorted((ROOT / "test-results").rglob("*.md"))[:4]:
        body = path.read_text(encoding="utf-8", errors="replace")
        emit("evidence:" + path.name, body[:1500])


def mjs_gate() -> None:
    try:
        proc = subprocess.run(["node", "scripts/check_publication_browser.mjs"], cwd=ROOT,
                              capture_output=True, text=True, timeout=420)
    except Exception as exc:  # noqa: BLE001 - diagnostics must never mask the real failure
        emit("mjs", f"could not re-run the gate: {exc}")
        return
    text = (proc.stdout + "\n" + proc.stderr).strip()
    tail = [l for l in text.splitlines() if l.strip()][-25:]
    emit("mjs:exit=" + str(proc.returncode), "\n".join(tail)[:1800])


if __name__ == "__main__":
    try:
        playwright_json()
        evidence_files()
        mjs_gate()
    except Exception as exc:  # noqa: BLE001
        emit("diagnostics", f"diagnostics itself failed: {exc}")
    sys.exit(0)
