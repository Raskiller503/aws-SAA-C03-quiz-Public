#!/usr/bin/env python3
"""
Generate a single-file HTML study guide from the markdown chapters in
学习框架/. The output `study.html` embeds all chapter content + a marked.js
renderer, so it works by double-clicking the file (file://) and also from
a static host like GitHub Pages.

Usage:
    python3 gen_study_html.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DIR = ROOT / "学习框架"
OUT = ROOT / "study.html"

# Chapter ordering: filenames begin with 00-, 01-, ... 12-
def chapter_sort_key(p: Path):
    m = re.match(r"(\d+)", p.stem)
    return int(m.group(1)) if m else 999


def title_from_filename(p: Path) -> str:
    # "01-架构师的全局视图.md" -> "01 · 架构师的全局视图"
    stem = p.stem
    m = re.match(r"(\d+)-(.+)", stem)
    if m:
        return f"{m.group(1)} · {m.group(2)}"
    return stem


def main():
    chapters = []
    for md in sorted(SRC_DIR.glob("*.md"), key=chapter_sort_key):
        content = md.read_text(encoding="utf-8")
        chapters.append({
            "id": md.stem,
            "title": title_from_filename(md),
            "filename": md.name,
            "content": content,
        })

    print(f"Found {len(chapters)} chapters:")
    for c in chapters:
        print(f"  - {c['title']}  ({len(c['content']):,} chars)")

    chapters_json = json.dumps(chapters, ensure_ascii=False)

    html = HTML_TEMPLATE.replace("__CHAPTERS_JSON__", chapters_json)
    OUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUT}  ({len(html):,} bytes)")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AWS SAA-C03 学习框架</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
<style>
:root {
  --aws-orange: #FF9900;
  --aws-dark: #232F3E;
  --bg: #f5f7fa;
  --side-bg: #ffffff;
  --card-bg: #ffffff;
  --text: #1a1a2e;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
  --link: #2563eb;
  --code-bg: #1e293b;
  --table-stripe: #f9fafb;
  --table-head: #f3f4f6;
}
.dark {
  --bg: #0f172a;
  --side-bg: #1e293b;
  --card-bg: #1e293b;
  --text: #e2e8f0;
  --text-secondary: #94a3b8;
  --border: #334155;
  --link: #60a5fa;
  --code-bg: #0f172a;
  --table-stripe: #1a2235;
  --table-head: #283549;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
               'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  display: flex;
  min-height: 100vh;
}
header.topbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 56px;
  background: var(--aws-dark);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 50;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
header.topbar h1 {
  font-size: 16px;
  font-weight: 700;
}
header.topbar h1 span { color: var(--aws-orange); }
header .spacer { flex: 1; }
header .topbtn {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  margin-left: 8px;
}
header .topbtn:hover { background: rgba(255,255,255,0.15); }
header .quizlink {
  background: var(--aws-orange);
  color: var(--aws-dark);
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 13px;
  margin-left: 8px;
}
header .quizlink:hover { background: #ffb84d; }

.menu-toggle {
  display: none;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  padding: 6px 10px;
  margin-right: 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
}

aside.toc {
  width: 280px;
  background: var(--side-bg);
  border-right: 1px solid var(--border);
  padding: 76px 16px 24px;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  overflow-y: auto;
  transition: transform 0.25s ease;
}
aside.toc h2 {
  font-size: 13px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
  padding: 0 8px;
}
aside.toc ul { list-style: none; }
aside.toc li a {
  display: block;
  padding: 10px 12px;
  color: var(--text);
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 2px;
}
aside.toc li a:hover { background: var(--bg); }
aside.toc li a.active {
  background: var(--aws-orange);
  color: var(--aws-dark);
  font-weight: 600;
}

main.content {
  margin-left: 280px;
  padding: 88px 48px 64px;
  flex: 1;
  max-width: 100%;
  min-width: 0;
}
.content-inner {
  max-width: 880px;
  margin: 0 auto;
}

/* Markdown rendering */
.content-inner h1 {
  font-size: 30px;
  font-weight: 800;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--aws-orange);
}
.content-inner h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 32px 0 14px;
  padding-left: 12px;
  border-left: 4px solid var(--aws-orange);
}
.content-inner h3 { font-size: 18px; font-weight: 700; margin: 24px 0 10px; }
.content-inner h4 { font-size: 16px; font-weight: 600; margin: 18px 0 8px; }
.content-inner p { margin-bottom: 12px; }
.content-inner a { color: var(--link); text-decoration: none; }
.content-inner a:hover { text-decoration: underline; }
.content-inner ul, .content-inner ol { margin: 8px 0 16px 24px; }
.content-inner li { margin-bottom: 4px; }
.content-inner blockquote {
  border-left: 4px solid var(--aws-orange);
  background: var(--table-stripe);
  padding: 10px 16px;
  margin: 16px 0;
  color: var(--text-secondary);
  border-radius: 4px;
}
.content-inner blockquote p:last-child { margin-bottom: 0; }
.content-inner code {
  background: var(--table-head);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 0.9em;
}
.content-inner pre {
  background: var(--code-bg);
  color: #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 14px 0 18px;
  font-size: 13px;
  line-height: 1.5;
}
.content-inner pre code {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: inherit;
}
.content-inner table {
  border-collapse: collapse;
  margin: 14px 0;
  width: 100%;
  font-size: 14px;
  background: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
}
.content-inner th, .content-inner td {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
  vertical-align: top;
}
.content-inner th { background: var(--table-head); font-weight: 600; }
.content-inner tbody tr:nth-child(even) { background: var(--table-stripe); }
.content-inner hr { border: 0; border-top: 1px solid var(--border); margin: 24px 0; }
.content-inner input[type="checkbox"] { margin-right: 6px; }
.content-inner strong { color: var(--text); font-weight: 700; }

/* Prev/Next nav */
.chapter-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  gap: 12px;
}
.chapter-nav a {
  flex: 1;
  background: var(--card-bg);
  border: 1px solid var(--border);
  padding: 14px 18px;
  border-radius: 10px;
  color: var(--text);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}
.chapter-nav a:hover {
  border-color: var(--aws-orange);
  transform: translateY(-2px);
}
.chapter-nav a span.dir {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.chapter-nav a.next { text-align: right; }
.chapter-nav .placeholder { flex: 1; }

@media (max-width: 900px) {
  aside.toc {
    transform: translateX(-100%);
    z-index: 60;
    box-shadow: 4px 0 20px rgba(0,0,0,0.15);
  }
  aside.toc.open { transform: translateX(0); }
  main.content { margin-left: 0; padding: 76px 20px 40px; }
  .menu-toggle { display: block; }
  .content-inner pre { font-size: 12px; }
  .content-inner table { font-size: 12px; }
}
</style>
</head>
<body>
<header class="topbar">
  <button class="menu-toggle" id="menuToggle">☰</button>
  <h1><span>AWS</span> SAA-C03 学习框架</h1>
  <div class="spacer"></div>
  <a href="quiz-app.html" class="quizlink">📝 刷题</a>
  <button class="topbtn" id="themeToggle">🌓</button>
</header>

<aside class="toc" id="toc">
  <h2>章节目录</h2>
  <ul id="tocList"></ul>
</aside>

<main class="content">
  <div class="content-inner" id="content">载入中…</div>
</main>

<script id="chapters-data" type="application/json">__CHAPTERS_JSON__</script>
<script>
const CHAPTERS = JSON.parse(document.getElementById('chapters-data').textContent);
const tocList = document.getElementById('tocList');
const content = document.getElementById('content');
const themeToggle = document.getElementById('themeToggle');
const menuToggle = document.getElementById('menuToggle');
const toc = document.getElementById('toc');

// Build TOC
CHAPTERS.forEach((ch, i) => {
  const li = document.createElement('li');
  const a = document.createElement('a');
  a.href = '#' + ch.id;
  a.textContent = ch.title;
  a.dataset.idx = i;
  li.appendChild(a);
  tocList.appendChild(li);
});

// Marked + highlight.js — preprocess to drop the leading "# Title" line so we
// don't render two H1s (the TOC already shows the title).
function renderChapter(idx) {
  const ch = CHAPTERS[idx];
  if (!ch) return;

  let md = ch.content;
  // Strip the first leading "# ..." line if any
  md = md.replace(/^\s*#[^\n]*\n?/, '');

  // Configure marked
  marked.setOptions({
    breaks: false,
    gfm: true,
    headerIds: true,
  });
  const html = marked.parse(md);

  let prevNext = '<div class="chapter-nav">';
  if (idx > 0) {
    prevNext += `<a href="#${CHAPTERS[idx-1].id}"><span class="dir">← 上一章</span>${CHAPTERS[idx-1].title}</a>`;
  } else {
    prevNext += `<span class="placeholder"></span>`;
  }
  if (idx < CHAPTERS.length - 1) {
    prevNext += `<a class="next" href="#${CHAPTERS[idx+1].id}"><span class="dir">下一章 →</span>${CHAPTERS[idx+1].title}</a>`;
  } else {
    prevNext += `<span class="placeholder"></span>`;
  }
  prevNext += '</div>';

  content.innerHTML = `<h1>${ch.title}</h1>` + html + prevNext;

  // Code highlight
  content.querySelectorAll('pre code').forEach(block => {
    try { hljs.highlightElement(block); } catch (e) {}
  });

  // Mark active
  tocList.querySelectorAll('a').forEach((a, i) => {
    a.classList.toggle('active', i === idx);
  });

  // Rewrite intra-doc links: "01-架构师...md" -> "#01-架构师..."
  content.querySelectorAll('a[href$=".md"]').forEach(a => {
    const target = decodeURIComponent(a.getAttribute('href')).replace(/\.md$/, '');
    a.setAttribute('href', '#' + target);
  });

  // Scroll to top on chapter switch
  window.scrollTo({ top: 0, behavior: 'auto' });

  // Close TOC on mobile after click
  if (window.innerWidth <= 900) toc.classList.remove('open');
}

function loadFromHash() {
  let hash = decodeURIComponent(location.hash.replace(/^#/, ''));
  if (!hash) {
    renderChapter(0);
    return;
  }
  const idx = CHAPTERS.findIndex(c => c.id === hash);
  renderChapter(idx >= 0 ? idx : 0);
}

window.addEventListener('hashchange', loadFromHash);
loadFromHash();

// Theme toggle
const savedTheme = localStorage.getItem('saa-theme');
if (savedTheme === 'dark') document.body.classList.add('dark');
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('saa-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
});

// Mobile TOC toggle
menuToggle.addEventListener('click', () => toc.classList.toggle('open'));
document.addEventListener('click', (e) => {
  if (window.innerWidth > 900) return;
  if (e.target.closest('#toc') || e.target.closest('#menuToggle')) return;
  toc.classList.remove('open');
});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
