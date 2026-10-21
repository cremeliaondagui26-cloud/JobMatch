from pathlib import Path

import pandas as pd
import streamlit as st

from styles import apply_theme, render_footer, render_header

# Configuration de la page
st.set_page_config(
    page_title="JobMatch | Dashboard",
    page_icon="💼",
    layout="wide"
)
apply_theme()
render_header("home")

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

# Calcul des indicateurs
nombre_offres = len(df)
nombre_metiers = df["job_title"].nunique()
nombre_pays = df["country"].nunique()
salaire_median = df["salary_midpoint_usd"].median()

# En-tête
st.markdown(
    f"""
    <section class="jm-home-hero">
        <div>
            <span class="jm-eyebrow">Emploi · Données · Intelligence artificielle</span>
            <h1>Comprenez le marché.<br>Choisissez mieux votre prochain emploi.</h1>
            <p class="jm-lead">Explorez les offres, comparez les salaires et obtenez une estimation personnalisée grâce aux données de JobMatch.</p>
        </div>
        <div class="jm-market-card">
            <div class="jm-market-head">
                <div class="jm-market-kicker">Aperçu du marché</div>
                <div class="jm-market-title">Les données de vos offres analysées</div>
            </div>
            <div class="jm-market-body">
                <div>
                    <div class="jm-market-label">Salaire médian observé</div>
                    <div class="jm-market-value">${salaire_median:,.0f}</div>
                </div>
                <div class="jm-chart">
                    <i style="height: 40%"></i><i style="height: 53%"></i>
                    <i style="height: 48%"></i><i style="height: 68%"></i>
                    <i style="height: 79%"></i><i style="height: 94%"></i>
                </div>
            </div>
            <div class="jm-market-stats">
                <div class="jm-market-stat"><small>Offres analysées</small><strong>{nombre_offres:,}</strong></div>
                <div class="jm-market-stat"><small>Métiers</small><strong>{nombre_metiers}</strong></div>
                <div class="jm-market-stat"><small>Pays</small><strong>{nombre_pays}</strong></div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Affichage des indicateurs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Offres d'emploi", f"{nombre_offres:,}")
col2.metric("Métiers différents", nombre_metiers)
col3.metric("Pays représentés", nombre_pays)
col4.metric("Salaire médian annuel", f"${salaire_median:,.0f}")

st.markdown('<section class="jm-panel"><h2>Les outils JobMatch</h2><p class="jm-muted">Des informations claires pour mieux comprendre le marché et préparer vos décisions.</p></section>', unsafe_allow_html=True)

feature_columns = st.columns(3)
features = [
    ("Explorer les offres", "Filtrez les opportunités par métier, pays et niveau d'expérience."),
    ("Estimer un salaire", "Obtenez une estimation indicative à partir d'un profil professionnel."),
    ("Comparer les modèles", "Consultez les métriques et les explications des modèles évalués."),
]
for column, (title, description) in zip(feature_columns, features):
    with column:
        st.markdown(
            f'<article class="jm-card"><h3>{title}</h3><p class="jm-muted">{description}</p></article>',
            unsafe_allow_html=True,
        )

render_footer()