"""Reproducible salary experiment with a held-out test set and a mean baseline."""
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder


def evaluate_salary_model(jobs, bridge, test_size=0.2, random_state=42):
    jobs = jobs.copy()
    if jobs.job_id.isna().any() or jobs.job_id.duplicated().any():
        raise ValueError("Chaque offre doit avoir un job_id unique et non manquant.")
    valid = (jobs.salary_min_usd.gt(0) & jobs.salary_max_usd.ge(jobs.salary_min_usd)
             & jobs[["salary_min_usd", "salary_max_usd"]].notna().all(axis=1))
    jobs = jobs.loc[valid].set_index("job_id")
    # Neither salary bounds, application counts nor IDs are explanatory features.
    categories = ["job_title", "country", "experience_level", "remote_option", "employment_type"]
    features = jobs[categories].fillna("Inconnu")
    links = bridge[["job_id", "skill"]].dropna().drop_duplicates()
    skills = pd.crosstab(links.job_id, links.skill).clip(upper=1).add_prefix("skill::")
    features = features.join(skills, how="left").fillna(0)
    target = (jobs.salary_min_usd + jobs.salary_max_usd) / 2
    train_ids, test_ids = train_test_split(jobs.index.to_numpy(), test_size=test_size, random_state=random_state)
    x_train, x_test = features.loc[train_ids], features.loc[test_ids]
    y_train, y_test = target.loc[train_ids], target.loc[test_ids]
    preprocessing = ColumnTransformer([
        ("categories", OneHotEncoder(handle_unknown="ignore"), categories),
    ], remainder="passthrough")
    # One-hot job title + linear regression = mean salary of each job title in the training set.
    title_only = ColumnTransformer([("metier", OneHotEncoder(handle_unknown="ignore"), ["job_title"])])
    models = {
        "Reference moyenne": DummyRegressor(strategy="mean"),
        "Moyenne par metier": make_pipeline(title_only, LinearRegression()),
        "Regression Ridge": make_pipeline(preprocessing, Ridge(alpha=10.0, solver="lsqr")),
    }
    rows = []
    predictions = pd.DataFrame({"job_id": test_ids, "salaire_cible_usd": y_test.to_numpy()})
    for name, model in models.items():
        model.fit(x_train, y_train)
        prediction = model.predict(x_test)
        predictions[name] = prediction
        rows.append({"modele": name, "MAE_USD": mean_absolute_error(y_test, prediction),
                     "RMSE_USD": mean_squared_error(y_test, prediction) ** 0.5,
                     "R2": r2_score(y_test, prediction), "n_train": len(train_ids), "n_test": len(test_ids)})
    return pd.DataFrame(rows).set_index("modele"), predictions


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data = root / "data" / "archive"
    scores, predictions = evaluate_salary_model(pd.read_csv(data / "fact_job_postings.csv"),
                                                pd.read_csv(data / "bridge_job_skills.csv"))
    output = root / "data" / "processed"
    output.mkdir(exist_ok=True)
    scores.to_csv(output / "salary_model_metrics.csv")
    predictions.to_csv(output / "salary_test_predictions.csv", index=False)
    print(scores.to_string())
