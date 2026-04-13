"""
Source configuration. Edit this file to add, remove, or recategorize feeds.

Each source is a dict with:
  - name: display name shown in digest
  - url:  RSS/Atom feed URL (or 'hackernews' for the HN fetcher)
  - category: one of {ai, tech, finance}
  - region: one of {global, us, canada}
  - weight: float 0.5–2.0, used to bias relevance scoring (higher = more likely to keep)
"""

SOURCES = [
    # ─── AI ─────────────────────────────────────────────────────────────────
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/",
     "category": "ai", "region": "global", "weight": 1.5},
    {"name": "Latent Space", "url": "https://www.latent.space/feed",
     "category": "ai", "region": "us", "weight": 1.3},
    {"name": "The Batch", "url": "https://www.deeplearning.ai/the-batch/feed/",
     "category": "ai", "region": "global", "weight": 1.2},
    {"name": "Anthropic", "url": "https://www.anthropic.com/news/rss.xml",
     "category": "ai", "region": "us", "weight": 1.5},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml",
     "category": "ai", "region": "global", "weight": 1.0},
    {"name": "Hacker News (AI)", "url": "hackernews",
     "category": "ai", "region": "global", "weight": 1.0},

    # ─── Tech ───────────────────────────────────────────────────────────────
    {"name": "Stratechery", "url": "https://stratechery.com/feed/",
     "category": "tech", "region": "global", "weight": 1.4},
    {"name": "Pragmatic Engineer", "url": "https://newsletter.pragmaticengineer.com/feed",
     "category": "tech", "region": "global", "weight": 1.2},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml",
     "category": "tech", "region": "us", "weight": 0.9},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/",
     "category": "tech", "region": "us", "weight": 0.9},

    # ─── Finance ────────────────────────────────────────────────────────────
    {"name": "Matt Levine — Money Stuff", "url": "https://www.bloomberg.com/opinion/authors/ARbTQlRLRjE/matthew-s-levine.rss",
     "category": "finance", "region": "us", "weight": 1.5},
    {"name": "Bloomberg Markets", "url": "https://feeds.bloomberg.com/markets/news.rss",
     "category": "finance", "region": "global", "weight": 1.0},
    {"name": "Globe & Mail — ROB", "url": "https://www.theglobeandmail.com/business/?service=rss",
     "category": "finance", "region": "canada", "weight": 1.4},
    {"name": "Financial Post", "url": "https://financialpost.com/feed",
     "category": "finance", "region": "canada", "weight": 1.3},
    {"name": "FT Alphaville", "url": "https://www.ft.com/alphaville?format=rss",
     "category": "finance", "region": "global", "weight": 1.1},
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex",
     "category": "finance", "region": "us", "weight": 1.0},
]

# How many items per category to keep after filtering, before sending to synthesis.
TOP_N_PER_CATEGORY = {"ai": 8, "tech": 5, "finance": 7}

# Look-back window in hours.
LOOKBACK_HOURS = 26  # 26 not 24, to absorb timezone slop and weekend gaps

# Relevance keywords to upweight during scoring (case-insensitive).
RELEVANCE_KEYWORDS = [
    # AI
    "llm", "claude", "gpt", "anthropic", "openai", "agent", "rag", "fine-tun",
    "transformer", "embedding", "inference", "evaluation", "benchmark",
    # Markets / finance
    "fed", "rate cut", "inflation", "earnings", "ipo", "etf", "factor",
    "portfolio", "pension", "boc", "tsx", "alternatives", "private credit",
    # Canada
    "canada", "ontario", "toronto", "boc", "cpp", "omers",
]

# Drop items whose titles match these (case-insensitive) — kills clickbait/sports/celeb.
NEGATIVE_KEYWORDS = [
    "horoscope", "celebrity", "kardashian", "nba", "nfl playoff",
]
