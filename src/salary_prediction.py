"""Expériences salariales reproductibles en USD, sans entraînement lors de l'import."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

CORE_FEATURES = ["job_title", "experience_level", "country"]
EXTENDED_FEATURES = ["job_title", "country", "experience_level", "remote_option", "employment_type"]


def evaluate_salary_model(jobs, bridge=None, test_size=0.2, random_state=42,
                          feature_columns=None, include_skills=True,
                          ridge_alpha=10.0, ridge_solver="lsqr", return_split=False):
    """Comparer moyenne globale, moyenne par métier et Ridge sur le même test.

    Le défaut reproduit l'ancienne expérience enrichie (alpha=10, solveur lsqr).
    La configuration principale du projet est passée explicitement par le notebook.
    Aucun résultat n'est exporté implicitement. Les IDs restent hors des variables X.
    """
    jobs = jobs.copy()
    if jobs.job_id.isna().any() or jobs.job_id.duplicated().any():
        raise ValueError("Chaque offre doit avoir un job_id unique et non manquant.")
    feature_columns = list(EXTENDED_FEATURES if feature_columns is None else feature_columns)
    if (not feature_columns or len(set(feature_columns)) != len(feature_columns)
            or not set(feature_columns).issubset(EXTENDED_FEATURES)):
        raise ValueError("Variables explicatives autorisées : métier, pays, expérience, mode et contrat ; aucun salaire ni identifiant.")
    required = set(feature_columns) | {"job_id", "job_title", "salary_min_usd", "salary_max_usd"}
    if missing := required - set(jobs.columns):
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")
    for column in ["salary_min_usd", "salary_max_usd"]:
        jobs[column] = pd.to_numeric(jobs[column], errors="coerce")
    valid = (np.isfinite(jobs.salary_min_usd) & np.isfinite(jobs.salary_max_usd)
             & jobs.salary_min_usd.gt(0) & jobs.salary_max_usd.ge(jobs.salary_min_usd))
    removed = int((~valid).sum())
    jobs = jobs.loc[valid].set_index("job_id")
    if len(jobs) < 3:
        raise ValueError("Au moins trois offres avec un salaire valide sont nécessaires.")
    features = jobs[feature_columns].fillna("Inconnu").astype(str)
    target = ((jobs.salary_min_usd + jobs.salary_max_usd) / 2).rename("salary_midpoint_usd")
    train_ids, test_ids = train_test_split(
        jobs.index.to_numpy(), test_size=test_size, random_state=random_state)

    if include_skills:
        if bridge is None:
            raise ValueError("La table des compétences est nécessaire si include_skills=True.")
        links = bridge.loc[bridge.job_id.isin(jobs.index), ["job_id", "skill"]].dropna().drop_duplicates()
        # Les compétences inconnues de l'entraînement ne créent pas de colonne apprise sur le test.
        vocabulary = sorted(links.loc[links.job_id.isin(train_ids), "skill"].unique())
        skills = pd.crosstab(links.job_id, links.skill).reindex(columns=vocabulary, fill_value=0)
        skills = skills.clip(upper=1).add_prefix("skill::").reindex(jobs.index, fill_value=0)
        features = features.join(skills, how="left").fillna(0)

    x_train, x_test = features.loc[train_ids], features.loc[test_ids]
    y_train, y_test = target.loc[train_ids], target.loc[test_ids]
    preprocess = ColumnTransformer([
        ("categories", OneHotEncoder(handle_unknown="ignore"), feature_columns),
    ], remainder="passthrough")
    dummy = DummyRegressor(strategy="mean").fit(x_train, y_train)
    ridge = make_pipeline(preprocess, Ridge(alpha=ridge_alpha, solver=ridge_solver))
    ridge.fit(x_train, y_train)
    titles = jobs.job_title.fillna("Inconnu").astype(str)
    title_means = y_train.groupby(titles.loc[train_ids]).mean()
    prediction_values = {
        "Reference moyenne": dummy.predict(x_test),
        "Moyenne par metier": titles.loc[test_ids].map(title_means).fillna(y_train.mean()).to_numpy(),
        "Regression Ridge": ridge.predict(x_test),
    }
    predictions = pd.DataFrame({"job_id": test_ids, "salaire_cible_usd": y_test.to_numpy()})
    rows = []
    for name, predicted in prediction_values.items():
        predictions[name] = predicted
        rows.append({
            "modele": name, "MAE_USD": mean_absolute_error(y_test, predicted),
            "RMSE_USD": mean_squared_error(y_test, predicted) ** 0.5,
            "R2": r2_score(y_test, predicted), "n_train": len(train_ids), "n_test": len(test_ids),
        })
    scores = pd.DataFrame(rows).set_index("modele")
    if return_split:
        return scores, predictions, {
            "X_train": x_train, "X_test": x_test, "y_train": y_train, "y_test": y_test,
            "excluded_salary_rows": removed, "ridge": ridge,
        }
    return scores, predictions


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Estimer le milieu des fourchettes salariales en USD.")
    parser.add_argument("--export", type=Path, help="Dossier facultatif pour les scores et prédictions.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    jobs = pd.read_csv(root / "data/raw/fact_job_postings.csv")
    scores, predictions = evaluate_salary_model(
        jobs, feature_columns=CORE_FEATURES, include_skills=False)
    number_fr = lambda value: f"{value:,.2f}".replace(",", " ").replace(".", ",")
    print(scores.to_string(
        float_format=number_fr,
        formatters={"R2": lambda value: f"{value:.3f}".replace(".", ",")},
    ))
    if args.export is not None:
        args.export.mkdir(parents=True, exist_ok=True)
        scores.to_csv(args.export / "salary_model_metrics.csv")
        predictions.to_csv(args.export / "salary_test_predictions.csv", index=False)


if __name__ == "__main__":
    main()
