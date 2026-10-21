from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="JobMatch | Modèles",
    page_icon="🤖",
    layout="wide"
)

ROOT = Path(__file__).resolve().parents[2]

st.title("🤖 Comparaison des modèles")
st.write(
    "Évaluation des performances des modèles "
    "de prédiction salariale de JobMatch."
)

@st.cache_data
def charger_metriques():
    chemin = (
        ROOT / "data" / "processed"
        / "salary_model_metrics.csv"
    )
    return pd.read_csv(chemin)

try:
    resultats = charger_metriques()
except FileNotFoundError:
    st.warning(
        "Les métriques ne sont pas encore exportées. "
        "Exécutez le script de prédiction avec --export."
    )
    st.stop()

# Vérifier les colonnes attendues
colonnes = {"modele", "MAE_USD", "RMSE_USD", "R2"}

if not colonnes.issubset(resultats.columns):
    st.error("Le fichier des métriques est incomplet.")
    st.stop()

st.subheader("📋 Résultats des modèles")

st.dataframe(
    resultats,
    use_container_width=True,
    hide_index=True
)

st.divider()

# Comparaison des métriques
st.subheader("📊 Comparaison graphique")

metrique = st.selectbox(
    "Choisir une métrique",
    ["MAE_USD", "RMSE_USD", "R2"]
)

graphique = resultats.set_index("modele")[[metrique]]

st.bar_chart(graphique)

# Identifier le meilleur modèle selon la métrique
if metrique == "R2":
    meilleur = resultats.loc[resultats[metrique].idxmax()]
else:
    meilleur = resultats.loc[resultats[metrique].idxmin()]

st.success(
    f"Meilleur modèle selon {metrique} : "
    f"{meilleur['modele']}"
)

st.divider()

st.subheader("📖 Comprendre les métriques")

with st.expander("MAE — Mean Absolute Error"):
    st.write(
        "La MAE mesure l'erreur absolue moyenne entre "
        "les salaires prédits et les salaires attendus. "
        "Plus elle est faible, meilleur est le résultat."
    )

with st.expander("RMSE — Root Mean Squared Error"):
    st.write(
        "La RMSE pénalise davantage les grandes erreurs "
        "de prédiction. Plus elle est faible, mieux c'est."
    )

with st.expander("R² — Coefficient de détermination"):
    st.write(
        "Le R² mesure la qualité de l'ajustement "
        "par rapport à une prédiction fondée sur la moyenne. "
        "Plus il est proche de 1, meilleur est l'ajustement."
    )

st.info(
    "Ces performances sont mesurées sur le jeu de test "
    "interne. Elles ne garantissent pas la même précision "
    "sur de nouvelles offres réelles."
)