from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from styles import apply_theme, render_footer, render_header, render_intro

st.set_page_config(
    page_title="JobMatch | Offres",
    page_icon="🔎",
    layout="wide"
)
apply_theme()
render_header("offers")

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

render_intro(
    "Exploration des offres d'emploi",
    "Recherchez des offres et explorez leurs caractéristiques.",
)

# Filtres
st.markdown('<div class="jm-section-title">Filtres de recherche</div>', unsafe_allow_html=True)
with st.container():
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

st.markdown(
    f'<div class="jm-result-count">{len(offres):,} offres trouvées</div>',
    unsafe_allow_html=True,
)

if offres.empty:
    st.warning("Aucune offre ne correspond aux filtres.")
    st.stop()

# Tableau
st.markdown('<div class="jm-section-title">Résultats de recherche</div>', unsafe_allow_html=True)

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
    width="stretch",
    hide_index=True
)

# Visualisations
st.divider()
st.markdown('<div class="jm-section-title">Analyse des offres filtrées</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="jm-chart-panel"><strong>Top 10 des métiers</strong>', unsafe_allow_html=True)
    top_metiers = offres["job_title"].value_counts().head(10)
    chart = alt.Chart(top_metiers.rename_axis("Métier").reset_index(name="Offres")).mark_bar(
        color="#2563EB"
    ).encode(
        x=alt.X("Métier:N", sort="-y", axis=alt.Axis(labelAngle=-45, labelColor="#62758A")),
        y=alt.Y("Offres:Q", axis=alt.Axis(labelColor="#62758A", title=None)),
        tooltip=["Métier:N", "Offres:Q"],
    ).properties(height=280).configure_view(stroke=None).configure_axis(
        domainColor="#DCE3E9", gridColor="#EEF2F5"
    )
    st.altair_chart(chart, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="jm-chart-panel"><strong>Répartition par expérience</strong>', unsafe_allow_html=True)
    repartition = offres["experience_level"].value_counts()
    chart = alt.Chart(repartition.rename_axis("Expérience").reset_index(name="Offres")).mark_bar(
        color="#2563EB"
    ).encode(
        x=alt.X("Expérience:N", axis=alt.Axis(labelColor="#62758A", title=None)),
        y=alt.Y("Offres:Q", axis=alt.Axis(labelColor="#62758A", title=None)),
        tooltip=["Expérience:N", "Offres:Q"],
    ).properties(height=280).configure_view(stroke=None).configure_axis(
        domainColor="#DCE3E9", gridColor="#EEF2F5"
    )
    st.altair_chart(chart, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="jm-section-title">Salaires médians par métier</div>', unsafe_allow_html=True)

salaires = (
    offres.groupby("job_title")["salary_midpoint_usd"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

chart = alt.Chart(salaires.rename_axis("Métier").reset_index(name="Salaire médian")).mark_bar(
    color="#174DBB"
).encode(
    x=alt.X("Métier:N", sort="-y", axis=alt.Axis(labelAngle=-45, labelColor="#62758A")),
    y=alt.Y("Salaire médian:Q", axis=alt.Axis(labelColor="#62758A", title=None)),
    tooltip=["Métier:N", "Salaire médian:Q"],
).properties(height=320).configure_view(stroke=None).configure_axis(
    domainColor="#DCE3E9", gridColor="#EEF2F5"
)
st.altair_chart(chart, width="stretch")

st.caption(
    "Les montants représentent le milieu des fourchettes "
    "salariales annoncées, en USD."
)
render_footer()