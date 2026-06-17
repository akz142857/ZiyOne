#!/usr/bin/env python3
"""Collect public X/Twitter posts into daily JSONL + Markdown files.

This script intentionally never reads ~/.xurl and never accepts inline secrets.
It uses the xurl CLI only when it is already authenticated by the user.

Usage:
  python3 scripts/collect-x-daily.py
  python3 scripts/collect-x-daily.py --date 2026-06-17 --limit-per-query 10

Manual fallback:
  Put public tweet URLs in data/x/daily/YYYY-MM-DD.links.txt.
  The script will preserve them in the daily markdown even if xurl auth is absent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "x"
DAILY_DIR = DATA_DIR / "daily"
QUERIES_FILE = DATA_DIR / "queries.txt"

DEFAULT_TAG_RULES = {
    "agent": ["agent", "agents", "autonomous"],
    "coding-agent": ["coding agent", "code agent", "ai coding", "devin", "swe"],
    "agent-economy": ["marketplace", "commerce", "economy", "payment", "wallet", "shop"],
    "ai-education": ["education", "tutor", "learning", "learn", "school"],
    "knowledge": ["knowledge", "memory", "notes", "personal ai", "pkm"],
    "model": ["model", "llm", "gpt", "claude", "open model"],
    "inference": ["inference", "serving", "latency", "gpu", "eval"],
}


def now_shanghai() -> dt.datetime:
    # Avoid external timezone deps. China has no DST.
    return dt.datetime.now(dt.UTC).astimezone(dt.timezone(dt.timedelta(hours=8)))


def today_shanghai() -> str:
    return now_shanghai().date().isoformat()


def run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def xurl_ready() -> tuple[bool, str]:
    if not shutil.which("xurl"):
        return False, "xurl is not installed"
    status = run(["xurl", "auth", "status"], timeout=20)
    text = (status.stdout + status.stderr).strip()
    if status.returncode != 0:
        return False, text or "xurl auth status failed"
    if "No apps registered" in text or "oauth2: (none)" in text:
        return False, text or "xurl is not authenticated"
    who = run(["xurl", "whoami"], timeout=30)
    if who.returncode != 0:
        return False, (who.stdout + who.stderr).strip() or "xurl whoami failed"
    return True, "xurl authenticated"


def load_queries() -> list[str]:
    if not QUERIES_FILE.exists():
        return []
    queries = []
    for line in QUERIES_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            queries.append(line)
    return queries


def parse_xurl_search(raw: str, source_query: str, collected_at: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    data = payload.get("data", [])
    includes = payload.get("includes", {}) if isinstance(payload, dict) else {}
    users = {u.get("id"): u for u in includes.get("users", []) if isinstance(u, dict)}
    records = []
    if isinstance(data, dict):
        data = [data]
    for tweet in data or []:
        if not isinstance(tweet, dict):
            continue
        author = users.get(tweet.get("author_id"), {})
        username = author.get("username") or tweet.get("author_id") or "unknown"
        tweet_id = str(tweet.get("id", "")).strip()
        if not tweet_id:
            continue
        text = tweet.get("text", "")
        records.append({
            "id": tweet_id,
            "url": f"https://x.com/{username}/status/{tweet_id}",
            "author": f"@{username}" if not str(username).startswith("@") else str(username),
            "author_name": author.get("name"),
            "created_at": tweet.get("created_at"),
            "text": text,
            "metrics": tweet.get("public_metrics", {}),
            "tags": infer_tags(text + " " + source_query),
            "source_query": source_query,
            "collected_at": collected_at,
        })
    return records


def infer_tags(text: str) -> list[str]:
    lower = text.lower()
    tags = []
    for tag, needles in DEFAULT_TAG_RULES.items():
        if any(n in lower for n in needles):
            tags.append(tag)
    return tags or ["ai"]


def collect_from_xurl(queries: list[str], limit_per_query: int, collected_at: str) -> list[dict[str, Any]]:
    all_records: list[dict[str, Any]] = []
    for query in queries:
        cmd = ["xurl", "search", query, "-n", str(limit_per_query)]
        proc = run(cmd, timeout=90)
        if proc.returncode != 0:
            all_records.append({
                "type": "collection_error",
                "source_query": query,
                "error": (proc.stdout + proc.stderr).strip(),
                "collected_at": collected_at,
            })
            continue
        all_records.extend(parse_xurl_search(proc.stdout, query, collected_at))
    return all_records


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for record in records:
        key = record.get("id") or record.get("url") or json.dumps(record, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        out.append(record)
    return out


def load_manual_links(date_str: str) -> list[str]:
    path = DAILY_DIR / f"{date_str}.links.txt"
    if not path.exists():
        return []
    links = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            links.append(line)
    return links


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def metric_score(record: dict[str, Any]) -> int:
    m = record.get("metrics") or {}
    if not isinstance(m, dict):
        return 0
    return int(m.get("like_count", 0) or 0) + 2 * int(m.get("retweet_count", 0) or 0) + 2 * int(m.get("quote_count", 0) or 0) + int(m.get("reply_count", 0) or 0)


def write_markdown(path: Path, date_str: str, records: list[dict[str, Any]], manual_links: list[str], auth_note: str) -> None:
    tweets = [r for r in records if r.get("id")]
    errors = [r for r in records if r.get("type") == "collection_error"]
    tweets = sorted(tweets, key=metric_score, reverse=True)
    tag_counts: dict[str, int] = {}
    for r in tweets:
        for tag in r.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    lines = [f"# X Archive — {date_str}", "", f"Collected records: {len(tweets)}", f"Collector status: {auth_note}", ""]
    if tag_counts:
        lines += ["## Themes", ""]
        for tag, count in sorted(tag_counts.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- {tag}: {count}")
        lines.append("")

    lines += ["## High-signal Tweets", ""]
    if tweets:
        for i, r in enumerate(tweets[:25], 1):
            text = re.sub(r"\s+", " ", r.get("text", "")).strip()
            if len(text) > 360:
                text = text[:357] + "..."
            lines += [
                f"### {i}. {r.get('author', '@unknown')} — {', '.join(r.get('tags', []))}",
                f"- URL: {r.get('url')}",
                f"- Created: {r.get('created_at') or 'unknown'}",
                f"- Score: {metric_score(r)}",
                f"- Text: {text}",
                f"- Source query: `{r.get('source_query', '')}`",
                "",
            ]
    else:
        lines += ["No collected tweets yet.", ""]

    if manual_links:
        lines += ["## Manual Links", ""]
        for link in manual_links:
            lines.append(f"- {link}")
        lines.append("")

    if errors:
        lines += ["## Collection Errors", ""]
        for e in errors:
            lines.append(f"- `{e.get('source_query')}`: {e.get('error', '')[:300]}")
        lines.append("")

    lines += [
        "## Notes",
        "",
        "- Public tweets only. No credentials, cookies, private DMs, or non-public data are stored.",
        "- Weekly analysis reads daily JSONL and Markdown files from this directory.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=today_shanghai(), help="YYYY-MM-DD, default: today in Asia/Shanghai")
    parser.add_argument("--limit-per-query", type=int, default=10)
    args = parser.parse_args()

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    collected_at = now_shanghai().replace(microsecond=0).isoformat()
    ready, auth_note = xurl_ready()
    queries = load_queries()
    records: list[dict[str, Any]] = []
    if ready and queries:
        records = collect_from_xurl(queries, args.limit_per_query, collected_at)
    records = dedupe_records(records)
    manual_links = load_manual_links(args.date)

    jsonl_path = DAILY_DIR / f"{args.date}.jsonl"
    md_path = DAILY_DIR / f"{args.date}.md"
    write_jsonl(jsonl_path, records)
    write_markdown(md_path, args.date, records, manual_links, auth_note)

    print(f"wrote {jsonl_path.relative_to(ROOT)} records={len(records)}")
    print(f"wrote {md_path.relative_to(ROOT)}")
    if not ready:
        print(f"xurl_not_ready: {auth_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
