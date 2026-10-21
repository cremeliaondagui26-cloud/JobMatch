
"""Entraînement, sauvegarde et utilisation du modèle de prédiction salariale."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Chemins du projet
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "raw" / "fact_job_postings.csv"
MODEL_DIR = ROOT_DIR / "models"
MODEL_PATH = MODEL_DIR / "salary_ridge.joblib"

# Variables utilisées pour prédire le salaire
FEATURES = ["job_title", "experience_level", "country"]


def train_model():
    """Entraîne le modèle Ridge et sauvegarde toute la pipeline."""

    # Charger les offres d'emploi
    jobs = pd.read_csv(DATA_PATH)

    # Vérifier les colonnes nécessaires
    required = FEATURES + ["salary_min_usd", "salary_max_usd"]
    missing = set(required) - set(jobs.columns)

    if missing:
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")

    # Convertir les salaires en valeurs numériques
    jobs["salary_min_usd"] = pd.to_numeric(
        jobs["salary_min_usd"], errors="coerce"
    )
    jobs["salary_max_usd"] = pd.to_numeric(
        jobs["salary_max_usd"], errors="coerce"
    )

    # Garder uniquement les offres avec des salaires valides
    valid = (
        np.isfinite(jobs["salary_min_usd"])
        & np.isfinite(jobs["salary_max_usd"])
        & (jobs["salary_min_usd"] > 0)
        & (jobs["salary_max_usd"] >= jobs["salary_min_usd"])
    )

    jobs = jobs.loc[valid].copy()

    if jobs.empty:
        raise ValueError("Aucune offre avec un salaire valide.")

    # Cible : milieu de la fourchette salariale
    y = (
        jobs["salary_min_usd"] + jobs["salary_max_usd"]
    ) / 2

    # Préparer les variables explicatives
    X = jobs[FEATURES].fillna("Inconnu").astype(str)

    # Transformer les catégories en variables numériques
    preprocessing = ColumnTransformer(
        transformers=[
            (
                "categories",
                OneHotEncoder(handle_unknown="ignore"),
                FEATURES,
            )
        ]
    )

    # Pipeline complète : prétraitement + régression Ridge
    model = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("regression", Ridge(alpha=10.0, solver="lsqr")),
        ]
    )

    # Entraîner le modèle
    model.fit(X, y)

    # Sauvegarder le modèle entraîné
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Modèle sauvegardé dans : {MODEL_PATH}")
    print(f"Nombre d'offres utilisées : {len(jobs)}")

    return model


def load_model():
    """Charge le modèle sauvegardé ou l'entraîne s'il n'existe pas."""

    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)

    return train_model()


def predict_salary(job_title, experience_level, country):
    """Retourne le salaire estimé en USD pour une offre donnée."""

    model = load_model()

    # Construire les données attendues par le modèle
    offer = pd.DataFrame(
        [
            {
                "job_title": job_title,
                "experience_level": experience_level,
                "country": country,
            }
        ]
    )

    # Appliquer la même pipeline que pendant l'entraînement
    prediction = model.predict(offer)[0]

    return max(0.0, float(prediction))


if __name__ == "__main__":
    model = train_model()

    example = predict_salary(
        job_title="Data Analyst",
        experience_level="Entry",
        country="United States",
    )

    print(f"Salaire estimé : {example:,.2f} USD")
