"""Daily synthesis: roll all summarized items up into a single bilingual digest."""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from anthropic import Anthropic

from .summarize import SummarizedItem

log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "synthesize.md"


def synthesize(items: list[SummarizedItem], client: Anthropic, today: date) -> str:
    """Return the daily digest as Markdown."""
    items_block = _format_items_for_prompt(items)
    prompt = _PROMPT_PATH.read_text(encoding="utf-8").format(
        date_iso=today.isoformat(),
        date_zh=f"{today.year}年{today.month}月{today.day}日",
        items_block=items_block,
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def _format_items_for_prompt(items: list[SummarizedItem]) -> str:
    lines = []
    for i, s in enumerate(items, 1):
        lines.append(
            f"[{i}] CATEGORY={s.item.category} REGION={s.item.region} SOURCE={s.item.source}\n"
            f"    TITLE: {s.item.title}\n"
            f"    URL: {s.item.url}\n"
            f"    EN: {s.summary_en}\n"
            f"    ZH: {s.summary_zh}\n"
        )
    return "\n".join(lines)
