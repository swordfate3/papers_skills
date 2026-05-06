from shared.scripts.classify_paper import classify_text, infer_year
from shared.scripts.kb_query import rank_related_papers


def test_infer_year_prefers_recent_paper_year():
    text = "Published at NeurIPS 2024. References include work from 2018 and 2020."
    assert infer_year(text) == 2024


def test_classify_machine_learning_paper():
    result = classify_text("We train a transformer neural network on ImageNet and compare against baselines.")
    assert "machine-learning" in result["domains"]
    assert "transformer" in result["keywords"]


def test_classify_systems_paper():
    result = classify_text("We design a distributed scheduler that improves latency and throughput in a cluster.")
    assert "systems" in result["domains"]


def test_classify_program_synthesis_paper():
    result = classify_text(
        "Playgol learns logic programs through inductive logic programming, program synthesis, "
        "symbolic reasoning, and reusable background knowledge."
    )
    assert "software-engineering" in result["domains"]
    assert "program-synthesis" in result["keywords"]


def test_rank_related_papers_scores_shared_fields():
    target = {
        "paper_id": "target",
        "classification": {
            "domains": ["machine-learning"],
            "tasks": ["classification"],
            "keywords": ["transformer"],
        },
        "evidence": {"datasets": ["ImageNet"], "metrics": ["accuracy"]},
        "critique": {"limitations": ["high compute"]},
    }
    candidates = [
        {
            "paper_id": "close",
            "classification": {
                "domains": ["machine-learning"],
                "tasks": ["classification"],
                "keywords": ["transformer"],
            },
            "evidence": {"datasets": ["ImageNet"], "metrics": ["accuracy"]},
            "critique": {"limitations": []},
        },
        {
            "paper_id": "far",
            "classification": {
                "domains": ["security"],
                "tasks": ["fuzzing"],
                "keywords": ["symbolic-execution"],
            },
            "evidence": {"datasets": [], "metrics": []},
            "critique": {"limitations": []},
        },
    ]
    ranked = rank_related_papers(target, candidates)
    assert ranked[0]["paper_id"] == "close"
    assert ranked[0]["score"] > ranked[1]["score"]
