from pathlib import Path

import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="JobMatch | Dashboard",
    page_icon="💼",
    layout="wide"
)

# Chemin vers le dossier principal du projet
ROOT = Path(__file__).resolve().parents[1]

# Fonction de chargement des données
@st.cache_data
def charger_donnees():
    chemin = ROOT / "data" / "raw" / "fact_job_postings.csv"
    return pd.read_csv(chemin)

# Chargement du dataset
try:
    df = charger_donnees()
except FileNotFoundError:
    st.error("Le fichier fact_job_postings.csv est introuvable.")
    st.stop()

# Calcul du salaire médian de chaque offre
df["salary_midpoint_usd"] = (
    df["salary_min_usd"] + df["salary_max_usd"]
) / 2

# En-tête
st.title("💼 JobMatch")
st.subheader("Tableau de bord du marché de l'emploi")

st.write(
    "Explorez les offres d'emploi, analysez les salaires "
    "et découvrez les performances de nos modèles de Machine Learning."
)

st.divider()

# Calcul des indicateurs
nombre_offres = len(df)
nombre_metiers = df["job_title"].nunique()
nombre_pays = df["country"].nunique()
salaire_median = df["salary_midpoint_usd"].median()

# Affichage des indicateurs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Offres d'emploi", f"{nombre_offres:,}")
col2.metric("Métiers différents", nombre_metiers)
col3.metric("Pays représentés", nombre_pays)
col4.metric("Salaire médian annuel", f"${salaire_median:,.0f}")