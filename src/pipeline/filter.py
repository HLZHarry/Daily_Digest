"""Dedupe, score, and filter items before summarization."""
from __future__ import annotations

import logging
import re
from collections import defaultdict
from urllib.parse import urlparse

from ..fetchers import Item
from ..config import RELEVANCE_KEYWORDS, NEGATIVE_KEYWORDS, TOP_N_PER_CATEGORY

log = logging.getLogger(__name__)


def dedupe(items: list[Item]) -> list[Item]:
    """Drop duplicates by canonicalized URL, then by lowercased title."""
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    out: list[Item] = []
    for item in items:
        url_key = _canonical_url(item.url)
        title_key = re.sub(r"\W+", "", item.title.lower())[:80]
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        out.append(item)
    log.info("Dedupe: %d → %d", len(items), len(out))
    return out


def filter_negative(items: list[Item]) -> list[Item]:
    out = [i for i in items if not _matches_any(i.title, NEGATIVE_KEYWORDS)]
    log.info("Negative filter: %d → %d", len(items), len(out))
    return out


def score(item: Item) -> float:
    """Heuristic relevance score. Higher = more likely to keep."""
    s = item.weight
    title_lower = item.title.lower()
    for kw in RELEVANCE_KEYWORDS:
        if kw in title_lower:
            s += 0.3
    if item.region == "canada":
        s += 0.4  # always boost Canada-focused items
    return s


def top_n_per_category(items: list[Item]) -> list[Item]:
    """Keep top-N per category by score."""
    by_cat: dict[str, list[Item]] = defaultdict(list)
    for i in items:
        by_cat[i.category].append(i)

    kept: list[Item] = []
    for cat, lst in by_cat.items():
        n = TOP_N_PER_CATEGORY.get(cat, 5)
        ranked = sorted(lst, key=score, reverse=True)[:n]
        kept.extend(ranked)
        log.info("Category %s: kept top %d of %d", cat, len(ranked), len(lst))
    return kept


def _matches_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in keywords)


def _canonical_url(url: str) -> str:
    try:
        p = urlparse(url)
        return f"{p.netloc.lower()}{p.path.rstrip('/')}"
    except Exception:
        return url
