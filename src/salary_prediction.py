
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Définir les chemins du projet
ROOT = Path.cwd()
if not (ROOT / "data" / "processed").exists():
    ROOT = ROOT.parent

DATA_DIR = ROOT / "data" / "processed"

# 2. Charger les jeux préparés par la personne 3
train = pd.read_csv(DATA_DIR / "salary_train.csv", index_col="job_id")
test = pd.read_csv(DATA_DIR / "salary_test.csv", index_col="job_id")

# 3. Définir X (variables explicatives) et y (salaire à prédire)
features = ["job_title", "experience_level"]
target = "salary_midpoint_usd"

X_train = train[features].fillna("Inconnu")
y_train = train[target]

X_test = test[features].fillna("Inconnu")
y_test = test[target]

# 4. Préparer l'encodage des variables catégorielles
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categories",
            OneHotEncoder(handle_unknown="ignore"),
            features
        )
    ]
)

# 5. Définir les modèles à comparer
modeles = {
    "Reference moyenne": DummyRegressor(strategy="mean"),
    "Regression Ridge": make_pipeline(
        preprocessor,
        Ridge(alpha=1.0)
    )
}

# 6. Entraîner les modèles et calculer les métriques
resultats = []

for nom, modele in modeles.items():
    if nom == "Reference moyenne":
        modele.fit(X_train[["job_title"]], y_train)
        predictions = modele.predict(X_test[["job_title"]])
    else:
        modele.fit(X_train, y_train)
        predictions = modele.predict(X_test)

    resultats.append({
        "modele": nom,
        "MAE_USD": mean_absolute_error(y_test, predictions),
        "RMSE_USD": mean_squared_error(y_test, predictions) ** 0.5,
        "R2": r2_score(y_test, predictions),
        "n_train": len(X_train),
        "n_test": len(X_test)
    })

# 7. Ajouter la moyenne par métier comme référence simple
moyennes_metier = y_train.groupby(X_train["job_title"]).mean()
moyenne_globale = y_train.mean()

predictions_metier = (
    X_test["job_title"]
    .map(moyennes_metier)
    .fillna(moyenne_globale)
)

resultats.append({
    "modele": "Moyenne par metier",
    "MAE_USD": mean_absolute_error(y_test, predictions_metier),
    "RMSE_USD": mean_squared_error(y_test, predictions_metier) ** 0.5,
    "R2": r2_score(y_test, predictions_metier),
    "n_train": len(X_train),
    "n_test": len(X_test)
})

# 8. Afficher et sauvegarder les résultats
tableau = pd.DataFrame(resultats).set_index("modele")
print(tableau.round(2))

tableau.to_csv(DATA_DIR / "salary_model_results.csv")
print(f"\nRésultats sauvegardés dans : {DATA_DIR / 'salary_model_results.csv'}")
