# X Tweets Daily Archive and Weekly Analysis Plan

**Goal:** 把 X/Twitter 推文按天归档到 ZiyOne 仓库，作为个人 AI 关注与研究的数据源；每周生成一次总结和趋势分析。

## Recommended Data Layout

```text
data/
└── x/
    ├── daily/
    │   ├── 2026-06-17.jsonl
    │   ├── 2026-06-17.md
    │   └── ...
    ├── weekly/
    │   ├── 2026-W25.md
    │   ├── 2026-W25.json
    │   └── ...
    └── README.md
```

## Daily JSONL Format

Use JSONL: one tweet per line. It is git-friendly, append-friendly, and easy to process.

```json
{"id":"...","url":"https://x.com/user/status/...","author":"@handle","created_at":"2026-06-17T10:00:00Z","text":"...","metrics":{"like_count":0,"retweet_count":0,"reply_count":0,"quote_count":0},"tags":["agent","ai-product"],"source_query":"AI Agent OR coding agent","collected_at":"2026-06-17T12:00:00+08:00"}
```

## Daily Markdown Digest

Daily markdown is for human reading.

```text
# X Archive — 2026-06-17

## High-signal Tweets

### 1. @author — topic
- URL:
- Summary:
- Why it matters:
- Tags:

## Raw Themes
- Agent economy
- Coding agents
- AI education
```

## Weekly Summary

Weekly summary should include:

1. Top themes
2. Important tweets / threads
3. Repeated signals
4. People/projects worth following
5. Product implications for claycosmos.ai / ZiyOne
6. Action items for next week

## Suggested Queries

Start with focused AI/product signals:

```text
"AI agent" OR "autonomous agent" lang:en
"coding agent" OR "AI coding" lang:en
"agent economy" OR "AI marketplace" lang:en
"AI education" OR "AI tutor" lang:en
"personal knowledge" "AI" lang:en
(from:OpenAI OR from:AnthropicAI OR from:NousResearch OR from:huggingface) lang:en
```

## Collection Options

### Option A — xurl official API

Best if X API credentials are already configured.

Requirements:

```bash
xurl auth status
xurl whoami
```

Do not store credentials in repo. Never commit `.xurl`, tokens, cookies, or passwords.

### Option B — manual/imported links

If API rate limit or auth is unavailable, save manually selected tweet URLs into:

```text
data/x/daily/YYYY-MM-DD.links.txt
```

Then enrich later.

## Privacy / Safety Rules

- Do not commit API tokens, cookies, `.xurl`, or private DMs.
- Store public tweets only unless the user explicitly asks for private personal archive handling.
- Prefer tweet URL + metadata + summary; avoid unnecessary personal data.
- Use English tags for consistency.

## Automation Plan

1. Daily collector job writes `data/x/daily/YYYY-MM-DD.jsonl`.
2. Daily digest job writes `data/x/daily/YYYY-MM-DD.md`.
3. Weekly analysis job reads the past 7 daily files and writes:
   - `data/x/weekly/YYYY-Www.md`
   - `data/x/weekly/YYYY-Www.json`
4. Commit and push changes to GitHub.

## Git Commit Convention

```bash
git add data/x docs/plans/x-archive-weekly-analysis.md
git commit -m "data: archive X tweets for YYYY-MM-DD"
git push
```
