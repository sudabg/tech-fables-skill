#!/usr/bin/env python3
"""
Tech Fables — Interactive Project Scaffolder
=============================================

One-command setup for any tech-domain fable project.

Usage (interactive):
    python3 init-project.py

Usage (non-interactive / CI):
    python3 init-project.py \
        --name my-fables \
        --title "My Fables" \
        --title-cn "我的寓言" \
        --tagline "Learn concepts through stories" \
        --categories 'consensus:Consensus:共识:⚖️:desc|replication:Replication:复制:📦:desc' \
        --output .
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def ask(prompt: str, default: str = "") -> str:
    """Prompt user with optional default."""
    if default:
        full = f"{prompt} [{default}]: "
    else:
        full = f"{prompt}: "
    try:
        reply = input(full).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)
    return reply if reply else default


def sanitize_slug(raw: str) -> str:
    """Sanitize directory slug: lowercase, alphanumeric + hyphen only."""
    import re
    s = raw.lower().strip()
    s = re.sub(r'[^a-z0-9-]', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s or "category"


def ask_bool(prompt: str, default: bool = True) -> bool:
    """Yes/no prompt."""
    suffix = "Y/n" if default else "y/N"
    reply = ask(prompt, suffix).lower()
    if reply in ("y", "yes", "Y"):
        return True
    if reply in ("n", "no", "N"):
        return False
    return default


def collect_categories() -> list:
    """Interactively collect category definitions."""
    categories = []
    print("\n--- Categories ---")
    print("Define your content categories (e.g., Consensus, Replication, ...)")
    print("Press Enter on empty slug to finish.\n")

    defaults = [
        ("architecture", "Architecture", "架构设计", "🏗️", "系统架构与核心设计模式"),
        ("protocol", "Protocol", "协议机制", "📜", "通信协议与共识机制"),
        ("security", "Security", "安全", "🔒", "安全模型与攻击防御"),
    ]

    for i, (slug, en, cn, emoji, desc) in enumerate(defaults, 1):
        print(f"\nCategory {i}:")
        slug = sanitize_slug(ask("  Directory slug", slug))
        if not slug:
            break
        en_title = ask("  English title", en)
        cn_title = ask("  Chinese title", cn)
        icon = ask("  Emoji icon", emoji)
        description = ask("  Short description", desc)
        categories.append((slug, en_title, cn_title, icon, description))

    # Extra categories
    while True:
        print(f"\nCategory {len(categories) + 1}:")
        slug = sanitize_slug(ask("  Directory slug (empty to finish)", ""))
        if not slug:
            break
        en_title = ask("  English title")
        cn_title = ask("  Chinese title")
        icon = ask("  Emoji icon", "📦")
        description = ask("  Short description")
        categories.append((slug, en_title, cn_title, icon, description))

    return categories


def generate_project(project_name: str, project_title: str, project_title_cn: str,
                     tagline: str, categories: list, output_dir: Path) -> Path:
    """Generate the full project scaffold."""
    base = output_dir / project_name
    base.mkdir(parents=True, exist_ok=True)

    # Directory structure
    for cat_dir, _, _, _, _ in categories:
        (base / "fables" / cat_dir).mkdir(parents=True, exist_ok=True)
        (base / "fables" / "en" / cat_dir).mkdir(parents=True, exist_ok=True)
    (base / "scripts").mkdir(exist_ok=True)
    (base / "templates").mkdir(exist_ok=True)
    (base / "public").mkdir(exist_ok=True)
    (base / ".vitepress").mkdir(exist_ok=True)
    (base / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    # package.json
    pkg = {
        "name": project_name,
        "private": True,
        "version": "1.0.0",
        "description": f"Learn {project_title} concepts through allegorical stories",
        "devDependencies": {"vitepress": "^1.6.4"},
        "scripts": {
            "dev": "vitepress dev",
            "build": "vitepress build",
            "preview": "vitepress preview"
        }
    }
    (base / "package.json").write_text(json.dumps(pkg, ensure_ascii=False, indent=2), encoding="utf-8")

    # .vitepress/config.mjs
    sidebar_cn = []
    sidebar_en = []
    for slug, en, cn, icon, _ in categories:
        sidebar_cn.append(json.dumps({
            "text": f"{icon} {cn}",
            "collapsed": False,
            "items": [
                {"text": "📑 分类概览", "link": f"/fables/{slug}/"},
                {"text": "【示例】待创作", "link": f"/fables/{slug}/01-example"},
            ]
        }, ensure_ascii=False, indent=8))
        sidebar_en.append(json.dumps({
            "text": f"{icon} {en}",
            "collapsed": False,
            "items": [
                {"text": "📑 Overview", "link": f"/fables/en/{slug}/"},
                {"text": "[Example] TBD", "link": f"/fables/en/{slug}/01-example"},
            ]
        }, ensure_ascii=False, indent=8))

    config = f'''import {{ defineConfig }} from 'vitepress'

export default defineConfig({{
  title: '{project_title_cn}',
  description: '{tagline}',
  base: '/{project_name}/',
  lang: 'zh-CN',
  lastUpdated: true,
  ignoreDeadLinks: true,
  srcExclude: ['README.md', 'scripts/**', 'package.json', 'package-lock.json', 'node_modules/**'],
  themeConfig: {{
    logo: '📜',
    nav: [
      {{ text: 'Home', link: '/' }},
      {{ text: 'Fables', link: '/fables/{categories[0][0]}/01-example' }},
      {{ text: 'English', link: '/fables/en/' }},
      {{ text: 'GitHub', link: 'https://github.com/yourname/{project_name}' }}
    ],
    sidebar: {{
      '/fables/en/': [
{','.join(sidebar_en)}
      ],
      '/fables/': [
{','.join(sidebar_cn)}
      ]
    }},
    search: {{
      provider: 'local',
      options: {{
        locales: {{
          root: {{
            translations: {{
              button: {{ buttonText: '搜索寓言', buttonAriaLabel: '搜索寓言' }},
              modal: {{
                noResultsText: '未找到相关寓言',
                resetButtonTitle: '清除搜索',
                footer: {{ selectText: '选择', navigateText: '切换', closeText: '关闭' }}
              }}
            }}
          }}
        }}
      }}
    }},
    editLink: {{
      pattern: 'https://github.com/yourname/{project_name}/edit/main/:path',
      text: 'Edit this page on GitHub'
    }},
    lastUpdated: {{ text: 'Updated at' }},
    docFooter: {{ prev: 'Previous Fable', next: 'Next Fable' }}
  }},
  head: [
    ['meta', {{ name: 'theme-color', content: '#66fcf1' }}]
  ]
}})
'''
    (base / ".vitepress" / "config.mjs").write_text(config, encoding="utf-8")

    # index.md (homepage)
    features = "\n".join(
        f"  - icon: {icon}\n    title: {cn}\n    details: {desc}\n    link: /fables/{slug}/"
        for slug, _, cn, icon, desc in categories
    )
    toc_rows = "\n".join(f"| {cn} | — | 待创作 |" for _, _, cn, _, _ in categories)

    index = f'''---
layout: home

hero:
  name: "{project_title}"
  text: "{project_title_cn}"
  tagline: {tagline}
  actions:
    - theme: brand
      text: 开始阅读
      link: /fables/{categories[0][0]}/01-example
    - theme: alt
      text: GitHub
      link: https://github.com/yourname/{project_name}

features:
{features}
---

## 关于本项目

**{project_title}** 是一个开源教育项目，将 {project_title_cn} 的核心概念转化为古老风格的寓言故事。

### 📥 下载电子书

- [PDF 版]({project_name}.pdf) — 适合打印和离线阅读
- [EPUB 版]({project_name}.epub) — 适合电子书和手机阅读

### 核心理念

> *"同一个概念，套上不同的隐喻，理解可以天差地别。"*

## 目录概览

| 类别 | 篇数 | 代表寓言 |
|------|------|----------|
{toc_rows}

**总计：待填充**

## 贡献

欢迎提交 PR！每则寓言需遵循 [叙事契约](CONTRIBUTING.md)。
'''
    (base / "index.md").write_text(index, encoding="utf-8")

    # CONTRIBUTING.md
    valid_cats = ", ".join(f'"{s[0]}"' for s in categories)
    contributing = f'''# 贡献指南

## 叙事契约

1. **延迟揭示**：故事前 1/3 不暴露技术术语
2. **角色动机**：角色有自己的利益和盲点
3. **冲突代价**：错误决策带来可感知的后果
4. **完整映射**：每个核心设定都有技术对应
5. **概念准确**：故事可简化，不能歪曲

## Frontmatter 规范

```yaml
---
title: "中文标题 / English Title"
title_cn: "中文标题"
concept: "Technical Concept"
concept_cn: "技术概念中文名"
category: "{categories[0][0]}"
difficulty: "intermediate"  # beginner | intermediate | advanced
author: "your-name"
created: "YYYY-MM-DD"
reading_time: 5   # auto-calculated by scripts
word_count: 1200  # auto-calculated by scripts
sources:
  - "path/to/source.md"
tags: [tag1, tag2]
---
```

## 难度分级

- 🟢 **初级**：不需要前置知识
- 🟡 **中级**：需要了解该领域基础概念
- 🔴 **高级**：需要深入理解相关前置知识

## 写作模板

参见 `templates/fable-template.md`。

## 质量门禁

提交前运行验证脚本：

```bash
python3 scripts/validate-fables.py
```
'''
    (base / "CONTRIBUTING.md").write_text(contributing, encoding="utf-8")

    # fable-template.md
    template = '''---
title: "中文标题 / English Title"
title_cn: "中文标题"
concept: "Concept Name"
concept_cn: "概念中文名"
category: "CATEGORY"
difficulty: "intermediate"
author: "your-name"
created: "2026-01-01"
reading_time: 5
word_count: 1200
sources:
  - "path/to/source.md"
tags: [tag1, tag2]
---

# 中文标题 / English Title

> *"一句点题的引语。"*

## 故事

[在这里写故事。1000-3000 字。]

---

## 这则寓言在说什么

### 关键映射

| 故事元素 | 技术概念 | 说明 |
|---------|---------|------|

### 为什么是这个故事？

### 延伸阅读

- [源概念](path/to/source)
'''
    (base / "templates" / "fable-template.md").write_text(template, encoding="utf-8")

    # validate-fables.py
    validate = f'''#!/usr/bin/env python3
"""Validate all fables for structural compliance."""
import sys
import yaml
from pathlib import Path

VALID_CATEGORIES = {{{valid_cats}}}
VALID_DIFFICULTIES = {{"beginner", "intermediate", "advanced"}}
REQUIRED_FIELDS = {{"title", "concept", "category", "difficulty"}}

errors = 0


def extract_frontmatter(path: Path):
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]), parts[2]
            except Exception as e:
                print(f"YAML ERROR: {{path}} - {{e}}")
                return None, None
    return None, None


def count_words_mixed(text: str) -> int:
    import re
    cn = len(re.findall(r'[\\u4e00-\\u9fff]', text))
    en = len(re.findall(r'[a-zA-Z]{{2,}}', text))
    num = len(re.findall(r'\\d+', text))
    return cn + en + num


def estimate_reading_time(word_count: int) -> int:
    return max(1, round(word_count / 220))


for md_file in sorted(Path("fables").rglob("*.md")):
    if md_file.name == "index.md":
        continue
    fm, body = extract_frontmatter(md_file)
    if fm is None:
        errors += 1
        continue

    missing = REQUIRED_FIELDS - set(fm.keys())
    if missing:
        print(f"MISSING fields in {{md_file}}: {{missing}}")
        errors += 1

    if fm.get("category") not in VALID_CATEGORIES:
        print(f"INVALID category in {{md_file}}: {{fm.get('category')}}")
        errors += 1

    if fm.get("difficulty") not in VALID_DIFFICULTIES:
        print(f"INVALID difficulty in {{md_file}}: {{fm.get('difficulty')}}")
        errors += 1

    if "## 故事" not in body:
        print(f"MISSING '## 故事' in {{md_file}}")
        errors += 1

    if "## 这则寓言在说什么" not in body:
        print(f"MISSING '## 这则寓言在说什么' in {{md_file}}")
        errors += 1

    # Auto-update word_count and reading_time
    words = count_words_mixed(body)
    rt = estimate_reading_time(words)
    if fm.get("word_count") != words or fm.get("reading_time") != rt:
        # Update frontmatter
        fm["word_count"] = words
        fm["reading_time"] = rt
        new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_content = f"---\\n{{new_fm}}---{{body}}"
        md_file.write_text(new_content, encoding="utf-8")
        print(f"UPDATED metadata in {{md_file}}: {{words}} words, ~{{rt}} min")

if errors:
    print(f"\\n❌ {{errors}} error(s) found.")
    sys.exit(1)
else:
    print("✅ All fables passed validation.")
'''
    vpath = base / "scripts" / "validate-fables.py"
    vpath.write_text(validate, encoding="utf-8")
    os.chmod(vpath, 0o755)

    # GitHub Actions workflow
    workflow = '''name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .vitepress/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
'''
    (base / ".github" / "workflows" / "deploy.yml").write_text(workflow, encoding="utf-8")

    # README.md
    readme = f'''# {project_title} / {project_title_cn}

> {tagline}

## 快速开始

```bash
git clone https://github.com/yourname/{project_name}.git
cd {project_name}
npm install
npm run dev
```

## 项目结构

```
{project_name}/
├── fables/              # 寓言内容
│   ├── {{category}}/    # 中文分类
│   └── en/              # 英文版镜像
├── scripts/             # 验证 + 电子书生成
├── templates/           # 写作模板
├── public/              # 静态资源（PDF/EPUB）
└── .vitepress/          # 站点配置
```

## 贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.md)。
'''
    (base / "README.md").write_text(readme, encoding="utf-8")

    # .gitignore
    (base / ".gitignore").write_text("""node_modules/
.vitepress/dist/
.vitepress/cache/
""", encoding="utf-8")

    return base


def main():
    parser = argparse.ArgumentParser(description="Tech Fables Project Scaffolder")
    parser.add_argument("--name", help="Project directory name")
    parser.add_argument("--title", help="Project English title")
    parser.add_argument("--title-cn", help="Project Chinese title")
    parser.add_argument("--tagline", help="One-line tagline")
    parser.add_argument("--categories", help="Categories in format: slug:en:cn:emoji:desc|...")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--non-interactive", action="store_true", help="Skip interactive prompts")
    args = parser.parse_args()

    if args.non_interactive:
        if not all([args.name, args.title, args.title_cn, args.tagline, args.categories]):
            print("Error: --non-interactive requires --name, --title, --title-cn, --tagline, --categories")
            sys.exit(1)
        project_name = args.name
        project_title = args.title
        project_title_cn = args.title_cn
        tagline = args.tagline
        categories = []
        for cat_str in args.categories.split("|"):
            parts = cat_str.split(":")
            if len(parts) != 5:
                print(f"Error: Invalid category format: {cat_str}")
                sys.exit(1)
            categories.append((sanitize_slug(parts[0]), parts[1], parts[2], parts[3], parts[4]))
        output_dir = Path(args.output)
    else:
        print("=" * 60)
        print("  Tech Fables — Interactive Project Scaffolder")
        print("=" * 60)
        print()

        project_name = ask("Project directory name (repo name)", "my-fables")
        project_title = ask("Project English title", project_name.replace("-", " ").title())
        project_title_cn = ask("Project Chinese title", project_title)
        tagline = ask("One-line tagline", f"用古老寓言的隐喻，理解 {project_title_cn} 的核心概念")

        categories = collect_categories()
        if not categories:
            print("Error: At least one category is required.")
            sys.exit(1)

        output_dir = Path(ask("Output directory", "."))

    output_dir = output_dir.resolve()

    print(f"\n⚙️  Generating project: {project_name}")
    base = generate_project(project_name, project_title, project_title_cn,
                            tagline, categories, output_dir)

    print(f"\n✅ Project scaffold created at: {base}")
    print(f"   Categories: {len(categories)}")
    print()
    print("Next steps:")
    print(f"  1. cd {project_name}")
    print("  2. npm install")
    print("  3. Copy generate-ebooks.py from tech-fables skill scripts/")
    print("  4. npm run dev")
    print("  5. Start writing fables per CONTRIBUTING.md")


if __name__ == "__main__":
    main()
