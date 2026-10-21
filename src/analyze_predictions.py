
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error

ROOT_DIR = Path(__file__).resolve().parents[1]
PREDICTIONS_PATH = ROOT_DIR / "reports" / "salary_test_predictions.csv"

predictions = pd.read_csv(PREDICTIONS_PATH)

# Calculer l'erreur absolue de chaque modèle
for model_name in ["Moyenne par metier", "Regression Ridge"]:
    predictions[f"erreur_{model_name}"] = (
        predictions["salaire_cible_usd"] - predictions[model_name]
    ).abs()

# Résumer les erreurs
print("\n=== Erreurs sur le jeu de test ===")

for model_name in ["Moyenne par metier", "Regression Ridge"]:
    mae = mean_absolute_error(
        predictions["salaire_cible_usd"],
        predictions[model_name]
    )
    print(f"{model_name} : MAE = {mae:,.2f} USD")

# Afficher les 10 plus grosses erreurs du Ridge
print("\n=== Les 10 plus grosses erreurs du Ridge ===")

worst_predictions = predictions.nlargest(
    10, "erreur_Regression Ridge"
)

print(
    worst_predictions[
        ["job_id", "salaire_cible_usd", "Regression Ridge",
         "erreur_Regression Ridge"]
    ].to_string(index=False)
)

# Retrouver les caractéristiques des offres qui ont les plus grosses erreurs
JOBS_PATH = ROOT_DIR / "data" / "raw" / "fact_job_postings.csv"

jobs = pd.read_csv(JOBS_PATH)

worst_ids = worst_predictions["job_id"]

details = jobs.loc[
    jobs["job_id"].isin(worst_ids),
    [
        "job_id",
        "job_title",
        "experience_level",
        "country",
        "salary_min_usd",
        "salary_max_usd",
    ],
]

print("\n=== Profils des offres les plus difficiles à prédire ===")
print(details.to_string(index=False))


# Vérifier la répartition des salaires dans le jeu de test
print("\n=== Statistiques des salaires réels ===")
print(predictions["salaire_cible_usd"].describe())

# Vérifier les salaires par métier et niveau d'expérience
print("\n=== Salaires moyens par métier et expérience ===")
salary_stats = jobs.groupby(
    ["job_title", "experience_level"]
).agg(
    salaire_min_moyen=("salary_min_usd", "mean"),
    salaire_max_moyen=("salary_max_usd", "mean"),
    nombre_offres=("job_id", "count"),
).round(2)

print(salary_stats.to_string())

# Comparer les salaires moyens selon le pays
print("\n=== Salaires moyens par pays ===")

country_stats = jobs.groupby("country").agg(
    salaire_min_moyen=("salary_min_usd", "mean"),
    salaire_max_moyen=("salary_max_usd", "mean"),
    nombre_offres=("job_id", "count"),
).round(2)

print(country_stats.sort_values(
    "salaire_min_moyen",
    ascending=False
).to_string())

