"""Fonctions communes de l'EDA ; les données sources restent inchangées."""
from collections import Counter
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

# Convention de présentation du projet, indicative et non un cours de change actuel.
USD_TO_EUR = 0.92

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


def add_salary_columns(jobs):
    """Ajouter le milieu en USD et sa présentation EUR, sans arrondir les calculs."""
    result = jobs.copy()
    result["salary_mid_usd"] = (result.salary_min_usd + result.salary_max_usd) / 2
    for part in ("min", "max", "mid"):
        result[f"salary_{part}_eur"] = result[f"salary_{part}_usd"] * USD_TO_EUR
    return result


def salary_summary(jobs, groups):
    """Statistiques des milieux de fourchettes, présentées en euros."""
    return jobs.groupby(groups, observed=True).agg(
        nombre_offres=("job_id", "nunique"),
        minimum_eur=("salary_mid_eur", "min"),
        moyenne_eur=("salary_mid_eur", "mean"),
        q1_eur=("salary_mid_eur", lambda s: s.quantile(0.25)),
        mediane_eur=("salary_mid_eur", "median"),
        q3_eur=("salary_mid_eur", lambda s: s.quantile(0.75)),
        maximum_eur=("salary_mid_eur", "max"),
        ecart_type_eur=("salary_mid_eur", "std"),
    )


def to_skill_families(bridge):
    """Une famille est comptée une seule fois par offre, même avec plusieurs outils."""
    unknown = set(bridge.skill.dropna()) - set(SKILL_FAMILIES)
    if unknown:
        raise ValueError(f"Compétences sans famille : {sorted(unknown)}")
    return (bridge.dropna(subset=["job_id", "skill"])
            .assign(skill=lambda d: d.skill.map(SKILL_FAMILIES))
            [["job_id", "skill"]].drop_duplicates())


def group_percentages(dataframe, groups, category):
    """Effectifs et pourcentages au sein du groupe ; entrée : une ligne par offre."""
    counts = dataframe.groupby(groups + [category], dropna=False, observed=True).size()
    result = counts.rename("nombre_offres").reset_index()
    result["effectif_groupe"] = result.groupby(groups, dropna=False, observed=True)["nombre_offres"].transform("sum")
    result["pourcentage"] = result.nombre_offres / result.effectif_groupe * 100
    return result


def _check_job_ids(jobs):
    if jobs.job_id.isna().any() or jobs.job_id.duplicated().any():
        raise ValueError("Chaque offre doit avoir un job_id unique et non manquant.")


def skill_pairs(jobs, bridge):
    """Paires non orientées ; support et lift utilisent toutes les offres distinctes."""
    _check_job_ids(jobs)
    columns = ["competence_1", "competence_2", "nombre_offres", "support_pct", "lift"]
    links = bridge.loc[bridge.job_id.isin(jobs.job_id), ["job_id", "skill"]].dropna().drop_duplicates()
    n = jobs.job_id.nunique()
    singles = links.skill.value_counts()
    counts = Counter()
    for _, skills in links.groupby("job_id").skill:
        counts.update(combinations(sorted(skills), 2))
    rows = [
        {"competence_1": a, "competence_2": b, "nombre_offres": count,
         "support_pct": 100 * count / n, "lift": count * n / (singles[a] * singles[b])}
        for (a, b), count in counts.items()
    ]
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["nombre_offres", "competence_1", "competence_2"], ascending=[False, True, True])


def skill_prevalence(jobs, bridge, group):
    """Pourcentage des offres du groupe demandant chaque compétence (zéros inclus)."""
    _check_job_ids(jobs)
    links = bridge[["job_id", "skill"]].dropna().drop_duplicates()
    joined = jobs[["job_id", group]].merge(links, on="job_id", validate="one_to_many")
    counts = pd.crosstab(joined[group], joined.skill)
    totals = jobs.groupby(group, observed=True).job_id.nunique()
    return counts.reindex(index=totals.index, columns=sorted(links.skill.unique()), fill_value=0).div(totals, axis=0).mul(100)


def cramers_v(a, b):
    """V de Cramér non corrigé du biais, sans correction de continuité de Yates."""
    table = pd.crosstab(a, b)
    degrees = min(table.shape) - 1
    if degrees <= 0 or table.to_numpy().sum() == 0:
        return np.nan
    chi2 = chi2_contingency(table, correction=False)[0]
    return np.sqrt(chi2 / (table.to_numpy().sum() * degrees))


def eta_squared(category, values):
    """Part de variance associée aux différences de moyennes entre groupes."""
    data = pd.DataFrame({"category": category, "value": values}).dropna()
    denominator = ((data.value - data.value.mean()) ** 2).sum()
    if denominator == 0:
        return np.nan
    means = data.groupby("category", observed=True).value.transform("mean")
    return ((means - data.value.mean()) ** 2).sum() / denominator
