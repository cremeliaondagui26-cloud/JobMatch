from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="JobMatch", layout="wide")

st.title("JobMatch")
st.write("Base de projet pour l'exploration de donnees et le prototypage d'un systeme de matching.")

st.subheader("Sections")
st.markdown("- Donnees brutes dans `data/raw/`")
st.markdown("- Traitements Python dans `src/`")
st.markdown("- Notebooks d'analyse dans `notebooks/`")
