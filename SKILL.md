---
name: tech-fables-project
description: |
  Create and maintain open-source "Tech Fables" projects that explain technical concepts through allegorical stories.
  One-command scaffold → write → validate → build ebooks → deploy.
  Use when user says "create fables project", "tech storytelling", "explain concepts through stories",
  "build educational allegory site", or wants to scaffold a bilingual VitePress project for technical writing.
  Works for any technical domain: distributed systems, cryptography, ML, compilers, etc.
  Do NOT use for general documentation sites without allegorical storytelling component.
version: 2.2.0
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

**详细方法论**（隐喻选择原则、世界观设计、批量生产工作流）：见 `references/methodology.md`

## 项目结构

生成的项目包含：

```
project-name/
├── README.md, CONTRIBUTING.md, LICENSE
├── package.json, index.md, concepts-catalog.md
├── templates/fable-template.md
├── scripts/init-project.py, validate-fables.py, generate-ebooks.py
├── public/          # 静态资源（电子书、图片）— 自动部署
├── site/            # 脚本中间输出 — 不部署
├── .vitepress/config.mjs
├── .github/workflows/deploy.yml
└── fables/
    ├── {category}/index.md + stories...
    └── en/          # 英文版镜像目录
```

**详细结构说明与 VitePress 配置**：见 `references/project-structure.md`

## 标准化 Frontmatter

```yaml
---
title: "中文标题 / English Title"
title_cn: "中文标题"
concept: "Technical Concept Name"
concept_cn: "技术概念中文名"
category: "consensus"
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

## 自动化脚本

| 脚本 | 功能 | 依赖 |
|------|------|------|
| `init-project.py` | 交互式生成完整项目脚手架 | Python 3.7+（标准库） |
| `validate-fables.py` | frontmatter 校验、字数统计、质量门禁 | Python 3.7+（标准库） |
| `generate-ebooks.py` | 生成 PDF/EPUB 电子书 | `pip install weasyprint ebooklib markdown pyyaml` |

**故障排查**（构建失败、验证错误、电子书问题）：见 `references/troubleshooting.md`

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

## 自监控与迭代

Skill 是活文档。部署后持续监控触发率和执行质量，基于反馈迭代改进。

### 健康检查

```bash
# 运行自检（评估 description 质量、结构完整性、feedback 趋势）
python3 scripts/skill-audit.py
```

输出示例：
```
Health Score: [██████████████████████████████████████░░] 97/100 (Grade A)
Issues found: 0 critical, 0 warnings, 1 suggestions
```

**评分维度**：
- frontmatter 完整性（name、description、version）
- description 质量（触发短语数量、negative triggers、字数）
- SKILL.md 体积（>5000 词扣分，提示拆分至 references/）
- references/ 和 templates/ 完整性
- feedback-log 趋势（欠触发/过触发/执行错误统计）

### 反馈记录

每次使用 skill 后，在 `references/feedback-log.md` 记录：

```markdown
- [2026-04-24] trigger: miss | user said "build tech storytelling site" | expected to trigger
- [2026-04-24] trigger: over | user said "write docs" | loaded incorrectly
- [2026-04-24] exec: error | scaffold failed with "dir exists" | expected prompt for overwrite
```

### 自动改进

```bash
# 基于 feedback-log 生成针对性改进建议
python3 scripts/skill-improve.py
```

功能：
- 分析欠触发记录 → 建议补充 description 触发短语
- 分析过触发记录 → 建议添加 negative triggers
- 分析执行错误 → 定位需要加强的指令或错误处理
- 输出可直接应用的 patch

### 迭代工作流

```
使用 skill → 记录反馈 → 运行 audit → 运行 improve → 修改 SKILL.md → 提交 → 重复
```

建议频率：
- **每次重大修改后**：运行 `skill-audit.py`
- **每周**：review `feedback-log.md`，运行 `skill-improve.py`
- **每月**：评估是否需要拆分 SKILL.md 到 references/

## 测试规范

### 触发测试

确保 skill 在以下场景自动触发：

**应该触发**：
- "帮我创建一个分布式系统的寓言项目"
- "用故事方式讲解密码学概念"
- "搭建一个 tech fables 站点"
- "把区块链知识写成寓言"

**不应该触发**：
- "写一个技术文档"（无 storytelling 成分）
- "搭建一个博客"（general docs，无 allegory）
- "用 Python 写个爬虫"（纯代码任务）

### 功能测试

运行脚手架生成测试项目：

```bash
python3 scripts/init-project.py --non-interactive \
  --name test-fables \
  --title "Test Fables" \
  --title-cn "测试寓言" \
  --tagline "Testing" \
  --categories 'test:Test:测试:🧪:desc' \
  --output /tmp/test-fables
```

验证：
- [ ] 目录结构完整（fables/test/、fables/en/、.vitepress/、.github/）
- [ ] package.json 有效（`npm install` 成功）
- [ ] `npm run build` 成功
- [ ] `validate-fables.py` 在空项目上不报错

### 电子书测试

```bash
cd /tmp/test-fables
# 创建一篇测试寓言
cp templates/fable-template.md fables/test/01-test-fable.md
# 修改 frontmatter 和正文
python3 scripts/validate-fables.py
python3 scripts/generate-ebooks.py
# 验证 public/*.pdf 和 public/*.epub 存在
```

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
