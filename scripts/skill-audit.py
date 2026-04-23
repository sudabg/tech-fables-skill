#!/usr/bin/env python3
"""
Skill Self-Audit — Automatic quality check for Hermes/Claude Skills
====================================================================

Usage:
    cd <skill-directory>
    python3 scripts/skill-audit.py

Checks:
1. Frontmatter quality (description triggers, size, forbidden patterns)
2. SKILL.md structural quality (word count, sections, cross-references)
3. references/ and templates/ completeness
4. feedback-log trends (if exists)
5. Generates improvement recommendations + score

Exit codes:
    0 — All critical checks pass
    1 — Critical issues found (skill may not trigger or work correctly)
"""

import os
import re
import sys
from pathlib import Path
from typing import Any


# ─── Config ──────────────────────────────────────────────────────

CRITICAL_MAX_WORDS = 5000
WARN_MAX_WORDS = 3000
DESCRIPTION_MAX_CHARS = 1024
DESCRIPTION_MIN_TRIGGERS = 2


# ─── Helpers ─────────────────────────────────────────────────────

def read_skill_md(skill_dir: Path) -> tuple[dict, str]:
    """Parse SKILL.md frontmatter + body."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {}, ""
    content = skill_md.read_text(encoding="utf-8")
    # Extract frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not fm_match:
        return {}, content
    fm_text, body = fm_match.group(1), fm_match.group(2)
    
    # Parse YAML frontmatter — handle multi-line values (|)
    frontmatter = {}
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' in line and not line.strip().startswith('#'):
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # Check if value is YAML multi-line indicator (| or >)
            if val in ('|', '>'):
                i += 1  # skip to first content line
                value_lines = []
                while i < len(lines):
                    # End when we hit a non-indented line (new key) or end of frontmatter
                    stripped = lines[i].strip()
                    if stripped == '' or (':' in lines[i] and not lines[i].startswith(' ')):
                        break
                    value_lines.append(lines[i])
                    i += 1
                frontmatter[key] = '\n'.join(value_lines)
                continue
            frontmatter[key] = val
        i += 1
    return frontmatter, body


def count_words(text: str) -> int:
    """Approximate word count (handles CJK)."""
    # CJK characters count as words
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    # Latin words
    latin = len(re.findall(r'[a-zA-Z]+', text))
    return cjk + latin


def check_description(frontmatter: dict) -> list[dict]:
    """Check description quality. Returns list of issue dicts."""
    issues = []
    desc = frontmatter.get('description', '')
    
    if not desc:
        issues.append({"level": "critical", "field": "description", 
                       "msg": "description is empty — skill will never trigger automatically"})
        return issues
    
    # Size check
    if len(desc) > DESCRIPTION_MAX_CHARS:
        issues.append({"level": "warn", "field": "description",
                       "msg": f"description is {len(desc)} chars (max {DESCRIPTION_MAX_CHARS}) — may be truncated in system prompt"})
    
    # Trigger phrases check
    trigger_patterns = [
        r'\buse when\b',
        r'\bsays\b',
        r'\basks\b',
        r'\bmentions\b',
        r'\bcreate\b',
        r'\bbuild\b',
        r'\bgenerate\b',
        r'\bscaffold\b',
    ]
    trigger_count = sum(1 for p in trigger_patterns if re.search(p, desc, re.I))
    if trigger_count < DESCRIPTION_MIN_TRIGGERS:
        issues.append({"level": "warn", "field": "description",
                       "msg": f"description has only ~{trigger_count} trigger indicators (aim for {DESCRIPTION_MIN_TRIGGERS}+). Add specific phrases users say"})
    
    # Negative trigger check
    if not re.search(r'\bdo not use\b|\bnot for\b|\bdo NOT\b', desc, re.I):
        issues.append({"level": "info", "field": "description",
                       "msg": "no negative triggers — consider adding 'Do NOT use for...' to reduce over-triggering"})
    
    # Vague check
    vague_words = ['help', 'assist', 'manage', 'process', 'handle']
    vague_found = [w for w in vague_words if re.search(rf'\b{w}\b', desc, re.I)]
    if vague_found and len(desc) < 200:
        issues.append({"level": "warn", "field": "description",
                       "msg": f"description may be too vague (contains: {', '.join(vague_found)}). Be specific about WHAT and WHEN"})
    
    return issues


def check_frontmatter(frontmatter: dict) -> list[dict]:
    """Check frontmatter completeness."""
    issues = []
    required = ['name', 'description']
    recommended = ['version', 'author', 'license']
    
    for field in required:
        if field not in frontmatter or not frontmatter[field]:
            issues.append({"level": "critical", "field": f"frontmatter.{field}",
                           "msg": f"missing required field: {field}"})
    
    for field in recommended:
        if field not in frontmatter or not frontmatter[field]:
            issues.append({"level": "info", "field": f"frontmatter.{field}",
                           "msg": f"missing recommended field: {field}"})
    
    # Name format
    name = frontmatter.get('name', '')
    if name:
        if re.search(r'[A-Z]', name):
            issues.append({"level": "warn", "field": "frontmatter.name",
                           "msg": f"name '{name}' contains capitals — use kebab-case"})
        if re.search(r'[\s_]', name):
            issues.append({"level": "warn", "field": "frontmatter.name",
                           "msg": f"name '{name}' contains spaces/underscores — use kebab-case"})
        if 'claude' in name.lower() or 'anthropic' in name.lower():
            issues.append({"level": "critical", "field": "frontmatter.name",
                           "msg": f"name '{name}' uses reserved prefix 'claude'/'anthropic'"})
    
    # Security: XML tags
    desc = frontmatter.get('description', '')
    if re.search(r'<[^>]+>', desc):
        issues.append({"level": "critical", "field": "frontmatter.description",
                       "msg": "description contains XML-like tags (<>) — forbidden for security"})
    
    return issues


def check_skill_body(body: str) -> list[dict]:
    """Check SKILL.md body structure."""
    issues = []
    words = count_words(body)
    
    if words > CRITICAL_MAX_WORDS:
        issues.append({"level": "critical", "field": "body",
                       "msg": f"SKILL.md body is {words} words (max {CRITICAL_MAX_WORDS}) — will cause context bloat. Move content to references/"})
    elif words > WARN_MAX_WORDS:
        issues.append({"level": "warn", "field": "body",
                       "msg": f"SKILL.md body is {words} words (warn at {WARN_MAX_WORDS}) — consider moving detailed docs to references/"})
    
    # Section checks
    required_sections = ['快速开始', 'quick start', '何时使用', 'when to use']
    has_quickstart = any(s.lower() in body.lower() for s in required_sections)
    if not has_quickstart:
        issues.append({"level": "info", "field": "body",
                       "msg": "no quick start section found — users need fast path to first success"})
    
    # Error handling check
    error_patterns = ['错误处理', 'error handling', 'troubleshoot', '故障排查', '常见问题']
    has_errors = any(p.lower() in body.lower() for p in error_patterns)
    if not has_errors:
        issues.append({"level": "warn", "field": "body",
                       "msg": "no error handling or troubleshooting section — skill will fail silently on edge cases"})
    
    # References check
    if 'references/' in body or 'references' in body.lower():
        issues.append({"level": "info", "field": "body",
                       "msg": "references/ mentioned in body — good progressive disclosure"})
    
    # Examples check
    example_patterns = ['example', '示例', '例子', '## 测试', '## test']
    has_examples = any(p.lower() in body.lower() for p in example_patterns)
    if not has_examples:
        issues.append({"level": "info", "field": "body",
                       "msg": "no examples or test cases — add concrete usage examples"})
    
    return issues


def check_references(skill_dir: Path) -> list[dict]:
    """Check references/ directory."""
    issues = []
    refs_dir = skill_dir / "references"
    
    if not refs_dir.exists():
        issues.append({"level": "info", "field": "references/",
                       "msg": "references/ directory missing — all docs inlined in SKILL.md, causes context bloat"})
        return issues
    
    files = list(refs_dir.iterdir())
    if not files:
        issues.append({"level": "info", "field": "references/",
                       "msg": "references/ is empty — move detailed docs from SKILL.md here"})
    
    for f in files:
        if f.is_file():
            content = f.read_text(encoding="utf-8")
            words = count_words(content)
            if words < 50:
                issues.append({"level": "info", "field": f"references/{f.name}",
                               "msg": f"only {words} words — may be a stub"})
    
    return issues


def check_templates(skill_dir: Path) -> list[dict]:
    """Check templates/ directory."""
    issues = []
    tmpl_dir = skill_dir / "templates"
    
    if not tmpl_dir.exists():
        issues.append({"level": "info", "field": "templates/",
                       "msg": "templates/ directory missing — users need templates for consistent output"})
        return issues
    
    files = list(tmpl_dir.iterdir())
    if not files:
        issues.append({"level": "info", "field": "templates/",
                       "msg": "templates/ is empty — add at least one output template"})
    
    return issues


def check_feedback_log(skill_dir: Path) -> list[dict]:
    """Check feedback-log.md if exists."""
    issues = []
    log_file = skill_dir / "references" / "feedback-log.md"
    
    if not log_file.exists():
        issues.append({"level": "info", "field": "feedback-log",
                       "msg": "feedback-log.md not found — create one to track trigger/execution issues"})
        return issues
    
    content = log_file.read_text(encoding="utf-8")
    
    # Remove HTML comments before matching
    content_no_comments = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Count issues by type
    misses = len(re.findall(r'trigger:\s*miss', content_no_comments))
    overs = len(re.findall(r'trigger:\s*over', content_no_comments))
    exec_errors = len(re.findall(r'exec:\s*error', content_no_comments))
    improvements = len(re.findall(r'improve:', content_no_comments))
    
    if misses > 0:
        issues.append({"level": "warn", "field": "feedback-log",
                       "msg": f"{misses} under-triggering records — expand description with more trigger phrases"})
    
    if overs > 0:
        issues.append({"level": "warn", "field": "feedback-log",
                       "msg": f"{overs} over-triggering records — add negative triggers or narrow description scope"})
    
    if exec_errors > 0:
        issues.append({"level": "warn", "field": "feedback-log",
                       "msg": f"{exec_errors} execution errors — improve instructions or add error handling"})
    
    if misses + overs + exec_errors > 0 and improvements == 0:
        issues.append({"level": "warn", "field": "feedback-log",
                       "msg": f"issues recorded but no improvements made yet — run skill-improve.py to generate fixes"})
    
    return issues


def generate_recommendations(all_issues: list[dict]) -> list[str]:
    """Generate human-readable recommendations."""
    recs = []
    
    critical = [i for i in all_issues if i["level"] == "critical"]
    warns = [i for i in all_issues if i["level"] == "warn"]
    infos = [i for i in all_issues if i["level"] == "info"]
    
    if critical:
        recs.append("🔴 CRITICAL — Fix these before using the skill:")
        for i in critical:
            recs.append(f"   • [{i['field']}] {i['msg']}")
        recs.append("")
    
    if warns:
        recs.append("🟡 WARNINGS — Address for better reliability:")
        for i in warns:
            recs.append(f"   • [{i['field']}] {i['msg']}")
        recs.append("")
    
    if infos:
        recs.append("🔵 SUGGESTIONS — Nice to have:")
        for i in infos:
            recs.append(f"   • [{i['field']}] {i['msg']}")
        recs.append("")
    
    return recs


def calculate_score(all_issues: list[dict], body_words: int) -> int:
    """Calculate a 0-100 health score."""
    score = 100
    
    for i in all_issues:
        if i["level"] == "critical":
            score -= 20
        elif i["level"] == "warn":
            score -= 10
        elif i["level"] == "info":
            score -= 3
    
    # Word count bonus/penalty
    if body_words < 1000:
        score += 5  # Lean skill
    elif body_words > WARN_MAX_WORDS:
        score -= 5
    
    # Progressive disclosure bonus
    has_refs = any(i["field"].startswith("references") and i["level"] == "info" 
                   and "mentioned" in i["msg"] for i in all_issues)
    if has_refs:
        score += 5
    
    return max(0, min(100, score))


def main() -> int:
    skill_dir = Path.cwd()
    
    # Allow running from scripts/ directory
    if skill_dir.name == "scripts":
        skill_dir = skill_dir.parent
    
    print("=" * 60)
    print("Skill Self-Audit")
    print("=" * 60)
    print(f"Skill directory: {skill_dir}")
    print()
    
    # Run all checks
    frontmatter, body = read_skill_md(skill_dir)
    all_issues: list[dict] = []
    
    all_issues.extend(check_frontmatter(frontmatter))
    all_issues.extend(check_description(frontmatter))
    all_issues.extend(check_skill_body(body))
    all_issues.extend(check_references(skill_dir))
    all_issues.extend(check_templates(skill_dir))
    all_issues.extend(check_feedback_log(skill_dir))
    
    # Calculate score
    body_words = count_words(body)
    score = calculate_score(all_issues, body_words)
    
    # Summary
    critical = len([i for i in all_issues if i["level"] == "critical"])
    warns = len([i for i in all_issues if i["level"] == "warn"])
    infos = len([i for i in all_issues if i["level"] == "info"])
    
    print(f"SKILL.md word count: {body_words}")
    print(f"Issues found: {critical} critical, {warns} warnings, {infos} suggestions")
    print()
    
    # Score bar
    bar_len = 40
    filled = int(bar_len * score / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    print(f"Health Score: [{bar}] {score}/100 (Grade {grade})")
    print()
    
    # Recommendations
    if all_issues:
        recs = generate_recommendations(all_issues)
        for r in recs:
            print(r)
    else:
        print("✅ All checks pass. Skill looks great!")
    
    # Quick actions
    print("─" * 60)
    print("Next steps:")
    if critical > 0:
        print("   1. Fix critical issues above")
        print("   2. Run this audit again: python3 scripts/skill-audit.py")
    elif warns > 0:
        print("   1. Address warnings for better trigger reliability")
        print("   2. Run skill-improve.py for automated suggestions")
    else:
        print("   1. Start using the skill and record feedback in references/feedback-log.md")
        print("   2. Run this audit weekly to catch regressions")
    print()
    
    return 1 if critical > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
