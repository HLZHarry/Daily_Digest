"""Fetch top Hacker News stories matching AI/ML keywords."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import httpx

from .rss import Item

log = logging.getLogger(__name__)

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "anthropic", "openai", "gemini",
    "model", "neural", "transformer", "agent", "rag", "embedding",
    "machine learning", "ml", "deep learning",
]

MIN_POINTS = 100
MAX_STORIES_TO_SCAN = 80


def fetch_hackernews(source: dict, lookback_hours: int) -> list[Item]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    items: list[Item] = []

    with httpx.Client(timeout=10.0) as client:
        try:
            top_ids = client.get(HN_TOP_URL).json()[:MAX_STORIES_TO_SCAN]
        except Exception as e:
            log.warning("HN top fetch failed: %s", e)
            return items

        for sid in top_ids:
            try:
                story = client.get(HN_ITEM_URL.format(id=sid)).json()
            except Exception:
                continue
            if not story or story.get("type") != "story":
                continue
            if story.get("score", 0) < MIN_POINTS:
                continue
            published = datetime.fromtimestamp(story.get("time", 0), tz=timezone.utc)
            if published < cutoff:
                continue
            title = story.get("title", "")
            if not _is_ai_related(title):
                continue
            items.append(Item(
                title=title.strip(),
                url=story.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                source=source["name"],
                category=source["category"],
                region=source["region"],
                weight=source["weight"],
                published=published,
                summary=f"HN: {story.get('score', 0)} points, {story.get('descendants', 0)} comments",
            ))

    log.info("  %s: %d items in window", source["name"], len(items))
    return items


def _is_ai_related(title: str) -> bool:
    lower = title.lower()
    return any(kw in lower for kw in AI_KEYWORDS)
