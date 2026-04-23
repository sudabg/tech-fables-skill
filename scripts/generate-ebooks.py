#!/usr/bin/env python3
"""
Generate professional PDF and EPUB ebooks from Tech Fables markdown sources.

Usage:
    python3 scripts/generate-ebooks.py

Dependencies:
    pip install weasyprint ebooklib markdown pyyaml

Outputs:
    public/{project-name}.pdf   — A4 print-ready PDF
    public/{project-name}.epub  — EPUB for e-readers
    site/{project-name}.html    — Intermediate HTML (for debugging)
"""

import yaml
import markdown
from pathlib import Path
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from ebooklib import epub

BASE_DIR = Path(__file__).parent.parent
FABLES_DIR = BASE_DIR / "fables"
PUBLIC_DIR = BASE_DIR / "public"
SITE_DIR = BASE_DIR / "site"


def extract_frontmatter(path: Path):
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                data = yaml.safe_load(parts[1])
            except Exception:
                data = {}
            return data, parts[2]
    return {}, content


def discover_categories():
    """Auto-discover categories from fables/ directory."""
    cats = []
    for d in sorted(FABLES_DIR.iterdir()):
        if d.is_dir() and d.name != "en":
            # Try to read category index for title
            idx = d / "index.md"
            title = d.name.capitalize()
            if idx.exists():
                fm, _ = extract_frontmatter(idx)
                title = fm.get("title", title)
            cats.append((d.name, title))
    return cats


def load_fables():
    """Load all Chinese fables grouped by category."""
    cats = discover_categories()
    result = []
    for slug, title in cats:
        cat_dir = FABLES_DIR / slug
        if not cat_dir.exists():
            continue
        fables = []
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            fm, body = extract_frontmatter(md_file)
            fables.append({
                "path": md_file,
                "slug": md_file.stem,
                "title": fm.get("title", ""),
                "title_cn": fm.get("title_cn", ""),
                "concept": fm.get("concept_cn", fm.get("concept", "")),
                "difficulty": fm.get("difficulty", "intermediate"),
                "reading_time": fm.get("reading_time", 5),
                "word_count": fm.get("word_count", 0),
                "tags": fm.get("tags", []),
                "body_md": body,
            })
        fables.sort(key=lambda x: x["slug"])
        result.append((slug, title, fables))
    return result


def build_pdf(cn_fables: list, project_name: str, project_title: str):
    """Generate A4 PDF with cover, TOC, metadata cards, and category dividers."""
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    total = sum(len(f) for _, _, f in cn_fables)

    html_parts = []

    # Cover
    html_parts.append(
        f'<div class="cover"><div class="cover-content">'
        f'<div class="cover-icon">📜</div>'
        f'<h1 class="cover-title">{project_title}</h1>'
        f'<div class="cover-meta"><p>{total} fables</p></div>'
        f'</div></div>'
    )

    # TOC
    html_parts.append(
        '<div class="toc-page"><h1 class="toc-title">目录</h1>'
        '<table class="toc-table"><thead><tr>'
        '<th>编号</th><th>寓言</th><th>概念</th><th>难度</th><th>阅读时间</th>'
        '</tr></thead><tbody>'
    )
    idx = 1
    for cat, cat_title, fables in cn_fables:
        for f in fables:
            diff = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}.get(f["difficulty"], "🟡")
            html_parts.append(
                f'<tr><td>{idx}</td><td><a href="#fable-{idx}">{f["title"]}</a></td>'
                f'<td>{f["concept"]}</td><td>{diff}</td><td>{f["reading_time"]} min</td></tr>'
            )
            idx += 1
    html_parts.append("</tbody></table></div>")

    # Fables
    idx = 1
    for cat, cat_title, fables in cn_fables:
        html_parts.append(
            f'<div class="category-divider"><span class="category-label">{cat_title}</span></div>'
        )
        for f in fables:
            md.reset()
            body_html = md.convert(f["body_md"])
            diff_text = {"beginner": "初级", "intermediate": "中级", "advanced": "高级"}.get(
                f["difficulty"], "中级"
            )
            tags_html = " ".join([f'<span class="tag">{t}</span>' for t in f["tags"]])
            html_parts.append(
                f'<div class="fable" id="fable-{idx}">'
                f'<div class="fable-header">'
                f'<div class="fable-number">寓言 {idx}</div>'
                f'<h1 class="fable-title">{f["title"]}</h1>'
                f'<div class="fable-meta">'
                f'<span class="meta-item difficulty {f["difficulty"]}">{diff_text}</span>'
                f'<span class="meta-item">⏱️ {f["reading_time"]} 分钟</span>'
                f'<span class="meta-item">📝 {f["word_count"]} 字</span>'
                f'<span class="meta-item">💡 {f["concept"]}</span>'
                f'</div><div class="fable-tags">{tags_html}</div></div>'
                f'<div class="fable-body">{body_html}</div></div>'
            )
            idx += 1

    body = "\n".join(html_parts)

    css = """
@page { size: A4; margin: 2.5cm 2cm;
    @bottom-center { content: counter(page); font-size: 9pt; color: #888; }
    @top-left { content: attr(data-title); font-size: 8pt; color: #aaa; }
}
@page :first { @bottom-center { content: none; } @top-left { content: none; } }
* { box-sizing: border-box; }
body { font-family: "Noto Sans", "Droid Sans Fallback", "PingFang SC", sans-serif; font-size: 10.5pt; line-height: 1.75; color: #2c3e50; }
.cover { page-break-after: always; display: flex; align-items: center; justify-content: center; min-height: 24cm; text-align: center; }
.cover-icon { font-size: 72pt; margin-bottom: 0.5em; }
.cover-title { font-size: 36pt; color: #1a1a2e; margin: 0; border: none; }
.cover-meta { margin-top: 3em; font-size: 10pt; color: #888; }
.toc-page { page-break-after: always; }
.toc-title { font-size: 22pt; color: #1a1a2e; text-align: center; margin-bottom: 1.5em; border: none; }
.toc-table { width: 100%; border-collapse: collapse; font-size: 10pt; }
.toc-table th { background: #1a1a2e; color: #fff; padding: 8px 10px; text-align: left; }
.toc-table td { padding: 6px 10px; border-bottom: 1px solid #eee; }
.toc-table tr:nth-child(even) { background: #f8f9fa; }
.category-divider { page-break-before: always; text-align: center; padding: 3em 0; margin: 2em 0; border-top: 2px solid #66fcf1; border-bottom: 2px solid #66fcf1; }
.category-label { font-size: 18pt; color: #1a1a2e; font-weight: bold; }
.fable { page-break-before: always; margin-bottom: 2em; }
.fable:first-of-type { page-break-before: auto; }
.fable-header { background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-left: 5px solid #66fcf1; padding: 1.2em 1.5em; margin-bottom: 1.5em; border-radius: 0 8px 8px 0; }
.fable-number { font-size: 9pt; color: #888; text-transform: uppercase; letter-spacing: 1pt; margin-bottom: 0.3em; }
.fable-title { font-size: 20pt; color: #1a1a2e; margin: 0 0 0.5em 0; border: none; }
.fable-meta { display: flex; flex-wrap: wrap; gap: 0.8em; font-size: 9pt; color: #555; margin-bottom: 0.5em; }
.meta-item { background: #fff; padding: 2px 8px; border-radius: 4px; border: 1px solid #ddd; }
.difficulty.beginner { background: #d4edda; color: #155724; border-color: #c3e6cb; }
.difficulty.intermediate { background: #fff3cd; color: #856404; border-color: #ffeeba; }
.difficulty.advanced { background: #f8d7da; color: #721c24; border-color: #f5c6cb; }
.tag { display: inline-block; font-size: 8pt; background: #1a1a2e; color: #fff; padding: 2px 8px; border-radius: 12px; margin-right: 4px; }
.fable-body h1 { font-size: 16pt; color: #1a1a2e; border-bottom: 2px solid #66fcf1; padding-bottom: 0.3em; margin-top: 1.2em; }
.fable-body h2 { font-size: 14pt; color: #16213e; margin-top: 1em; }
.fable-body h3 { font-size: 12pt; color: #0f3460; margin-top: 0.8em; }
.fable-body p { margin: 0.8em 0; text-align: justify; }
.fable-body blockquote { border-left: 4px solid #66fcf1; margin: 1em 0; padding: 0.8em 1.2em; background: #f8f9fa; color: #555; font-style: italic; border-radius: 0 4px 4px 0; }
.fable-body table { width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 9.5pt; }
.fable-body th { background: #1a1a2e; color: #fff; padding: 8px 10px; text-align: left; }
.fable-body td { padding: 6px 10px; border: 1px solid #ddd; }
.fable-body tr:nth-child(even) { background: #f8f9fa; }
.fable-body code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 0.9em; color: #e94560; }
.fable-body pre { background: #1a1a2e; color: #e94560; padding: 1em; border-radius: 6px; overflow-x: auto; font-family: monospace; font-size: 9pt; }
.fable-body pre code { background: transparent; color: inherit; padding: 0; }
.fable-body ul, .fable-body ol { margin: 0.8em 0; padding-left: 2em; }
.fable-body li { margin: 0.3em 0; }
p, li { orphans: 3; widows: 3; }
"""

    html_doc = f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>{project_title}</title><style>{css}</style></head><body>{body}</body></html>"

    SITE_DIR.mkdir(exist_ok=True)
    PUBLIC_DIR.mkdir(exist_ok=True)

    html_path = SITE_DIR / f"{project_name}.html"
    html_path.write_text(html_doc, encoding="utf-8")
    print(f"[HTML] {html_path}")

    pdf_path = PUBLIC_DIR / f"{project_name}.pdf"
    HTML(string=html_doc).write_pdf(str(pdf_path), font_config=FontConfiguration())
    print(f"[PDF] {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")
    return pdf_path


def build_epub(cn_fables: list, project_name: str, project_title: str):
    """Generate EPUB with cover, TOC, and per-fable chapters."""
    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    total = sum(len(f) for _, _, f in cn_fables)

    book = epub.EpubBook()
    book.set_identifier(f"{project_name}-v1.0")
    book.set_title(project_title)
    book.set_language("zh-CN")
    book.add_author(project_name)

    css = """
body { font-family: "Noto Sans", "Droid Sans Fallback", sans-serif; line-height: 1.7; color: #2c3e50; margin: 1em; }
h1 { color: #1a1a2e; border-bottom: 2px solid #66fcf1; padding-bottom: 0.3em; }
h2 { color: #16213e; margin-top: 1.5em; }
blockquote { border-left: 4px solid #66fcf1; margin: 1em 0; padding: 0.5em 1em; background: #f8f9fa; font-style: italic; }
table { width: 100%; border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #1a1a2e; color: #fff; }
tr:nth-child(even) { background: #f8f9fa; }
code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
pre { background: #1a1a2e; color: #e94560; padding: 1em; border-radius: 6px; overflow-x: auto; }
.meta-box { background: #f8f9fa; border-left: 4px solid #66fcf1; padding: 1em; margin: 1em 0; border-radius: 0 4px 4px 0; }
.meta-line { font-size: 0.9em; color: #666; margin: 0.3em 0; }
.tag { display: inline-block; font-size: 0.8em; background: #1a1a2e; color: #fff; padding: 2px 8px; border-radius: 12px; margin-right: 4px; }
"""
    style = epub.EpubItem(uid="style", file_name="style/styles.css", media_type="text/css", content=css)
    book.add_item(style)

    # Cover
    cover_html = f"""<html><head><link rel='stylesheet' href='style/styles.css'/></head><body>
<div style='text-align:center; padding-top: 5em;'><div style='font-size: 72pt;'>📜</div>
<h1 style='border:none; font-size: 36pt;'>{project_title}</h1>
<p style='color: #aaa; margin-top: 3em;'>{total} fables</p></div></body></html>"""
    cover = epub.EpubHtml(title="Cover", file_name="cover.xhtml", lang="zh-CN")
    cover.content = cover_html
    book.add_item(cover)

    # TOC
    toc_rows = []
    idx = 1
    for cat, cat_title, fables in cn_fables:
        for f in fables:
            diff = {"beginner": "🟢 初级", "intermediate": "🟡 中级", "advanced": "🔴 高级"}.get(
                f["difficulty"], "🟡 中级"
            )
            toc_rows.append(
                f'<tr><td>{idx}</td><td><a href="fable_{idx}.xhtml">{f["title"]}</a></td>'
                f'<td>{f["concept"]}</td><td>{diff}</td><td>{f["reading_time"]} min</td></tr>'
            )
            idx += 1

    toc_html = f"""<html><head><link rel='stylesheet' href='style/styles.css'/></head><body>
<h1>目录</h1><table><thead><tr><th>编号</th><th>寓言</th><th>概念</th><th>难度</th><th>阅读时间</th></tr></thead>
<tbody>{''.join(toc_rows)}</tbody></table></body></html>"""
    toc_page = epub.EpubHtml(title="目录", file_name="toc.xhtml", lang="zh-CN")
    toc_page.content = toc_html
    book.add_item(toc_page)

    # Chapters
    idx = 1
    spine = ["cover", "toc"]
    for cat, cat_title, fables in cn_fables:
        for f in fables:
            md.reset()
            body_html = md.convert(f["body_md"])
            diff_text = {"beginner": "初级", "intermediate": "中级", "advanced": "高级"}.get(
                f["difficulty"], "中级"
            )
            tags_html = " ".join([f'<span class="tag">{t}</span>' for t in f["tags"]])
            chapter_html = f"""<html><head><link rel='stylesheet' href='style/styles.css'/></head><body>
<div class='meta-box'><div style='font-size: 0.85em; color: #888; margin-bottom: 0.5em;'>寓言 {idx} · {cat_title}</div>
<h1 style='margin-top:0; border:none;'>{f['title']}</h1>
<div class='meta-line'>难度: <strong>{diff_text}</strong> · 阅读时间: ⏱️ {f['reading_time']} 分钟 · 字数: {f['word_count']}</div>
<div class='meta-line'>概念: {f['concept']}</div><div style='margin-top: 0.5em;'>{tags_html}</div></div>
{body_html}</body></html>"""
            chapter = epub.EpubHtml(title=f["title"], file_name=f"fable_{idx}.xhtml", lang="zh-CN")
            chapter.content = chapter_html
            book.add_item(chapter)
            spine.append(chapter)
            idx += 1

    book.spine = spine
    book.toc = [epub.Link("toc.xhtml", "目录", "toc")] + [
        epub.Link(f"fable_{i}.xhtml", f["title"], f"fable_{i}")
        for i, f in enumerate([f for _, _, fs in cn_fables for f in fs], 1)
    ]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    PUBLIC_DIR.mkdir(exist_ok=True)
    epub_path = PUBLIC_DIR / f"{project_name}.epub"
    epub.write_epub(str(epub_path), book, {})
    print(f"[EPUB] {epub_path} ({epub_path.stat().st_size / 1024:.1f} KB)")
    return epub_path


def main():
    import re
    # Auto-detect project name from directory
    project_name = BASE_DIR.name
    project_title = project_name.replace("-", " ").title()

    cn_fables = load_fables()
    total = sum(len(f) for _, _, f in cn_fables)
    if not total:
        print("No fables found in fables/ directory.")
        return

    print(f"Loaded {total} fables from {len(cn_fables)} categories")
    build_pdf(cn_fables, project_name, project_title)
    build_epub(cn_fables, project_name, project_title)
    print("Done!")


if __name__ == "__main__":
    main()
