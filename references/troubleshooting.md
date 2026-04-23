# 故障排查指南

> 常见问题诊断与解决方案。

## Skill 不触发

**症状**：提到"fables"、"寓言"时 skill 没有自动加载

**诊断**：
1. 检查 description 是否包含用户实际会说的触发短语
2. 确认不是 general documentation 请求（有 negative trigger）

**解决**：
- 确认请求包含"storytelling"、"allegory"、"隐喻"等关键词
- 如果只是"搭建文档站点"，不触发是正确的——这是 general docs 场景

## 脚手架生成失败

**症状**：`python3 scripts/init-project.py` 报错

| 错误 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError` | Python 版本过低 | 需要 Python 3.7+ |
| 输入中文乱码 | 终端编码问题 | `export LANG=zh_CN.UTF-8` |
| 目录已存在 | 目标目录不为空 | 选择空目录或 `--output ./new-dir` |

## VitePress 构建失败

**症状**：`npm run build` 报错

### Error: Element is missing end tag

**原因**：泛型语法如 `Option<T>` 被 Vue 编译器当成未闭合 HTML 标签

**解决**：所有尖括号内容必须用反引号包裹：
```markdown
| 没有空指针 | `Option<T>` / 无 null | ... |
```

批量修复：
```python
import re
content = re.sub(r'(?<![`\\])Option<T>(?!`)', '`Option<T>`', content)
```

### Error: Dead links found

**原因**：寓言的"延伸阅读"链接回源知识库，但目标不存在于当前仓库

**解决**：`defineConfig({ ignoreDeadLinks: true })` — 知识库和寓言库是独立仓库，链接本身是合理的。

## 验证脚本失败

### reading_time / word_count 统计错误

**原因**：如果验证脚本用 `---` 作为故事结束标记，而故事与注解之间恰好用 `---` 分隔

**解决**：始终匹配 `## 这则寓言在说什么` 作为故事结束边界：
```python
# ✅ 正确
re.search(r"## 故事\s*\n(.*?)\n## 这则寓言在说什么", body, re.DOTALL)
# ❌ 错误（会匹配故事内部的 ---）
re.search(r"## 故事\s*\n(.*?)\n---\s*\n", body, re.DOTALL)
```

### 新增分类导致批量失败

**原因**：`VALID_CATEGORIES` 集合硬编码

**解决**：脚本应从 `fables/` 目录结构自动推断有效分类，而非硬编码。

## 电子书生成失败

**症状**：`python3 scripts/generate-ebooks.py` 报错

| 错误 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: weasyprint` | 依赖未安装 | `pip install weasyprint ebooklib markdown pyyaml` |
| 字体缺失 | 系统中无 Noto Sans 或 WenQuanYi | 安装 `fonts-noto-cjk` 包 |
| PDF 乱码 | 中文字体未找到 | 检查脚本中的 font-family 配置 |

## VitePress 首页 features 无法点击

**原因**：VitePress home layout 的 `features` 卡片默认不可点击

**解决**：给每个 feature 显式添加 `link` 属性，并创建对应的分类索引页 `fables/{category}/index.md`。

## 电子书部署后 404

**原因**：电子书放在 `site/` 目录

**解决**：VitePress 只自动复制 `public/` 到 `dist/`。所有需要部署的静态资源必须放在 `public/`。

## 测试检查清单

在提交 PR 或发布前运行：

- [ ] `python3 scripts/validate-fables.py` 全量通过
- [ ] `npm run build` 无错误
- [ ] `npm run dev` 本地预览正常
- [ ] 所有分类索引页 `fables/{category}/index.md` 存在
- [ ] 英文版 `fables/en/` 结构与中文版一致
- [ ] 电子书生成成功且文件在 `public/` 中
- [ ] GitHub Actions 部署日志无错误
