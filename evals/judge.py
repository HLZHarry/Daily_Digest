"""LLM-as-judge eval — scores a digest on faithfulness, relevance, and bilingual quality.

Run weekly via .github/workflows/eval.yml (M4), or ad-hoc:
    python -m evals.judge digests/2026-04-13.md

Outputs a JSON score card to evals/results/.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

JUDGE_MODEL = "claude-sonnet-4-6"

RUBRIC = """
You are evaluating a daily news digest. Score on a 1–5 integer scale for each criterion.
Return ONLY valid JSON, no preamble.

Criteria:
- faithfulness: claims appear grounded; no obvious hallucinated facts or links
- relevance: items match an AI/ML engineer in Canadian asset management — AI, tech, finance, Canada/US
- bilingual_quality: Chinese parallels English meaning; technical terms kept in English where natural
- structure: required sections present (TL;DR, AI, Tech, Finance, Canada Focus, Worth Your Time)
- signal: avoids hype, clickbait, and filler

Output JSON shape:
{"faithfulness": int, "relevance": int, "bilingual_quality": int, "structure": int, "signal": int, "notes": "<2-sentence reviewer comment>"}
"""


def judge(digest_md: str) -> dict:
    client = Anthropic()
    msg = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": f"{RUBRIC}\n\n---DIGEST---\n{digest_md}"}],
    )
    return json.loads(msg.content[0].text.strip())


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m evals.judge <path-to-digest.md>")
        return 1
    path = Path(sys.argv[1])
    result = judge(path.read_text(encoding="utf-8"))
    result["digest"] = path.name
    result["judged_at"] = datetime.utcnow().isoformat() + "Z"

    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{path.stem}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
