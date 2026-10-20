from __future__ import annotations

import pandas as pd
from itertools import combinations
from collections import Counter


SKILL_FAMILIES = {
    "SQL": "SQL",
    "BigQuery": "Entrepôts cloud", "Redshift": "Entrepôts cloud", "Snowflake": "Entrepôts cloud",
    "AWS": "Cloud", "GCP": "Cloud", "Azure": "Cloud",
    "Tableau": "Visualisation / BI", "Power BI": "Visualisation / BI",
    "Data Visualization": "Visualisation / BI", "Excel": "Visualisation / BI",
    "Airflow": "Pipelines / Data Engineering", "dbt": "Pipelines / Data Engineering",
    "ETL": "Pipelines / Data Engineering", "Data Engineering": "Pipelines / Data Engineering",
    "Spark": "Big Data / streaming", "Kafka": "Big Data / streaming",
    "Python": "Python et librairies", "Pandas": "Python et librairies", "NumPy": "Python et librairies",
    "Machine Learning": "Machine Learning / IA", "Deep Learning": "Machine Learning / IA",
    "TensorFlow": "Machine Learning / IA", "PyTorch": "Machine Learning / IA", "NLP": "Machine Learning / IA",
    "Statistics": "Statistiques",
}


def to_skill_families(bridge):
    """Replace each skill by its family; an offer citing two tools of a family keeps one link."""
    unknown = set(bridge.skill.dropna()) - set(SKILL_FAMILIES)
    if unknown:
        raise ValueError(f"Compétences sans famille : {sorted(unknown)}")
    return bridge.assign(skill=bridge.skill.map(SKILL_FAMILIES))[["job_id", "skill"]].drop_duplicates()


def missing_values_report(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a missing-values summary."""
    return pd.DataFrame(
        {
            "missing_count": dataframe.isna().sum(),
            "missing_ratio": dataframe.isna().mean(),
        }
    ).sort_values("missing_count", ascending=False)


def group_percentages(dataframe, groups, category):
    """Count rows and normalize within each group, never across the whole sample."""
    counts = dataframe.groupby(groups + [category], dropna=False).size().rename("nombre_offres")
    result = counts.reset_index()
    result["effectif_groupe"] = result.groupby(groups, dropna=False)["nombre_offres"].transform("sum")
    result["pourcentage"] = result["nombre_offres"] / result["effectif_groupe"] * 100
    return result


def skill_pairs(jobs, bridge):
    """Offer-level support and lift for unordered pairs; duplicate links count once."""
    links = bridge.loc[bridge.job_id.isin(jobs.job_id), ["job_id", "skill"]].dropna().drop_duplicates()
    n = jobs.job_id.nunique()
    singles = links.skill.value_counts()
    counts = Counter()
    for skills in links.groupby("job_id").skill:
        counts.update(combinations(sorted(skills[1]), 2))
    rows = []
    for (a, b), count in counts.items():
        rows.append({"competence_1": a, "competence_2": b,
                     "nombre_offres": count, "support_pct": 100 * count / n,
                     "lift": count * n / (singles[a] * singles[b])})
    return pd.DataFrame(rows, columns=["competence_1", "competence_2", "nombre_offres", "support_pct", "lift"]).sort_values(
        ["nombre_offres", "competence_1", "competence_2"], ascending=[False, True, True])


def skill_prevalence(jobs, bridge, group):
    """Share of all offers in each group requesting each skill, including zeroes."""
    links = bridge[["job_id", "skill"]].dropna().drop_duplicates()
    joined = jobs[["job_id", group]].merge(links, on="job_id", validate="one_to_many")
    counts = pd.crosstab(joined[group], joined.skill)
    totals = jobs.groupby(group).job_id.nunique()
    return counts.reindex(index=totals.index, columns=sorted(links.skill.unique()), fill_value=0).div(totals, axis=0).mul(100)
