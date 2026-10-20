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
    skills = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "raw" / "dim_skill.csv").skill
    assert set(skills) <= set(SKILL_FAMILIES)
    links = pd.DataFrame({"job_id": [1, 1, 1], "skill": ["Tableau", "Power BI", "SQL"]})
    assert sorted(to_skill_families(links).skill) == ["SQL", "Visualisation / BI"]
    with pytest.raises(ValueError, match="sans famille"):
        to_skill_families(pd.DataFrame({"job_id": [1], "skill": ["Cobol"]}))


def test_currency_conversion_preserves_sources_and_numeric_statistics():
    from src.analysis import USD_TO_EUR, add_salary_columns, salary_summary
    jobs = pd.DataFrame({"job_id": [1, 2, 3], "level": ["Entry"] * 3,
                         "salary_min_usd": [100, 200, 300], "salary_max_usd": [200, 300, 400]})
    original = jobs.copy(deep=True)
    enriched = add_salary_columns(jobs)
    pd.testing.assert_frame_equal(jobs, original)
    assert enriched.salary_mid_eur.tolist() == pytest.approx([150 * USD_TO_EUR, 250 * USD_TO_EUR, 350 * USD_TO_EUR])
    summary = salary_summary(enriched, "level").loc["Entry"]
    assert summary.nombre_offres == 3
    assert summary.mediane_eur == pytest.approx(250 * USD_TO_EUR)
    assert summary.q1_eur == pytest.approx(200 * USD_TO_EUR)


def test_association_coefficients_and_currency_invariance():
    from src.analysis import cramers_v, eta_squared, USD_TO_EUR
    category = pd.Series(["A", "A", "B", "B"])
    salary = pd.Series([10.0, 20.0, 40.0, 50.0])
    assert cramers_v(category, category) == pytest.approx(1)
    assert eta_squared(category, salary) == pytest.approx(eta_squared(category, salary * USD_TO_EUR))
    assert 0 < eta_squared(category, salary) < 1
