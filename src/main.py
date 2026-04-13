"""Daily digest pipeline entry point.

Run modes:
  python -m src.main             # full pipeline: fetch → summarize → synthesize → email → commit
  python -m src.main --dry-run   # everything except email send
  python -m src.main --no-write  # don't write digest file (for local experimentation)
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date
from pathlib import Path

from anthropic import Anthropic

from .config import SOURCES, LOOKBACK_HOURS
from .fetchers import fetch_rss, fetch_hackernews
from .pipeline import dedupe, filter_negative, top_n_per_category, summarize_all, synthesize
from .render import to_html
from .send import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("digest")

DIGEST_DIR = Path(__file__).parent.parent / "digests"
REPO_URL = os.environ.get("REPO_URL", "https://github.com/HLZHarry/daily-digest")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip sending email")
    parser.add_argument("--no-write", action="store_true",
                        help="Don't write digest markdown file")
    args = parser.parse_args()

    today = date.today()
    log.info("=== Daily Digest pipeline for %s ===", today.isoformat())

    # 1. Fetch
    log.info("Fetching from %d sources (lookback=%dh)...", len(SOURCES), LOOKBACK_HOURS)
    raw: list = []
    for src in SOURCES:
        if src["url"] == "hackernews":
            raw.extend(fetch_hackernews(src, LOOKBACK_HOURS))
        else:
            raw.extend(fetch_rss(src, LOOKBACK_HOURS))
    log.info("Fetched %d total items", len(raw))

    if not raw:
        log.warning("No items fetched. Exiting without sending.")
        return 0

    # 2. Dedupe + filter
    items = filter_negative(dedupe(raw))
    items = top_n_per_category(items)
    log.info("After filtering: %d items going to summarization", len(items))

    # 3. Summarize per-item
    client = Anthropic()
    summarized = summarize_all(items, client)
    summarized = [s for s in summarized
                  if s.summary_en.strip().upper() != "SKIP"]
    log.info("After SKIP filter: %d items", len(summarized))

    # 4. Synthesize
    digest_md = synthesize(summarized, client, today)
    log.info("Digest generated: %d chars", len(digest_md))

    # 5. Write archive
    if not args.no_write:
        DIGEST_DIR.mkdir(exist_ok=True)
        out_path = DIGEST_DIR / f"{today.isoformat()}.md"
        out_path.write_text(digest_md, encoding="utf-8")
        log.info("Wrote %s", out_path)

    # 6. Send email
    if args.dry_run:
        log.info("--dry-run set; skipping email send")
        print("\n" + "=" * 60 + "\nDIGEST PREVIEW\n" + "=" * 60)
        print(digest_md)
        return 0

    html = to_html(digest_md, repo_url=REPO_URL)
    subject = f"🌅 Daily Digest — {today.isoformat()}"
    send_email(subject, html)
    log.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
