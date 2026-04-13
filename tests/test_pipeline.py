"""Quick smoke tests — run with `pytest tests/`."""
from datetime import datetime, timezone

from src.fetchers import Item
from src.pipeline.filter import dedupe, filter_negative, score, top_n_per_category


def _mk(title, source="X", category="ai", region="global", weight=1.0, url=None):
    return Item(
        title=title, url=url or f"https://example.com/{title.replace(' ', '-')}",
        source=source, category=category, region=region, weight=weight,
        published=datetime.now(timezone.utc), summary="",
    )


def test_dedupe_by_url():
    a = _mk("A", url="https://example.com/a")
    b = _mk("A different title", url="https://example.com/a")  # same URL
    assert len(dedupe([a, b])) == 1


def test_filter_negative():
    items = [_mk("Daily Horoscope"), _mk("Anthropic ships Opus 4.6")]
    out = filter_negative(items)
    assert len(out) == 1
    assert "Opus" in out[0].title


def test_score_boosts_canada():
    base = _mk("Generic AI news", region="global", weight=1.0)
    canada = _mk("Generic AI news", region="canada", weight=1.0)
    assert score(canada) > score(base)


def test_top_n_per_category():
    items = [_mk(f"AI item {i}", category="ai") for i in range(20)]
    items += [_mk(f"Finance item {i}", category="finance") for i in range(20)]
    kept = top_n_per_category(items)
    by_cat = {}
    for i in kept:
        by_cat[i.category] = by_cat.get(i.category, 0) + 1
    assert by_cat["ai"] == 8
    assert by_cat["finance"] == 7
