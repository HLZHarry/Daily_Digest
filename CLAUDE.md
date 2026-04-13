# Claude Code instructions

This repo is a personal daily news/digest pipeline. Read this before making changes.

## Project goal
Bilingual (EN / 中文) daily AI · Tech · Finance briefing, fully automated via GitHub Actions, delivered by email and archived to `/digests/`.

## Architecture in one breath
`src/main.py` orchestrates: fetch (RSS + HN) → dedupe + filter + score → per-item summary (Haiku 4.5) → daily synthesis (Sonnet 4.6) → render HTML → send via Resend → commit markdown to `/digests/`.

## Conventions
- Python 3.12, no framework, stdlib + `anthropic`, `feedparser`, `httpx`, `markdown` only. Don't pull in heavy deps without discussion.
- Keep `src/config.py` as the single source of truth for sources and tuning knobs.
- Prompts live in `prompts/` as plain markdown, formatted with `str.format()` (not f-strings — they're loaded at runtime). When editing a prompt, also update the placeholder list in the Python file that loads it.
- Models are pinned by exact ID strings (`claude-haiku-4-5-20251001`, `claude-sonnet-4-6`). Bump deliberately, never silently.
- New tests go in `tests/`. Run with `pytest tests/`.

## Common tasks
- **Add a source**: append to `SOURCES` in `src/config.py`. If it's not RSS, add a fetcher in `src/fetchers/` and dispatch in `main.py`.
- **Tweak digest format**: edit `prompts/synthesize.md` only — don't move structure into Python.
- **Change schedule**: edit cron in `.github/workflows/digest.yml`. Note EST vs EDT — the cron is fixed UTC.

## Don't
- Don't commit `.env` or anything with API keys.
- Don't let the model invent URLs — every link in a digest must come from a fetched item's `url` field.
- Don't add dependencies that need compilation (we want a clean GitHub Actions runner).
