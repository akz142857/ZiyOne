#!/usr/bin/env python3
"""Generate a weekly X archive summary from daily JSONL files.

This is a deterministic summarizer. It creates a useful scaffold from stored
records; an LLM/agent can later rewrite the Markdown with deeper analysis.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "x"
DAILY_DIR = DATA_DIR / "daily"
WEEKLY_DIR = DATA_DIR / "weekly"


def current_iso_week_shanghai() -> tuple[int, int]:
    day = dt.datetime.now(dt.UTC).astimezone(dt.timezone(dt.timedelta(hours=8))).date()
    year, week, _ = day.isocalendar()
    return year, week


def dates_for_iso_week(year: int, week: int) -> list[str]:
    monday = dt.date.fromisocalendar(year, week, 1)
    return [(monday + dt.timedelta(days=i)).isoformat() for i in range(7)]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"type": "parse_error", "path": str(path), "line": line[:200]})
    return out


def metric_score(record: dict[str, Any]) -> int:
    m = record.get("metrics") or {}
    if not isinstance(m, dict):
        return 0
    return int(m.get("like_count", 0) or 0) + 2 * int(m.get("retweet_count", 0) or 0) + 2 * int(m.get("quote_count", 0) or 0) + int(m.get("reply_count", 0) or 0)


def main() -> int:
    default_year, default_week = current_iso_week_shanghai()
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=default_year)
    parser.add_argument("--week", type=int, default=default_week)
    args = parser.parse_args()

    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    week_id = f"{args.year}-W{args.week:02d}"
    dates = dates_for_iso_week(args.year, args.week)
    records: list[dict[str, Any]] = []
    daily_counts: dict[str, int] = {}
    for date_str in dates:
        day_records = read_jsonl(DAILY_DIR / f"{date_str}.jsonl")
        daily_counts[date_str] = len([r for r in day_records if r.get("id")])
        records.extend(day_records)

    tweets = [r for r in records if r.get("id")]
    errors = [r for r in records if r.get("type")]

    tag_counts = collections.Counter()
    author_counts = collections.Counter()
    query_counts = collections.Counter()
    for r in tweets:
        tag_counts.update(r.get("tags", []))
        if r.get("author"):
            author_counts[r["author"]] += 1
        if r.get("source_query"):
            query_counts[r["source_query"]] += 1

    top_tweets = sorted(tweets, key=metric_score, reverse=True)[:20]

    summary_json = {
        "week": week_id,
        "dates": dates,
        "tweet_count": len(tweets),
        "daily_counts": daily_counts,
        "top_tags": tag_counts.most_common(20),
        "top_authors": author_counts.most_common(20),
        "top_queries": query_counts.most_common(20),
        "top_tweets": [
            {
                "id": r.get("id"),
                "url": r.get("url"),
                "author": r.get("author"),
                "score": metric_score(r),
                "tags": r.get("tags", []),
                "text": r.get("text", "")[:500],
            }
            for r in top_tweets
        ],
        "error_count": len(errors),
    }

    json_path = WEEKLY_DIR / f"{week_id}.json"
    md_path = WEEKLY_DIR / f"{week_id}.md"
    json_path.write_text(json.dumps(summary_json, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        f"# X Weekly Analysis — {week_id}",
        "",
        f"Date range: {dates[0]} → {dates[-1]}",
        f"Collected public tweets: {len(tweets)}",
        "",
        "## Executive Summary",
        "",
    ]
    if tweets:
        top_theme = tag_counts.most_common(1)[0][0] if tag_counts else "AI"
        lines.append(f"This week, the strongest archived signal is **{top_theme}**. Review the top tweets and themes below, then add human/LLM interpretation for strategy implications.")
    else:
        lines.append("No tweet records were collected this week. Check xurl auth or add manual links under `data/x/daily/`.")
    lines += ["", "## Daily Volume", ""]
    for date_str, count in daily_counts.items():
        lines.append(f"- {date_str}: {count}")

    lines += ["", "## Top Themes", ""]
    if tag_counts:
        for tag, count in tag_counts.most_common(20):
            lines.append(f"- {tag}: {count}")
    else:
        lines.append("- No themes available")

    lines += ["", "## Top Authors", ""]
    if author_counts:
        for author, count in author_counts.most_common(20):
            lines.append(f"- {author}: {count}")
    else:
        lines.append("- No authors available")

    lines += ["", "## High-signal Tweets", ""]
    if top_tweets:
        for i, r in enumerate(top_tweets, 1):
            text = " ".join(str(r.get("text", "")).split())
            if len(text) > 320:
                text = text[:317] + "..."
            lines += [
                f"### {i}. {r.get('author', '@unknown')} — score {metric_score(r)}",
                f"- URL: {r.get('url')}",
                f"- Tags: {', '.join(r.get('tags', []))}",
                f"- Text: {text}",
                "",
            ]
    else:
        lines.append("No high-signal tweets available.")

    lines += [
        "",
        "## Product Implications",
        "",
        "- claycosmos.ai:",
        "- ZiyOne personal homepage:",
        "- AI learning / English learning products:",
        "",
        "## Next Actions",
        "",
        "- [ ] Pick 3 themes worth deeper research.",
        "- [ ] Convert one signal into a ZiyOne/ClayCosmos experiment.",
        "- [ ] Update watchlist queries if the week had too much noise.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {json_path.relative_to(ROOT)}")
    print(f"wrote {md_path.relative_to(ROOT)}")
    print(f"tweet_count={len(tweets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
