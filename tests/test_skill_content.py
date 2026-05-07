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
    assert "scripts/paper_workflow.py" in text
    assert "shared/scripts/paper_workflow.py" not in text


def test_ingest_skill_uses_bundled_pdf_references_not_external_skills():
    text = (ROOT / "skills/paper-research-workflow/references/child-skills/paper-ingest-classifier.md").read_text(
        encoding="utf-8"
    )
    assert ".agents/skills/" not in text
    assert "references/pdf-processing.md" in text
    assert "references/mineru-local.md" in text
    assert "workspace/extracted/<paper-id>/" in text


def test_each_skill_mentions_shared_contracts():
    for relative in [
        "SKILL.md",
        "references/child-skills/paper-ingest-classifier.md",
        "references/child-skills/paper-plain-explainer.md",
        "references/child-skills/paper-expert-reader.md",
        "references/child-skills/paper-code-reproducer.md",
        "references/child-skills/paper-knowledge-base.md",
        "references/child-skills/paper-innovation-miner.md",
    ]:
        text = (ROOT / "skills/paper-research-workflow" / relative).read_text(encoding="utf-8")
        assert "workspace/knowledge/papers/<paper-id>.json" in text


def test_child_workflow_references_are_bundled():
    expected = [
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    ]
    for name in expected:
        assert (ROOT / "skills/paper-research-workflow/references/child-skills" / f"{name}.md").is_file()


def test_workflow_skill_defaults_to_chinese_with_hot_language_switch():
    text = read_skill("paper-research-workflow")
    assert "Default to Chinese" in text
    assert "切换英文" in text
    assert "English mode" in text
    assert "切换中文" in text
    assert "Chinese mode" in text


def test_output_workflows_follow_selected_language():
    for relative in [
        "references/child-skills/paper-plain-explainer.md",
        "references/child-skills/paper-expert-reader.md",
        "references/child-skills/paper-code-reproducer.md",
        "references/child-skills/paper-innovation-miner.md",
    ]:
        text = (ROOT / "skills/paper-research-workflow" / relative).read_text(encoding="utf-8")
        assert "selected language" in text
        assert "default Chinese" in text


def test_skill_docs_no_longer_depend_on_custom_mineru_wrapper():
    for relative in [
        "README.md",
        "skills/paper-research-workflow/SKILL.md",
        "skills/paper-research-workflow/references/mineru-local.md",
        "skills/paper-research-workflow/references/child-skills/paper-ingest-classifier.md",
    ]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "MINERU_TO_MD" not in text
        assert "custom" not in text or "custom or" not in text


def test_skill_docs_describe_bundled_local_docker_mineru_flow():
    for relative in [
        "README.md",
        "skills/paper-research-workflow/SKILL.md",
        "skills/paper-research-workflow/references/mineru-local.md",
        "docs/论文研究技能可视化工作流.md",
    ]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Docker MinerU" in text
        assert "是否要启用" in text or "enable it" in text


def test_reading_workflows_support_iterative_refinement():
    for relative in [
        "references/child-skills/paper-plain-explainer.md",
        "references/child-skills/paper-expert-reader.md",
        "references/child-skills/paper-code-reproducer.md",
    ]:
        text = (ROOT / "skills/paper-research-workflow" / relative).read_text(encoding="utf-8")
        assert "not satisfied" in text
        assert "refine" in text
        assert "overwrite" in text
        assert "new version" in text


def test_innovation_workflow_requires_ranked_append_only_storage():
    text = (ROOT / "skills/paper-research-workflow/references/child-skills/paper-innovation-miner.md").read_text(
        encoding="utf-8"
    )
    assert "score" in text
    assert "rank" in text
    assert "highest to lowest" in text
    assert "must not overwrite" in text
    assert "append" in text


def test_visual_workbench_documents_three_cards_and_innovation_sources():
    for relative in [
        "README.md",
        "skills/paper-research-workflow/SKILL.md",
    ]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "web/" in text
        assert "通俗易懂" in text
        assert "专家阅读" in text
        assert "复现计划" in text
        assert "创新挖掘" in text
        assert "Codex" in text
        assert "Claude Code" in text
