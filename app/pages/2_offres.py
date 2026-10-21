from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="JobMatch | Offres",
    page_icon="🔎",
    layout="wide"
)

ROOT = Path(__file__).resolve().parents[2]

@st.cache_data
def charger_offres():
    chemin = ROOT / "data" / "raw" / "fact_job_postings.csv"
    return pd.read_csv(chemin)

try:
    df = charger_offres()
except FileNotFoundError:
    st.error("Le fichier des offres est introuvable.")
    st.stop()

# Salaire cible : milieu de la fourchette annoncée
df["salary_midpoint_usd"] = (
    df["salary_min_usd"] + df["salary_max_usd"]
) / 2

st.title("🔎 Exploration des offres d'emploi")
st.write("Recherchez des offres et explorez leurs caractéristiques.")

st.divider()

# Filtres
col1, col2, col3 = st.columns(3)

with col1:
    recherche = st.text_input(
        "Rechercher un métier",
        placeholder="Ex. Data Scientist"
    )

with col2:
    pays = st.multiselect(
        "Pays",
        options=sorted(df["country"].dropna().unique())
    )

with col3:
    experiences = st.multiselect(
        "Niveau d'expérience",
        options=sorted(df["experience_level"].dropna().unique())
    )

# Application des filtres
offres = df.copy()

if recherche:
    offres = offres[
        offres["job_title"].fillna("").str.contains(
            recherche, case=False, regex=False
        )
    ]

if pays:
    offres = offres[offres["country"].isin(pays)]

if experiences:
    offres = offres[
        offres["experience_level"].isin(experiences)
    ]

st.metric("Offres trouvées", len(offres))

if offres.empty:
    st.warning("Aucune offre ne correspond aux filtres.")
    st.stop()

# Tableau
st.subheader("📋 Résultats de recherche")

colonnes = [
    "job_title",
    "country",
    "experience_level",
    "salary_min_usd",
    "salary_max_usd",
    "salary_midpoint_usd"
]

st.dataframe(
    offres[colonnes],
    use_container_width=True,
    hide_index=True
)

# Visualisations
st.divider()
st.subheader("📊 Analyse des offres filtrées")

col1, col2 = st.columns(2)

with col1:
    st.write("**Top 10 des métiers**")
    top_metiers = offres["job_title"].value_counts().head(10)
    st.bar_chart(top_metiers)

with col2:
    st.write("**Répartition par expérience**")
    repartition = offres["experience_level"].value_counts()
    st.bar_chart(repartition)

st.subheader("💰 Salaires médians par métier")

salaires = (
    offres.groupby("job_title")["salary_midpoint_usd"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(salaires)

st.caption(
    "Les montants représentent le milieu des fourchettes "
    "salariales annoncées, en USD."
)