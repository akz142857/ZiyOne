# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

ZiyOne is a personal homepage repo (GitHub: `akz142857/ZiyOne`, deployed via GitHub Pages at `https://akz142857.github.io/ZiyOne/`). It is **two unrelated things living side by side**:

1. **An Astro site** — the personal homepage, built with **Astro + Bun**. Content is data-driven (TS modules under `src/data/`), pages under `src/pages/`. Standalone static works (e.g. the picture book) live in `public/works/` and are served verbatim.
2. **An X/Twitter archive pipeline** — Python scripts under `scripts/` that collect public tweets into `data/x/` for a personal AI watchlist and weekly trend analysis. Independent of the site; shares no code.

`docs/plans/` holds plans (the homepage rebuild — now done as Astro, not the Vue variant the plan originally proposed; plus a world-model learning roadmap that is **not yet implemented**). Treat plans as intent, not current state — verify against actual files.

### Critical: base path

The site deploys under `/ZiyOne` (GitHub Pages project page). `base: '/ZiyOne'` is set in `astro.config.mjs` and **must stay in sync with the repo name** or production assets 404. Every internal link/asset must be prefixed — use `withBase()` from `src/lib/url.ts` (it leaves `http`/`mailto`/`#` URLs untouched). Do not hardcode `/ZiyOne/...`.

## Commands

```bash
# Astro site
bun install
bun run dev          # dev server at http://localhost:4321/ZiyOne
bun run build        # static output to dist/
bun run preview      # serve the built dist/
bun run check        # astro check (type safety) — run before commits

# X archive pipeline
python3 scripts/collect-x-daily.py                              # collect today (Asia/Shanghai)
python3 scripts/collect-x-daily.py --date 2026-06-17 --limit-per-query 10
python3 scripts/summarize-x-weekly.py                           # current ISO week
python3 scripts/summarize-x-weekly.py --year 2026 --week 25
```

Scripts use only the Python standard library — no `pip install` needed.

## X archive architecture

The pipeline is two stages, daily then weekly, both deterministic:

- **`collect-x-daily.py`** reads queries from `data/x/queries.txt` (one per line, `#` comments ignored) and fetches tweets via the **`xurl` CLI**, which must already be authenticated by the user. The script *deliberately* never reads `~/.xurl`, never accepts inline secrets, and degrades gracefully when `xurl` is missing or unauthenticated (`xurl_ready()`), still writing output files. As a fallback it picks up manual public URLs from `data/x/daily/YYYY-MM-DD.links.txt`. Output: `data/x/daily/YYYY-MM-DD.jsonl` (one record per line, the source of truth) + `.md` (human digest). Tags are inferred from text via `DEFAULT_TAG_RULES`; tweets are ranked by `metric_score` (likes + 2×retweets + 2×quotes + replies).
- **`summarize-x-weekly.py`** reads all daily JSONL for an ISO week, aggregates tags/authors/queries, and writes `data/x/weekly/YYYY-Www.json` + `.md`. The Markdown is a scaffold with empty "Product Implications" / "Next Actions" sections meant to be filled in later by a human or LLM.

Both scripts share an inlined `metric_score` and an Asia/Shanghai timezone helper (UTC+8, no DST, no external tz deps). JSONL is the canonical data format; Markdown is for reading.

### Data rules (from `data/x/README.md`)

- **Public tweets only.** Never commit credentials, tokens, cookies, `.xurl`, private DMs, or non-public data.
- Prefer JSONL for raw records, Markdown for summaries.
- Keep tags in English for easy aggregation.

## Site conventions

- **Content is data, not markup.** Add/edit works, research directions, learning tracks, watchlist items by editing `src/data/*.ts` (each is typed). Pages map over that data. The homepage (`src/pages/index.astro`) renders Featured Works / Learning / Research / Watchlist / Now from these modules.
- **Design tokens** live in `src/styles/tokens.css` (palette, fluid type scale, spacing, motion). Never hardcode palette/spacing repeatedly — reference the CSS custom properties. Style direction: "AI-native personal lab" — editorial + technical, clean but warm, single accent.
- Component-scoped styles go in each `.astro` file's `<style>` block; only truly global rules belong in `src/styles/global.css`.
- **Static HTML works** (e.g. `public/works/english-picture-book/index.html`) are self-contained single files with inlined CSS tokens, served verbatim from `public/`. They are NOT part of the Astro build — keep them dependency-free and standalone. Put new static works under `public/works/`.
- Bilingual: Chinese (`lang="zh-CN"`) primary, English for identity/project titles.
- `bun run check` is clean (0 errors) — keep it that way.

## Deployment

`.github/workflows/deploy.yml` builds with Bun and publishes `dist/` to GitHub Pages on push to `main`. Requires GitHub Pages source set to "GitHub Actions" in repo settings (one-time, in the GitHub UI).
