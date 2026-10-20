import pandas as pd
import pytest

from src.analysis import group_percentages, skill_pairs, skill_prevalence


def test_percentages_use_each_group_denominator():
    jobs = pd.DataFrame({"level": ["Entry", "Entry", "Senior"], "mode": ["Remote", "Onsite", "Remote"]})
    result = group_percentages(jobs, ["level"], "mode")
    assert result.groupby("level").pourcentage.sum().eq(100).all()
    assert result.loc[result.level.eq("Senior"), "pourcentage"].item() == 100


def test_pairs_deduplicate_links_and_include_offers_without_skills_in_denominator():
    jobs = pd.DataFrame({"job_id": [1, 2, 3, 4]})
    bridge = pd.DataFrame({"job_id": [1, 1, 1, 2, 3, 99], "skill": ["SQL", "Python", "SQL", "SQL", "Python", "SQL"]})
    pair = skill_pairs(jobs, bridge).iloc[0]
    assert pair.nombre_offres == 1
    assert pair.support_pct == 25
    assert pair.lift == pytest.approx(1)


def test_skill_prevalence_counts_offers_not_links():
    jobs = pd.DataFrame({"job_id": [1, 2, 3], "level": ["Entry", "Entry", "Senior"]})
    links = pd.DataFrame({"job_id": [1, 1, 1, 3], "skill": ["SQL", "SQL", "Python", "SQL"]})
    result = skill_prevalence(jobs, links, "level")
    assert result.loc["Entry", "SQL"] == 50
    assert result.loc["Senior", "SQL"] == 100
    assert result.loc["Senior", "Python"] == 0


def test_every_dataset_skill_has_a_family_and_families_count_once_per_offer():
    from pathlib import Path
    from src.analysis import SKILL_FAMILIES, to_skill_families
    skills = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "archive" / "dim_skill.csv").skill
    assert set(skills) <= set(SKILL_FAMILIES)
    links = pd.DataFrame({"job_id": [1, 1, 1], "skill": ["Tableau", "Power BI", "SQL"]})
    assert sorted(to_skill_families(links).skill) == ["SQL", "Visualisation / BI"]
    with pytest.raises(ValueError, match="sans famille"):
        to_skill_families(pd.DataFrame({"job_id": [1], "skill": ["Cobol"]}))
