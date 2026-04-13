# Daily Digest 📰

> Bilingual (EN / 中文) daily AI · Tech · Finance briefing — fully automated, runs on GitHub Actions, delivered to my inbox at 7am ET, archived in this repo.

Built as a personal learning tool while transitioning into an AI/ML Engineer role. The repo doubles as a portfolio piece demonstrating LLM pipeline design: multi-source ingestion, two-tier summarization (Haiku for compression, Sonnet for synthesis), prompt versioning, and LLM-as-judge evaluation.

## Architecture

```
                    ┌─────────────────────────┐
                    │  GitHub Actions (cron)  │
                    │     0 11 * * *  UTC     │
                    │     = 7 AM ET daily     │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
  ┌──────────┐            ┌──────────┐            ┌──────────┐
  │   RSS    │            │    HN    │            │ YouTube  │
  │ fetchers │            │  top AI  │            │ (phase 2)│
  └────┬─────┘            └────┬─────┘            └────┬─────┘
       └───────────────────────┼───────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │  Dedupe + Filter    │
                    │  (last 24h, score)  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │  Per-item summary   │
                    │  (Claude Haiku 4.5) │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │  Daily synthesis    │
                    │  (Claude Sonnet 4.6)│
                    │  EN + 中文 digest   │
                    └──────────┬──────────┘
                               ▼
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌───────────────┐            ┌──────────────────┐
       │  Resend API   │            │  git commit to   │
       │  → my inbox   │            │  /digests/*.md   │
       └───────────────┘            └──────────────────┘
```

## Sources (16)

**AI** · Simon Willison · Latent Space · The Batch · Anthropic · Hugging Face · Hacker News (AI filter)
**Tech** · Stratechery · Pragmatic Engineer · The Verge · TechCrunch
**Finance** · Matt Levine (Money Stuff) · Bloomberg Markets · Globe & Mail ROB · Financial Post · FT Alphaville · Yahoo Finance

Edit `src/config.py` to add/remove sources.

## Sample digest format

```markdown
# 🌅 Daily Digest — 2026-04-13 / 2026年4月13日

## ⚡ TL;DR
- [EN one-liner with 🔗 source]
- [中文一句话 + 🔗 链接]
- ...

## 🤖 AI / 人工智能
**[Anthropic ships Claude Opus 4.6](https://...)** — Anthropic
> EN: 2-sentence summary.
> 中文: 两句话的中文摘要。

## 💼 Tech / 科技
...

## 📈 Finance / 金融
...

## 🇨🇦 Canada Focus / 加拿大焦点
...

## 💡 Worth Your Time / 今日精读
**[Headline](link)** — why it's worth the full read.
```

Every item links back to the original source.

## Cost

~CAD $4–5/month (Claude API). GitHub Actions and Resend free tiers cover the rest.

| Component | Daily tokens | Daily cost USD |
|---|---|---|
| Per-item summary (Haiku 4.5) | ~70 items × 950 tok | ~$0.05 |
| Daily synthesis (Sonnet 4.6, bilingual) | ~18k tok | ~$0.10 |
| **Total** | | **~$0.15** |

## Setup

```bash
# 1. Clone & install
git clone https://github.com/HLZHarry/daily-digest.git
cd daily-digest
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Local config
cp .env.example .env
# fill in: ANTHROPIC_API_KEY, RESEND_API_KEY, RECIPIENT_EMAIL, SENDER_EMAIL

# 3. Run locally to test
python -m src.main --dry-run     # fetches + summarizes, no email sent
python -m src.main                # full pipeline

# 4. Deploy
# Push to GitHub. Add the three secrets in repo Settings → Secrets and variables → Actions.
# The workflow at .github/workflows/digest.yml runs daily at 11:00 UTC.
```

## Repo layout

```
daily-digest/
├── src/
│   ├── config.py              # source list — edit to customize
│   ├── main.py                # pipeline entry point
│   ├── fetchers/              # RSS, Hacker News
│   ├── pipeline/              # dedupe, score, summarize, synthesize
│   └── render/                # HTML email + markdown archive
├── prompts/                   # versioned prompts (reviewable)
├── digests/                   # auto-committed daily archive
├── evals/                     # LLM-as-judge quality checks
└── .github/workflows/         # daily cron + weekly evals
```

## Roadmap

- [x] **M1** — MVP: 5 RSS feeds → Haiku summaries → plain email, runs locally
- [ ] **M2** — Sonnet bilingual synthesis, HTML email, all 16 sources
- [ ] **M3** — GitHub Actions deploy, secrets, auto-commit digests
- [ ] **M4** — LLM-as-judge evals, cost dashboard, architecture polish

## Why this exists

Starting an AI/ML Engineer role at OMERS AI Labs and want a forcing function to keep up with the field — across AI, the broader tech industry, and the Canadian/US capital markets. Reading raw feeds doesn't scale; this does.

## License

MIT
