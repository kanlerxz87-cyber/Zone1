#!/usr/bin/env python3
"""Append one authorized, aggregate-only report row to the campaign ledger.

The tool does not fetch Associates Central, parse Amazon Program Content, or verify that a
report is genuine. Run it only after obtaining a first-party report through an authorized
account. It writes the requested aggregate fields and never stores order IDs or the source
report file. The repository's ledger remains empty until this explicit import is run.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "campaign-ledger.json"
REQUIRED = {
    "timestamp_utc",
    "source_report",
    "channel",
    "date_range",
    "eligible_sessions",
    "clicks",
    "reported_orders",
}


def normalize_row(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict) or set(row) != REQUIRED:
        raise ValueError("row must contain exactly the campaign-ledger fields")
    stamp = row["timestamp_utc"]
    if not isinstance(stamp, str):
        raise ValueError("timestamp_utc must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp_utc must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("timestamp_utc must carry a UTC timezone")

    source = row["source_report"]
    channel = row["channel"]
    if not isinstance(source, str) or not source.strip() or len(source.strip()) > 120:
        raise ValueError("source_report must identify the authorized aggregate report")
    if not isinstance(channel, str) or not channel.strip() or len(channel.strip()) > 80:
        raise ValueError("channel must be the reported channel or tracking-ID label")
    if any(token in (source + channel).lower() for token in ("http://", "https://", "@")):
        raise ValueError("URLs and email addresses are not permitted in source/channel")

    date_range = row["date_range"]
    if not isinstance(date_range, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}", date_range):
        raise ValueError("date_range must use YYYY-MM-DD/YYYY-MM-DD")
    try:
        start, end = (date.fromisoformat(part) for part in date_range.split("/"))
    except ValueError as exc:
        raise ValueError("date_range must contain valid calendar dates") from exc
    if end < start:
        raise ValueError("date_range end must not precede its start")

    normalized: dict[str, Any] = {
        "timestamp_utc": parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_report": source.strip(),
        "channel": channel.strip(),
        "date_range": date_range,
    }
    for field in ("eligible_sessions", "clicks", "reported_orders"):
        value = row[field]
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            raise ValueError(f"{field} must be null or a non-negative integer copied from the report")
        normalized[field] = value
    if all(normalized[field] is None for field in ("eligible_sessions", "clicks", "reported_orders")):
        raise ValueError("at least one metric must actually be reported")
    return normalized


def append_report_row(row: Any, ledger_path: str | Path = DEFAULT_LEDGER) -> bool:
    """Append a validated row atomically; return False for an already-imported row."""
    normalized = normalize_row(row)
    path = Path(ledger_path)
    # Lock around read/compare/write, not just the final rename. Two authorized
    # imports must not overwrite each other. No raw report or customer data is kept.
    with path.with_suffix(path.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(ledger, dict) or not isinstance(ledger.get("rows"), list):
            raise ValueError("campaign ledger has an invalid schema")
        key = ("timestamp_utc", "source_report", "channel", "date_range")
        for existing in ledger["rows"]:
            if all(existing.get(field) == normalized[field] for field in key):
                if existing != normalized:
                    raise ValueError("conflicting metrics for an already-imported report; review provenance")
                return False
        ledger["rows"].append(normalized)
        temp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".ledger-", delete=False, encoding="utf-8") as out:
                temp = Path(out.name)
                out.write(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
                out.flush()
                os.fsync(out.fileno())
            os.replace(temp, path)
        finally:
            if temp and temp.exists():
                temp.unlink()
        return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_row_json", type=Path, help="one JSON aggregate row copied from an authorized first-party report")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER, help="campaign ledger path (default: data/campaign-ledger.json)")
    parser.add_argument("--authorized", action="store_true", help="confirm that this is an authorized first-party aggregate, not estimated data")
    args = parser.parse_args(argv)
    if not args.authorized:
        parser.error("--authorized is required; never import estimates or test fixtures into the real ledger")
    try:
        row = json.loads(args.report_row_json.read_text(encoding="utf-8"))
        added = append_report_row(row, args.ledger)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"report import refused: {exc}", file=sys.stderr)
        return 2
    print("aggregate row added" if added else "duplicate aggregate row; ledger unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
