# Tech Fables Skill

> One-command scaffolding for open-source "Tech Fables" projects.

Transform any technical domain into an allegorical-story education site. This skill provides:

- **Interactive project scaffolder** — answer a few prompts, get a complete bilingual VitePress site
- **E-book generator** — professional PDF + EPUB with covers, TOCs, and metadata cards
- **Validation & linting** — structural compliance checks + auto-metadata injection
- **Writing templates** — narrative contract + standardized frontmatter

## Quick Start

```bash
git clone https://github.com/sudabg/tech-fables-skill.git
cd tech-fables-skill

# Interactive mode
python3 scripts/init-project.py

# Or non-interactive / CI mode
python3 scripts/init-project.py \
  --non-interactive \
  --name "distributed-fables" \
  --title "Distributed Fables" \
  --title-cn "分布式寓言" \
  --tagline "用寓言理解分布式系统的核心概念" \
  --categories "consensus:Consensus:共识算法:⚖️:分布式一致性|replication:Replication:数据复制:📦:多节点同步" \
  --output .
```

Then:

```bash
cd <your-project>
npm install
npm run dev
```

## What's Included

Every generated project comes with:

| Asset | Purpose |
|-------|---------|
| `fables/{category}/` + `fables/en/` | Bilingual content directories |
| `.vitepress/config.mjs` | Bilingual sidebar routing |
| `scripts/validate-fables.py` | Auto-update word counts, validate structure |
| `scripts/generate-ebooks.py` | PDF/EPUB generation |
| `templates/fable-template.md` | Standardized writing template |
| `CONTRIBUTING.md` | Narrative contract & quality standards |
| `.github/workflows/deploy.yml` | Auto-deploy to GitHub Pages |

## Narrative Contract

All fables in a Tech Fables project must follow:

1. **Delayed revelation** — no technical terms in the first 1/3 of the story
2. **Character motivation** — blind spots map to common misconceptions
3. **Conflict cost** — wrong decisions have perceivable consequences
4. **Complete mapping** — every story element has a technical counterpart
5. **Conceptual accuracy** — simplification allowed, distortion forbidden

## Dependencies for E-books

```bash
pip install weasyprint ebooklib markdown pyyaml
```

## Projects Built With This Skill

- [LLM Fables](https://github.com/sudabg/llm-fables) — 28 fables covering Attention, Scaling Laws, MoE, RLHF, etc.

## License

MIT
