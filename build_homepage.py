#!/usr/bin/env python3
"""Generate optimized homepage content from sidebar navigation."""

import os
import re
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(ROOT, "index.html")


def clean_title(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text.strip())
    text = re.sub(r"^\d{4,8}_?", "", text)
    text = text.replace("_", "，").replace("  ", " ")
    return text.strip() or text


def parse_sidebar(html: str):
    catalog = []
    current_year = None

    year_re = re.compile(
        r'<li class="chapter[^"]*" data-level="1\.\d+"[^>]*>\s*'
        r"<span>\s*(\d{4})\s*</span>",
        re.DOTALL,
    )
    article_re = re.compile(
        r'data-path="([^"]+\.html)"[^>]*>\s*<a href="([^"]+)">\s*'
        r"([^<]+?)\s*</a>",
        re.DOTALL,
    )

    nav_start = html.find('<ul class="summary">')
    nav_end = html.find('<li class="divider">', nav_start)
    nav = html[nav_start:nav_end]

    for block in re.split(r"(?=<li class=\"chapter)", nav):
        year_match = re.search(
            r'data-level="1\.\d+"[^>]*>\s*<span>\s*(\d{4})\s*</span>',
            block,
        )
        if year_match:
            current_year = year_match.group(1)
            catalog.append({"year": current_year, "articles": []})
            continue
        if not current_year:
            continue
        for m in article_re.finditer(block):
            path, href, raw_title = m.group(1), m.group(2), m.group(3).strip()
            if "#" in path or path.endswith("/#.html"):
                continue
            title = clean_title(raw_title)
            catalog[-1]["articles"].append({"title": title, "link": href})

    return [y for y in catalog if y["articles"]]


def build_homepage_html(catalog) -> str:
    total = sum(len(y["articles"]) for y in catalog)

    parts = [
        '<div id="anchor-navigation-ex-navbar">'
        '<i class="fa fa-navicon"></i><ul>'
        '<li><span class="title-icon"></span>'
        '<a href="#home"><b>1. </b>任正非讲话实录</a></li>'
        '<li><span class="title-icon"></span>'
        '<a href="#catalog"><b>2. </b>目录索引</a></li>'
        "</ul></div>",
        '<a href="#home" id="anchorNavigationExGoTop">'
        '<i class="fa fa-arrow-up"></i></a>',
        "<style>",
        ".home-intro{margin-bottom:2em;line-height:1.8;color:#555;}",
        ".home-stats{display:flex;flex-wrap:wrap;gap:12px;margin:1.5em 0;}",
        ".home-stat{background:#f5f7fa;border-left:4px solid #008cff;"
        "padding:10px 16px;border-radius:4px;min-width:140px;}",
        ".home-stat strong{display:block;font-size:1.4em;color:#333;}",
        ".year-section{margin:2em 0 1.5em;padding-top:1em;border-top:1px solid #eee;}",
        ".year-section:first-of-type{border-top:none;padding-top:0;}",
        ".year-title{font-size:1.5em;margin:0 0 .75em;color:#008cff;}",
        ".year-count{font-size:.85em;color:#999;font-weight:normal;margin-left:8px;}",
        ".article-list{list-style:none;padding:0;margin:0;"
        "display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:8px 20px;}",
        ".article-list li{margin:0;padding:0;}",
        ".article-list a{display:block;padding:8px 12px;border-radius:4px;"
        "color:#333;text-decoration:none;border:1px solid transparent;"
        "transition:background .15s,border-color .15s;line-height:1.5;}",
        ".article-list a:hover{background:#f0f7ff;border-color:#cce4ff;color:#008cff;}",
        ".year-nav{display:flex;flex-wrap:wrap;gap:8px;margin:1em 0 2em;}",
        ".year-nav a{display:inline-block;padding:6px 14px;background:#eef3f8;"
        "border-radius:20px;color:#008cff;text-decoration:none;font-size:.9em;}",
        ".year-nav a:hover{background:#008cff;color:#fff;}",
        "</style>",
        '<h1 id="home"><a name="home" class="anchor-navigation-ex-anchor" '
        'href="#home"><i class="fa fa-link" aria-hidden="true"></i></a>'
        "任正非讲话实录</h1>",
        '<p class="home-intro">'
        "本站点收录 1994–2019 年任正非讲话、座谈纪要、采访记录等资料，"
        "按年份分类整理。可通过下方年份标签快速跳转，或从左侧导航栏浏览全部内容。</p>",
        '<div class="home-stats">',
        f'<div class="home-stat"><strong>{len(catalog)}</strong>年份</div>',
        f'<div class="home-stat"><strong>{total}</strong>篇文档</div>',
        '<div class="home-stat"><strong>1994–2019</strong>时间跨度</div>',
        "</div>",
        '<div class="year-nav">',
    ]

    for entry in catalog:
        parts.append(f'<a href="#year-{entry["year"]}">{entry["year"]}</a>')
    parts.append("</div>")

    parts.append(
        '<h2 id="catalog"><a name="catalog" class="anchor-navigation-ex-anchor" '
        'href="#catalog"><i class="fa fa-link" aria-hidden="true"></i></a>目录索引</h2>'
    )

    for entry in catalog:
        year = entry["year"]
        articles = entry["articles"]
        parts.append(f'<div class="year-section" id="year-{year}">')
        parts.append(
            f'<h3 class="year-title">{year}'
            f'<span class="year-count">（{len(articles)} 篇）</span></h3>'
        )
        parts.append('<ul class="article-list">')
        for art in articles:
            parts.append(
                f'<li><a href="{escape(art["link"])}">'
                f'{escape(art["title"])}</a></li>'
            )
        parts.append("</ul></div>")

    parts.append(
        '<footer class="page-footer-ex">'
        ' <span class="page-footer-ex-copyright">'
        ' By <a href="https://github.com/RiddleGo" target="_blank">RiddleGo</a>，'
        '使用<a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">'
        "知识共享 署名-相同方式共享 4.0协议</a>发布"
        " </span>"
        ' <span class="page-footer-ex-footer-update">'
        " <i>updated</i> 2024-07-02 21:35:10 </span>"
        " </footer>"
    )
    return "\n".join(parts)


def patch_index_html(content_html: str):
    with open(INDEX_PATH, encoding="utf-8") as f:
        html = f.read()

    html = re.sub(
        r"<title>.*?</title>",
        "<title>任正非讲话实录 · 目录索引</title>",
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="任正非讲话实录：1994-2019 年任正非讲话、座谈纪要与采访记录，按年份分类索引">',
        html,
        count=1,
    )

    html = re.sub(
        r'(<li class="chapter active"[^>]*>\s*<a href="\./">)\s*'
        r"(?:Introduction|首页)\s*(</a>)",
        r"\1\n            \n                    \n                    首页\n            \2",
        html,
        count=1,
    )

    html = re.sub(
        r'<a href="\."[^>]*>(Introduction|任正非讲话实录)</a>',
        '<a href="." >任正非讲话实录</a>',
        html,
        count=1,
    )

    start_marker = '<section class="normal markdown-section">'
    end_marker = "</section>"
    start = html.find(start_marker)
    if start == -1:
        raise SystemExit("Could not find content section")
    start += len(start_marker)
    end = html.find(end_marker, start)
    html = (
        html[:start]
        + "\n                                \n"
        + content_html
        + "\n                                \n"
        + html[end:]
    )

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Patched {INDEX_PATH}")


if __name__ == "__main__":
    with open(INDEX_PATH, encoding="utf-8") as f:
        source = f.read()
    catalog = parse_sidebar(source)
    content = build_homepage_html(catalog)
    patch_index_html(content)
    total = sum(len(y["articles"]) for y in catalog)
    print(f"Generated homepage: {len(catalog)} years, {total} articles")
