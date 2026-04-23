# 项目结构详解

> 完整目录结构说明与关键设计决策。

## 目录树

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

## 关键目录说明

- `public/` — VitePress 唯一自动部署的静态资源目录。电子书、CNAME、图片放这里。
- `fables/{category}/index.md` — 分类索引页，被首页 feature `link` 指向，含概览表格。
- `fables/en/` — 英文版镜像目录，与中文版完全相同的目录结构。
- `site/` — 脚本中间输出，**不会被 VitePress 部署**，不要放最终资源。

## 双语目录选择

使用 `fables/en/` 镜像目录，而非 `fables/category/xx.en.md` 后缀。原因：
1. VitePress 路由更干净（`/fables/en/security/...` vs `/fables/security/xx.en`）
2. 与 VitePress i18n 结构兼容
3. 批量处理脚本更容易区分语言（检查路径是否包含 `/en/`）

## VitePress 部署要点

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
