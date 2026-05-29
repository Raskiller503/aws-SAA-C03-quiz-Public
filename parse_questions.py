#!/usr/bin/env python3
"""
Convert raw SAA-C03 question bank (crawled from nicetd.github.io/saa-c03-quiz)
into the same schema used by the CLF02 quiz-app, so the existing UI works
unchanged.

Source schema (per question):
    {
      "id": int,
      "type": "single" | "multiple",
      "answer": ["A", "C", ...],
      "matchScore": float,
      "en": {"stem": str, "options": [{"key": "A", "text": "..."}, ...], "explanation": str},
      "zh": {"stem": str, "options": [...], "answer": [...]}   # zh may be null
    }

Target schema (CLF02-compatible):
    {
      "id": int,
      "topic": int,             # 1..N section index (50 per section)
      "cn_question": str,
      "cn_options": {"A": "...", "B": "...", ...},
      "en_question": str,
      "en_options": {...},
      "answer": ["A", ...],
      "votes": {},              # SAA bank has no community vote data
      "comments": [str, ...]    # split from en.explanation
    }
"""

import json
import re
from pathlib import Path

SRC = Path(__file__).parent / "source" / "raw_questions.json"
OUT_JSON = Path(__file__).parent / "questions.json"
OUT_JS = Path(__file__).parent / "questions.js"

SECTION_SIZE = 50


def options_list_to_dict(opts):
    """[{"key":"A","text":"..."}, ...] -> {"A":"...", ...}"""
    if not opts:
        return {}
    return {o["key"]: o.get("text", "").strip() for o in opts if o.get("key")}


def split_explanation(text):
    """Break a long explanation into a list of paragraphs / bullet points
    so the UI can render them as separate comment blocks.

    The crawled SAA explanations rarely contain blank-line separators —
    they are mostly one long sentence stream. We insert breaks at known
    section markers (Detailed Explanation, Option X, Why ..., Reference Links)
    so the resulting bubbles are scannable rather than wall-of-text.
    """
    if not text:
        return []
    text = text.replace("\r\n", "\n").strip()

    # Insert newlines before well-known section/clause markers so the regex
    # split below has something to grab onto.
    markers = [
        r"Detailed Explanation",
        r"Correct Answer\b",
        r"Why [A-Za-z]+\s*is\s*(best|correct)",
        r"Why not\b",
        r"Reference Links?",
        r"Key Concepts?",
        r"Explanation\s*:",
        r"-\s+Option\s+[A-F]\b",
        r"\b(Option\s+[A-F])\s+(is|uses|introduces|adds|fails|provides|removes|requires)",
        r"详细解析",
        r"参考链接",
        r"为什么\s*[A-F]",
        r"-\s+选项\s+[A-F]",
    ]
    pattern = "(" + "|".join(markers) + ")"
    # Insert a newline before each marker occurrence
    text = re.sub(pattern, r"\n\1", text)

    # Now split on newlines (single or multiple)
    paragraphs = [p.strip(" -\n\t") for p in re.split(r"\n+", text)]

    out = []
    for p in paragraphs:
        if not p or len(p) < 4:
            continue
        out.append(p)

    # Dedup while preserving order, by first 60 chars
    seen = set()
    deduped = []
    for c in out:
        key = c[:60].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def convert(q):
    qid = q["id"]
    topic = (qid - 1) // SECTION_SIZE + 1

    en = q.get("en") or {}
    zh = q.get("zh") or {}

    en_question = (en.get("stem") or "").strip()
    cn_question = (zh.get("stem") or "").strip()

    en_options = options_list_to_dict(en.get("options"))
    cn_options = options_list_to_dict(zh.get("options"))

    answer = list(q.get("answer") or [])
    # Fallback to zh.answer if top-level missing
    if not answer:
        answer = list(zh.get("answer") or [])

    explanation = (en.get("explanation") or "").strip()
    comments = split_explanation(explanation)

    return {
        "id": qid,
        "topic": topic,
        "cn_question": cn_question,
        "cn_options": cn_options,
        "answer": answer,
        "votes": {},
        "en_question": en_question,
        "en_options": en_options,
        "comments": comments,
    }


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        raw = json.load(f)

    out = [convert(q) for q in raw]
    out.sort(key=lambda x: x["id"])

    # Stats
    no_cn = sum(1 for q in out if not q["cn_question"])
    no_en = sum(1 for q in out if not q["en_question"])
    no_ans = sum(1 for q in out if not q["answer"])
    no_cmt = sum(1 for q in out if not q["comments"])
    multi = sum(1 for q in out if len(q["answer"]) > 1)
    topics = sorted({q["topic"] for q in out})

    print(f"Total questions: {len(out)}")
    print(f"  - sections (topics): {len(topics)} ({topics[0]}–{topics[-1]})")
    print(f"  - multi-answer: {multi}")
    print(f"  - missing CN translation: {no_cn}")
    print(f"  - missing EN text: {no_en}")
    print(f"  - missing answer: {no_ans}")
    print(f"  - missing explanation: {no_cmt}")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {OUT_JSON}")

    # Build questions.js — same format as CLF02 (var QUESTIONS_DATA = [...])
    js = "// Auto-generated from questions.json\nvar QUESTIONS_DATA = " + json.dumps(
        out, ensure_ascii=False, separators=(",", ": ")
    ) + ";\n"
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"Wrote {OUT_JS} ({len(js):,} bytes)")


if __name__ == "__main__":
    main()
