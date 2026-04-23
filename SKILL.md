---
name: tech-fables-project
description: |
  Create and maintain open-source "Tech Fables" projects that explain technical concepts through allegorical stories.
  One-command scaffold → write → validate → build ebooks → deploy.
  Works for any technical domain: distributed systems, cryptography, ML, compilers, etc.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fables, storytelling, education, technical-writing, open-source, metaphor, scaffolding]
    category: creative
    related_skills: [llm-wiki, knowledge-crawl-pipeline, baoyu-comic]
---

# Tech Fables Project

将任意技术领域的核心概念转化为寓言故事的开源教育项目框架。

**一句话定位**：你输入一个技术领域和分类体系，一键生成完整的项目脚手架（VitePress 双语站点 + 写作模板 + 验证脚本 + 电子书生成 + CI/CD），然后只需要专注写故事。

## 何时使用

- 需要将技术概念以故事形式传播（降低认知门槛）
- 维护一个按领域分类的"概念 → 故事"映射库
- 社区协作写作，需要统一格式和质量门禁
- 想为任意开源项目（分布式系统、密码学、编译器、ML 等）创建教育内容

## 快速开始（一行命令）

```bash
git clone https://github.com/sudabg/tech-fables-skill.git
cd tech-fables-skill
python3 scripts/init-project.py
# 按提示输入项目名、分类、隐喻主题
cd <your-project>
npm install && npm run dev
```

## 核心方法论：叙事契约

所有寓言必须遵守以下 5 条铁律：

1. **延迟揭示**：故事前 1/3 不暴露技术术语，读者在阅读中逐渐猜到映射关系
2. **有角色有动机**：角色的盲点对应技术中的常见误解
3. **有冲突有代价**：错误决策带来可感知的后果，让读者"痛"到记住
4. **完整映射**：每个核心设定在注解中有技术对应，禁止"为了文学性虚设情节"
5. **概念准确**：故事可以被简化，不能被歪曲。简化处必须在注解中标注

### 隐喻选择原则

- **好的隐喻**：世界内部的运行规则与技术机制一一对应，冲突点恰好是技术风险点
- **坏的隐喻**：把技术术语直接翻译成日常用语（"区块链就是一本公开账本"）
- **好的角色**：有自己的利益和盲点，盲点对应常见误解

## 项目结构模板（含双语支持）

```
project-name/
├── README.md                          # 项目介绍、阅读示例、快速开始
├── CONTRIBUTING.md                    # 叙事契约、质量标准、frontmatter 规范
├── LICENSE
├── package.json                       # VitePress 依赖（CI 必需）
├── index.md                           # VitePress 首页（features + hero）
├── concepts-catalog.md                # 源概念 → 寓言映射目录（追踪覆盖度）
├── templates/
│   └── fable-template.md              # 标准化写作模板
├── scripts/
│   ├── init-project.py                # ← 一键生成项目脚手架（交互式）
│   ├── generate-ebooks.py             # ← 生成 PDF/EPUB 电子书
│   └── validate-fables.py             # ← 结构校验 + 元数据自动更新
├── public/                            # VitePress 自动复制到 dist/ 的静态资源
│   ├── *.pdf                          # 电子书（会被部署）
│   ├── *.epub
│   └── CNAME                          # 自定义域名（如需要）
├── .github/workflows/
│   └── deploy.yml                     # GitHub Pages 自动部署
├── .vitepress/
│   └── config.mjs                     # 双语 Sidebar 配置
├── site/                              # 脚本中间输出（不会被部署）
└── fables/
    ├── consensus/
    │   ├── index.md                   # ← 分类索引页（概览 + 寓言列表）
    │   └── 01-the-byzantine-generals.md
    ├── replication/
    │   ├── index.md
    │   └── ...
    └── en/                            # 英文版镜像目录
        ├── index.md                   # ← 英文版首页（分类导航）
        ├── consensus/
        │   └── 01-the-byzantine-generals.md
        └── ...
```

**关键目录说明**：
- `public/` — VitePress 唯一自动部署的静态资源目录。电子书、CNAME、图片放这里。
- `fables/{category}/index.md` — 分类索引页，被首页 feature `link` 指向，含概览表格。
- `fables/en/` — 英文版镜像目录，与中文版完全相同的目录结构。
- `site/` — 脚本中间输出，**不会被 VitePress 部署**，不要放最终资源。

**双语目录选择**：使用 `fables/en/` 镜像目录，而非 `fables/category/xx.en.md` 后缀。原因：
1. VitePress 路由更干净（`/fables/en/security/...` vs `/fables/security/xx.en`）
2. 与 VitePress i18n 结构兼容
3. 批量处理脚本更容易区分语言（检查路径是否包含 `/en/`）

## 标准化 Frontmatter

```yaml
---
title: "中文标题 / English Title"
title_cn: "中文标题"              # 英文版中保留，用于双语对照搜索
concept: "Technical Concept Name"
concept_cn: "技术概念中文名"      # 同上
category: "consensus"             # 从预定义类别中选择
difficulty: "intermediate"        # beginner | intermediate | advanced
author: "your-name"
created: "YYYY-MM-DD"
reading_time: 5                   # 由 validate-fables.py 自动计算
word_count: 1200                  # 由 validate-fables.py 自动计算
sources:
  - "path/to/source-concept.md"
tags: [tag1, tag2, tag3]
---
```

## 正文结构

```markdown
# 中文标题 / English Title

> *"一句点题的引语，可选。"*

## 故事

[1500-3000 字。完整的虚构世界，直到结尾读者才意识到映射关系。]

---

## 这则寓言在说什么

[解释概念，500-1000 字]

### 关键映射

| 故事元素 | 技术概念 | 说明 |
|---------|---------|------|
| ... | ... | 为什么这个映射是准确的 |

### 为什么是这个故事？

[解释隐喻选择理由：世界规则如何复现技术约束]

### 延伸阅读

- [源概念原文](path/to/source)
```

## 自动化脚本详解

### init-project.py（交互式脚手架）

运行后依次收集：
1. 项目目录名（repo 名）
2. 英文标题 + 中文标题
3. 一句话 tagline
4. 分类列表（slug / 英文标题 / 中文标题 / emoji / 简介）
5. 输出目录

然后自动生成完整项目：VitePress 配置、双语 Sidebar、分类目录、GitHub Actions、验证脚本、写作模板、叙事契约。

**零依赖**：只用 Python 标准库。

### validate-fables.py（质量门禁）

校验项：
1. frontmatter 必填字段完整性
2. `category` 和 `difficulty` 取值合法性
3. `## 故事` 和 `## 这则寓言在说什么` 章节存在性
4. 故事字数范围检查
5. **自动注入/更新 `reading_time` 和 `word_count`**
6. 检查 `<>` 泛型语法是否用反引号包裹（VitePress 兼容）

**运行**：`python3 scripts/validate-fables.py`

### generate-ebooks.py（电子书生成）

**依赖**：`pip install weasyprint ebooklib markdown pyyaml`

**生成**：
- `public/{project}.pdf` — A4 打印版，含封面、目录、分类分隔页、元数据卡片
- `public/{project}.epub` — EPUB，含封面、目录、NCX 导航、每章元数据
- `site/{project}.html` — 中间 HTML（调试用）

**运行**：`python3 scripts/generate-ebooks.py`

**PDF 设计亮点**：
- 每篇寓言独立分页，带元数据头部卡片（渐变背景 + 彩色难度标签）
- 页眉显示书名，页脚显示页码
- 封面无页眉页脚
- 分类之间插入视觉分隔带
- 表格、代码块、引用块均有专业排版

## 规模化批量生产工作流（30+ 篇）

### 阶段 1：目录规划

从源知识库列出所有待覆盖概念，按领域分组：
```
Consensus:    5-7 篇
Replication:  6-8 篇
Partitioning: 6-8 篇
...
```

### 阶段 2：隐喻世界观设计（关键！）

决定你的**隐喻宇宙**：
- LLM 领域用「灯塔、铁匠铺、图书馆、王国议会」
- 分布式系统用「信使、公告板、城墙、议会投票」
- 密码学用「封印、钥匙、密室、拆信人」

**原则**：世界内部的运行规则必须与技术机制一一对应，冲突点恰好是技术风险点。

### 阶段 3：分批创作（每批 4-8 篇）

1. **批量读取源概念**：一次读取 3-5 篇 wiki/文档到上下文
2. **连续创作**：基于理解直接 write_file，不要逐篇等待确认
3. **批量验证**：运行 `validate-fables.py`
4. **修复失败项**：patch 或直接重写
5. **git commit + push**：每完成一批就提交
6. **重复直到该领域完成**

**关键经验**：
- 不同领域的概念不要在同一批次混写——保持上下文连贯性
- 故事正文控制在 1000-2000 字符（中文），总文件 6000-9000 字节
- 一次生成 2-4 篇再验证，比写一篇验一篇效率高

### 阶段 4：最终整合

- 更新 README.md 完整目录
- 确保 `concepts-catalog.md` 映射完整
- 运行 `generate-ebooks.py` 生成最终电子书
- 最终全量验证通过

## VitePress 部署

### 双语 Sidebar 配置

必须使用**路径前缀**区分中英文 sidebar：

```javascript
export default defineConfig({
  themeConfig: {
    sidebar: {
      '/fables/en/': [   // 英文路径前缀（必须先定义）
        { text: "⚖️ Consensus", items: [
          { text: "📑 Overview", link: "/fables/en/consensus/" },
          { text: "The Byzantine Generals", link: "/fables/en/consensus/01-the-byzantine-generals" },
        ]}
      ],
      '/fables/': [      // 中文路径前缀（fallback）
        { text: "⚖️ 共识算法", items: [
          { text: "📑 分类概览", link: "/fables/consensus/" },
          { text: "拜占庭将军", link: "/fables/consensus/01-the-byzantine-generals" },
        ]}
      ]
    }
  }
})
```

**关键规则**：
- 路径前缀从最长到最短匹配。`/fables/en/` 必须在 `/fables/` 之前定义
- 英文版 sidebar 中的 `link` 必须以 `/fables/en/` 开头
- 导航栏添加 `{ text: 'English', link: '/fables/en/' }` 作为语言切换入口

### 静态资源部署

电子书（PDF/EPUB）生成到 `public/` 后，VitePress 构建时自动复制到 `dist/`。

首页下载链接直接写文件名：`[PDF](project-name.pdf)`，无需 `public/` 前缀。

## LLM 批量写作提示词

```
我希望你从一个技术领域中选一个研究生水平的概念，通过写一个寓言的方式，
间接地把概念完整讲出来。最好一直到快结尾时，人才会慢慢意识到这个概念究竟是什么。

叙事要求：
1. 故事前 1/3 不要暴露任何技术术语
2. 角色要有自己的动机和盲点，盲点对应技术中的常见误解
3. 错误决策带来可感知的后果
4. 世界内部的运行规则与技术机制一一对应
5. 故事长度 1500-3000 字

故事之后，补一段解释，包含：
- 这则寓言在说什么（点明概念）
- 关键映射表（故事元素 | 技术概念 | 说明）
- 为什么是这个故事（隐喻选择理由）
- 延伸阅读（链接源概念和外部资源）

源概念材料如下：
---
{source_concept_markdown}
---
```

## 已知陷阱

### 1. VitePress 把 `Option<T>` 当成 HTML 标签

技术寓言中常出现泛型语法如 `Option<T>`、`Result<T, E>`。VitePress 的 Vue 编译器会将其解析为未闭合 HTML 标签，导致构建失败：`Element is missing end tag`。

**修复**：所有尖括号内容必须用反引号包裹成内联代码：
```markdown
| 没有空指针 | `Option<T>` / 无 null | ... |
```
批量修复：`re.sub(r'(?<![`\\])Option<T>(?!`)', '`Option<T>`', content)`

### 2. 外部 wiki 链接导致 dead links

寓言的"延伸阅读"常链接回源知识库。VitePress 构建时检查相对链接，若目标不存在则构建失败。

**修复**：`defineConfig({ ignoreDeadLinks: true })` — 知识库和寓言库是独立仓库，链接本身是合理的。

### 3. 故事提取正则截断

如果验证脚本用 `---` 作为故事结束标记，而故事与注解之间恰好用 `---` 分隔，会导致字数统计错误。

**修复**：始终匹配 `## 这则寓言在说什么` 作为故事结束边界：
```python
# ✅ 正确
re.search(r"## 故事\s*\n(.*?)\n## 这则寓言在说什么", body, re.DOTALL)
# ❌ 错误（会匹配故事内部的 ---）
re.search(r"## 故事\s*\n(.*?)\n---\s*\n", body, re.DOTALL)
```

### 4. 验证脚本类别硬编码

`VALID_CATEGORIES` 集合如果写死，新增领域时会批量失败。

**修复**：脚本应从 `fables/` 目录结构自动推断有效分类，而非硬编码。

### 5. VitePress 首页 features 无法点击

VitePress home layout 的 `features` 卡片默认不可点击。

**修复**：给每个 feature 显式添加 `link` 属性，并创建对应的分类索引页 `fables/{category}/index.md`。

### 6. `site/` 目录不会被部署

VitePress 只自动复制 `public/` 到 `dist/`。电子书若放在 `site/` 则部署后 404。

**修复**：所有需要部署的静态资源必须放在 `public/`。

## 完整启动命令

```bash
# 1. 获取 skill
git clone https://github.com/sudabg/tech-fables-skill.git
cd tech-fables-skill

# 2. 交互式初始化你的项目
python3 scripts/init-project.py
# → 输入项目名、分类、隐喻主题

# 3. 进入新项目
cd <your-project>
npm install

# 4. 开始写作
# 复制模板，按 CONTRIBUTING.md 创作

# 5. 验证
python3 scripts/validate-fables.py

# 6. 生成电子书
pip install weasyprint ebooklib markdown pyyaml
python3 scripts/generate-ebooks.py

# 7. 本地预览
npm run dev

# 8. 部署
# 推送到 GitHub，GitHub Actions 自动部署到 Pages
```
