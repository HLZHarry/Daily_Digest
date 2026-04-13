"""Fetch items from RSS/Atom feeds within the lookback window."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser

log = logging.getLogger(__name__)


@dataclass
class Item:
    title: str
    url: str
    source: str
    category: str
    region: str
    weight: float
    published: datetime
    summary: str  # raw summary/description from the feed; may be HTML


def fetch_rss(source: dict, lookback_hours: int) -> list[Item]:
    """Return items from a single RSS/Atom feed published within the window."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    items: list[Item] = []

    try:
        parsed = feedparser.parse(source["url"])
    except Exception as e:
        log.warning("Failed to parse %s: %s", source["name"], e)
        return items

    for entry in parsed.entries:
        published = _entry_datetime(entry)
        if published is None or published < cutoff:
            continue
        items.append(Item(
            title=entry.get("title", "").strip(),
            url=entry.get("link", "").strip(),
            source=source["name"],
            category=source["category"],
            region=source["region"],
            weight=source["weight"],
            published=published,
            summary=entry.get("summary", "") or entry.get("description", ""),
        ))

    log.info("  %s: %d items in window", source["name"], len(items))
    return items


def _entry_datetime(entry) -> Optional[datetime]:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        t = entry.get(key)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None
