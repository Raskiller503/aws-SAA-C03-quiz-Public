#!/usr/bin/env python3
"""
Translate the English `comments` of every question in questions.json into
Chinese, writing them to a new sibling field `comments_cn` (same length and
order as `comments`).

Design choices:
- Idempotent / resumable: skips questions where `comments_cn` already covers
  all `comments`. Safe to Ctrl-C and re-run.
- Incremental save: dumps progress to questions.json every CHECKPOINT_EVERY
  questions so a crash never loses more than a handful of translations.
- Batched per question: all of a question's comment segments are sent in
  one API call to preserve cross-segment context.
- Concurrency: N workers in parallel for throughput.

Usage:
    OPENAI_API_KEY=sk-...  python3 translate_comments.py
    # or
    OPENAI_API_KEY=sk-...  python3 translate_comments.py --workers 8 --model gpt-4o-mini

The defaults match the quiz-app's AI assistant (jp.api.openai.com / gpt-5.4),
but you can override with --base-url and --model.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).parent
QUESTIONS_PATH = ROOT / "questions.json"
QUESTIONS_JS = ROOT / "questions.js"

DEFAULT_BASE_URL = "https://jp.api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"  # cheap + good enough for translation
CHECKPOINT_EVERY = 25


SYSTEM_PROMPT = (
    "你是 AWS 认证考试题库的中文翻译助手。我会给你若干段关于一道 SAA-C03 题目"
    "的英文解题分析(每段是一条独立的解析片段)。请把每一段都翻译成自然、专业、"
    "简洁的中文 — 保留 AWS 服务名(EC2、S3、Lambda 等)和缩写(IAM、VPC、KMS 等)"
    "不译,保留 Markdown 链接,保留代码块。\n\n"
    "严格要求:\n"
    "1. 输出必须是 JSON 数组,顺序与输入完全一致,长度完全一致。\n"
    "2. 不要解释,不要添加额外字段,不要输出 ```json 包裹。\n"
    "3. 直接输出 JSON 数组本身,例如 [\"译文1\", \"译文2\"]。"
)


def call_openai(api_key: str, base_url: str, model: str, segments: list[str], timeout: int = 60) -> list[str]:
    """Translate a list of English segments to Chinese. Returns same-length list."""
    user_msg = "请翻译下面这 {n} 段(以 JSON 数组形式输入):\n\n{arr}".format(
        n=len(segments),
        arr=json.dumps(segments, ensure_ascii=False),
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    # Some endpoints reject response_format on older models; fall back if needed
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        # Retry without response_format if the model doesn't support it
        if "response_format" in msg or e.code == 400:
            payload.pop("response_format", None)
            req2 = request.Request(
                f"{base_url.rstrip('/')}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )
            with request.urlopen(req2, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8"))
        else:
            raise RuntimeError(f"HTTP {e.code}: {msg[:300]}") from e

    content = data["choices"][0]["message"]["content"].strip()

    # The model may either return a JSON array directly, or a JSON object
    # with one key holding the array. Handle both.
    parsed = json.loads(content)
    if isinstance(parsed, list):
        arr = parsed
    elif isinstance(parsed, dict):
        # Find the first list value
        arr = next((v for v in parsed.values() if isinstance(v, list)), None)
        if arr is None:
            raise ValueError(f"Expected list in response, got: {content[:200]}")
    else:
        raise ValueError(f"Unexpected response type: {type(parsed)}")

    if len(arr) != len(segments):
        # Best-effort: pad / truncate
        if len(arr) < len(segments):
            arr = arr + [""] * (len(segments) - len(arr))
        else:
            arr = arr[: len(segments)]

    return [str(x) for x in arr]


def needs_translation(q: dict) -> bool:
    """True if this question still has untranslated comments."""
    comments = q.get("comments") or []
    if not comments:
        return False
    existing = q.get("comments_cn") or []
    if len(existing) != len(comments):
        return True
    # If any slot is empty/None, we still need to translate
    return any(not s for s in existing)


def translate_one(q: dict, api_key: str, base_url: str, model: str, max_retries: int = 3):
    """Translate a single question's comments; mutates q in place."""
    comments = q["comments"]
    last_err = None
    for attempt in range(max_retries):
        try:
            cn = call_openai(api_key, base_url, model, comments)
            q["comments_cn"] = cn
            return q["id"], True, None
        except Exception as e:
            last_err = e
            time.sleep(1.5 ** attempt)
    return q["id"], False, str(last_err)


def save(questions: list, path: Path):
    """Atomic write."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def rebuild_js(questions: list):
    """Mirror parse_questions.py — keep questions.js in sync."""
    js = "// Auto-generated from questions.json\nvar QUESTIONS_DATA = " + json.dumps(
        questions, ensure_ascii=False, separators=(",", ": ")
    ) + ";\n"
    QUESTIONS_JS.write_text(js, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--limit", type=int, default=0, help="Only translate N questions (0 = all)")
    args = ap.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: set OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    pending = [q for q in questions if needs_translation(q)]
    if args.limit:
        pending = pending[: args.limit]

    total = len(pending)
    print(f"Loaded {len(questions)} questions; {total} still need translation.")
    if total == 0:
        print("Nothing to do.")
        return

    print(f"Model: {args.model}  Base URL: {args.base_url}  Workers: {args.workers}")

    done = 0
    fail = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(translate_one, q, api_key, args.base_url, args.model): q for q in pending}
        for fut in as_completed(futures):
            qid, ok, err = fut.result()
            if ok:
                done += 1
            else:
                fail += 1
                print(f"  ✗ Q{qid} failed: {err}")

            if (done + fail) % 10 == 0 or (done + fail) == total:
                elapsed = time.time() - start
                rate = (done + fail) / max(1, elapsed)
                eta = (total - done - fail) / max(rate, 0.001)
                print(f"  progress: {done + fail}/{total} (ok={done} fail={fail}) "
                      f"~{rate:.1f} q/s  ETA {eta:.0f}s")

            if (done + fail) % CHECKPOINT_EVERY == 0:
                save(questions, QUESTIONS_PATH)

    save(questions, QUESTIONS_PATH)
    rebuild_js(questions)
    print(f"\nDone. ok={done} fail={fail}  total time={time.time() - start:.1f}s")
    print(f"Wrote {QUESTIONS_PATH}")
    print(f"Wrote {QUESTIONS_JS}")


if __name__ == "__main__":
    main()
