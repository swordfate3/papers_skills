from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_workflow_skill_mentions_all_child_skills_and_shared_cli():
    text = read_skill("paper-research-workflow")
    for name in [
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    ]:
        assert name in text
    assert "shared/scripts/paper_workflow.py" in text


def test_ingest_skill_uses_bundled_pdf_references_not_external_skills():
    text = read_skill("paper-ingest-classifier")
    assert ".agents/skills/" not in text
    assert "shared/references/pdf-processing.md" in text
    assert "shared/references/mineru-local.md" in text
    assert "workspace/extracted/<paper-id>/" in text


def test_each_skill_mentions_shared_contracts():
    for name in [
        "paper-research-workflow",
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    ]:
        text = read_skill(name)
        assert "shared/templates" in text
        assert "workspace/knowledge/papers/<paper-id>.json" in text
