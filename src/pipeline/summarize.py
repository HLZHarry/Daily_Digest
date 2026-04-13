"""Per-item summarization with Claude Haiku 4.5 — fast and cheap."""
from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from anthropic import Anthropic

from ..fetchers import Item

log = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"
MAX_PARALLEL = 6

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "summarize.md"


@dataclass
class SummarizedItem:
    item: Item
    summary_en: str
    summary_zh: str


def summarize_all(items: list[Item], client: Anthropic) -> list[SummarizedItem]:
    prompt_template = _PROMPT_PATH.read_text(encoding="utf-8")
    out: list[SummarizedItem] = []
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as ex:
        futures = {ex.submit(_summarize_one, i, client, prompt_template): i for i in items}
        for fut in as_completed(futures):
            try:
                out.append(fut.result())
            except Exception as e:
                log.warning("Summary failed for '%s': %s", futures[fut].title[:60], e)
    log.info("Summarized %d/%d items", len(out), len(items))
    return out


def _summarize_one(item: Item, client: Anthropic, prompt_template: str) -> SummarizedItem:
    raw = _strip_html(item.summary)[:2000]
    prompt = prompt_template.format(
        title=item.title,
        source=item.source,
        category=item.category,
        url=item.url,
        raw=raw or "(no description provided in feed)",
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text
    en, zh = _split_bilingual(text)
    return SummarizedItem(item=item, summary_en=en, summary_zh=zh)


def _strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def _split_bilingual(text: str) -> tuple[str, str]:
    """Parse 'EN: ...\\nZH: ...' from the model output."""
    en = zh = ""
    for line in text.strip().splitlines():
        line = line.strip()
        if line.upper().startswith("EN:"):
            en = line[3:].strip()
        elif line.upper().startswith("ZH:") or line.startswith("中文:"):
            zh = line.split(":", 1)[1].strip()
    if not en:
        en = text.strip()  # fallback if model didn't follow format
    return en, zh
