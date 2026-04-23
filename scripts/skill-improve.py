#!/usr/bin/env python3
"""
Skill Improve — Automated improvement suggestions based on feedback log
=======================================================================

Usage:
    cd <skill-directory>
    python3 scripts/skill-improve.py [--apply]

Reads references/feedback-log.md and current SKILL.md, then generates
targeted improvement recommendations.

Modes:
    --report (default)  Print recommendations only
    --apply             Apply safe changes automatically (descriptions, links)
"""

import argparse
import re
import sys
from pathlib import Path


def read_feedback_log(skill_dir: Path) -> list[dict]:
    """Parse feedback-log.md into structured records."""
    log_file = skill_dir / "references" / "feedback-log.md"
    if not log_file.exists():
        return []
    
    content = log_file.read_text(encoding="utf-8")
    records = []
    
    # Parse trigger records
    for match in re.finditer(
        r'-\s*\[(\d{4}-\d{2}-\d{2}[^\]]*)\]\s+trigger:\s*(miss|over)\s*\|\s*(.*?)\s*(?:\n|$)',
        content, re.MULTILINE
    ):
        records.append({
            "date": match.group(1).strip(),
            "type": f"trigger_{match.group(2)}",
            "context": match.group(3).strip()
        })
    
    # Parse exec records
    for match in re.finditer(
        r'-\s*\[(\d{4}-\d{2}-\d{2}[^\]]*)\]\s+exec:\s*error\s*\|\s*(.*?)\s*(?:\n|$)',
        content, re.MULTILINE
    ):
        records.append({
            "date": match.group(1).strip(),
            "type": "exec_error",
            "context": match.group(2).strip()
        })
    
    return records


def analyze_triggers(records: list[dict]) -> dict:
    """Analyze trigger patterns from feedback."""
    misses = [r for r in records if r["type"] == "trigger_miss"]
    overs = [r for r in records if r["type"] == "trigger_over"]
    
    # Extract keywords from miss contexts
    miss_keywords = {}
    for r in misses:
        words = re.findall(r'[a-zA-Z\u4e00-\u9fff]+', r["context"].lower())
        for w in words:
            if len(w) > 2:
                miss_keywords[w] = miss_keywords.get(w, 0) + 1
    
    # Top missed keywords
    top_misses = sorted(miss_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "miss_count": len(misses),
        "over_count": len(overs),
        "top_missed_keywords": top_misses,
        "miss_contexts": [r["context"] for r in misses],
        "over_contexts": [r["context"] for r in overs],
    }


def generate_description_fix(skill_dir: Path, analysis: dict) -> list[str]:
    """Generate description improvement suggestions."""
    suggestions = []
    
    fm, body = read_skill_md(skill_dir)
    desc = fm.get("description", "")
    
    if analysis["miss_count"] > 0:
        suggestions.append("📝 DESCRIPTION — Add trigger phrases for missed contexts:")
        for ctx in analysis["miss_contexts"][:3]:
            suggestions.append(f"   • User said: \"{ctx}\"")
            # Extract key verb/noun
            keywords = re.findall(r'[a-zA-Z]{3,}', ctx.lower())
            if keywords:
                suggestions.append(f"     → Consider adding: '{', '.join(keywords[-2:])}' to description")
        suggestions.append("")
    
    if analysis["over_count"] > 0:
        suggestions.append("🛡️ DESCRIPTION — Add negative triggers:")
        for ctx in analysis["over_contexts"][:3]:
            suggestions.append(f"   • Skill triggered for: \"{ctx}\"")
            suggestions.append(f"     → Add: 'Do NOT use for {ctx[:50]}...'")
        suggestions.append("")
    
    return suggestions


def generate_instruction_fixes(records: list[dict]) -> list[str]:
    """Generate instruction improvement suggestions from exec errors."""
    suggestions = []
    exec_errors = [r for r in records if r["type"] == "exec_error"]
    
    if not exec_errors:
        return suggestions
    
    suggestions.append("🔧 INSTRUCTIONS — Fix execution issues:")
    
    for r in exec_errors:
        ctx = r["context"]
        suggestions.append(f"   • [{r['date']}] {ctx[:80]}")
        
        # Pattern-based suggestions
        if "not found" in ctx.lower() or "missing" in ctx.lower():
            suggestions.append("     → Add prerequisite check to instructions")
        elif "error" in ctx.lower() or "fail" in ctx.lower():
            suggestions.append("     → Add error handling section for this case")
        elif "unclear" in ctx.lower() or "confused" in ctx.lower():
            suggestions.append("     → Clarify this step with concrete example")
        else:
            suggestions.append("     → Review and rewrite related instruction section")
    
    suggestions.append("")
    return suggestions


def generate_reference_fixes(skill_dir: Path) -> list[str]:
    """Suggest new references based on gaps."""
    suggestions = []
    refs_dir = skill_dir / "references"
    
    expected_refs = {
        "troubleshooting.md": "故障排查速查表",
        "methodology.md": "详细方法论文档",
        "feedback-log.md": "运行时反馈记录",
    }
    
    missing = []
    for fname, purpose in expected_refs.items():
        if not (refs_dir / fname).exists():
            missing.append((fname, purpose))
    
    if missing:
        suggestions.append("📚 REFERENCES — Missing recommended files:")
        for fname, purpose in missing:
            suggestions.append(f"   • {fname} — {purpose}")
        suggestions.append("")
    
    return suggestions


def read_skill_md(skill_dir: Path) -> tuple[dict, str]:
    """Parse SKILL.md frontmatter + body."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {}, ""
    content = skill_md.read_text(encoding="utf-8")
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not fm_match:
        return {}, content
    fm_text, body = fm_match.group(1), fm_match.group(2)
    frontmatter = {}
    for line in fm_text.splitlines():
        if ':' in line and not line.strip().startswith('#'):
            key, val = line.split(':', 1)
            frontmatter[key.strip()] = val.strip()
    return frontmatter, body


def generate_patch(skill_dir: Path, analysis: dict, records: list[dict]) -> str:
    """Generate a unified-diff-style patch for safe changes."""
    patches = []
    fm, body = read_skill_md(skill_dir)
    desc = fm.get("description", "")
    
    # Patch 1: Add missed trigger phrases to description
    if analysis["miss_count"] > 0 and analysis["top_missed_keywords"]:
        new_phrases = ', '.join([k for k, _ in analysis["top_missed_keywords"][:2]])
        if new_phrases and new_phrases not in desc.lower():
            patches.append(f"""
--- a/SKILL.md
+++ b/SKILL.md
@@ -3,6 +3,7 @@
 description: |
   {desc}
+  Also triggers when user mentions: {new_phrases}.
""")
    
    # Patch 2: Add negative triggers if over-triggering
    if analysis["over_count"] > 0:
        over_ctx = analysis["over_contexts"][0] if analysis["over_contexts"] else "general queries"
        if "do not use" not in desc.lower():
            patches.append(f"""
--- a/SKILL.md
+++ b/SKILL.md
@@ -8,6 +8,7 @@
   {desc}
+  Do NOT use for {over_ctx[:60]}.
""")
    
    return "\n".join(patches) if patches else "# No automatic patches generated — manual review recommended"


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill improvement generator")
    parser.add_argument("--apply", action="store_true", help="Apply safe changes automatically")
    args = parser.parse_args()
    
    skill_dir = Path.cwd()
    if skill_dir.name == "scripts":
        skill_dir = skill_dir.parent
    
    print("=" * 60)
    print("Skill Improvement Report")
    print("=" * 60)
    print(f"Skill directory: {skill_dir}")
    print()
    
    # Read data
    records = read_feedback_log(skill_dir)
    
    if not records:
        print("ℹ️  No feedback records found in references/feedback-log.md")
        print()
        print("To start monitoring:")
        print("   1. Use the skill in real conversations")
        print("   2. Record issues in references/feedback-log.md")
        print("   3. Run this script again for targeted improvements")
        print()
        # Still run reference check
        ref_suggestions = generate_reference_fixes(skill_dir)
        for s in ref_suggestions:
            print(s)
        return 0
    
    # Analyze
    analysis = analyze_triggers(records)
    
    print(f"Feedback records: {len(records)}")
    print(f"  Under-triggering (missed): {analysis['miss_count']}")
    print(f"  Over-triggering:           {analysis['over_count']}")
    print(f"  Execution errors:          {len([r for r in records if r['type'] == 'exec_error'])}")
    print()
    
    # Generate suggestions
    all_suggestions = []
    all_suggestions.extend(generate_description_fix(skill_dir, analysis))
    all_suggestions.extend(generate_instruction_fixes(records))
    all_suggestions.extend(generate_reference_fixes(skill_dir))
    
    if all_suggestions:
        print("RECOMMENDATIONS")
        print("─" * 60)
        for s in all_suggestions:
            print(s)
    else:
        print("✅ No improvements needed based on current feedback")
    
    # Generate patch
    print()
    print("POTENTIAL PATCHES")
    print("─" * 60)
    patch = generate_patch(skill_dir, analysis, records)
    print(patch)
    
    if args.apply:
        print()
        print("⚠️  --apply not yet implemented — review patches manually")
        print("   Future versions will apply safe text substitutions automatically")
    
    print()
    print("─" * 60)
    print("Next steps:")
    print("   1. Review recommendations above")
    print("   2. Apply changes to SKILL.md manually")
    print("   3. Record improvement in feedback-log.md under '## 改进记录'")
    print("   4. Re-run skill-audit.py to verify score improvement")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
