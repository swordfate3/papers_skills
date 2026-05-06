import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_paper_memory_schema_requires_core_fields():
    schema = load_json("skills/paper-research-workflow/schemas/paper-memory.schema.json")
    assert schema["type"] == "object"
    for field in [
        "paper_id",
        "title",
        "authors",
        "year",
        "source",
        "classification",
        "core",
        "evidence",
        "critique",
        "reproduction",
        "innovation",
        "artifacts",
        "status",
    ]:
        assert field in schema["required"]


def test_paper_memory_template_matches_required_shape():
    template = load_json("skills/paper-research-workflow/templates/paper-memory.json")
    for field in [
        "paper_id",
        "title",
        "authors",
        "year",
        "source",
        "classification",
        "core",
        "evidence",
        "critique",
        "reproduction",
        "innovation",
        "artifacts",
        "status",
    ]:
        assert field in template
    assert template["reproduction"]["difficulty"] == "unknown"
    assert template["status"]["kb_validated"] is False


def test_markdown_templates_have_frontmatter_and_required_sections():
    required = {
        "paper-card.md": ["一句话总结", "核心问题", "方法", "证据", "局限性", "术语对照"],
        "expert-reading.md": ["专家结论", "技术机制", "证据质量", "局限与失败模式", "创新启发"],
        "reproduction-plan.md": ["复现目标", "最小可行复现", "依赖与数据", "实验与指标", "风险"],
        "innovation-brief.md": ["来源论文", "创新假设", "最小实验", "风险与证伪", "创新评分", "排序说明"],
    }
    for filename, sections in required.items():
        text = (ROOT / "skills/paper-research-workflow/templates" / filename).read_text(encoding="utf-8")
        assert text.startswith("---\n")
        for section in sections:
            assert f"## {section}" in text
