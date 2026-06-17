# X Archive

This directory stores public X/Twitter posts collected for ZiyOne's AI watchlist and weekly analysis.

## Structure

```text
queries.txt  # search queries used by the collector
daily/       # day-level JSONL and markdown digest
weekly/      # weekly summary and structured analysis
```

## Daily files

```text
data/x/daily/YYYY-MM-DD.jsonl
data/x/daily/YYYY-MM-DD.md
```

## Weekly files

```text
data/x/weekly/YYYY-Www.json
data/x/weekly/YYYY-Www.md
```

## Commands

```bash
python3 scripts/collect-x-daily.py
python3 scripts/summarize-x-weekly.py
```

## Rules

- Do not commit credentials, tokens, cookies, `.xurl`, private DMs, or non-public data.
- Store public tweets only.
- Prefer JSONL for raw tweet records.
- Use Markdown for human-readable summaries.
- Keep tags in English for easier aggregation.
