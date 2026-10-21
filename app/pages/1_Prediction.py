
import streamlit as st
from styles import apply_theme, render_footer, render_header, render_intro
from src.predictor import predict_salary

st.set_page_config(
    page_title="JobMatch | Prédiction salariale",
    page_icon="📊",
    layout="wide"
)
apply_theme()
render_header("prediction")
render_intro("Prédiction salariale", "Estimez votre valeur sur le marché selon le poste, l'expérience et le pays.", "📊")

st.markdown(
    '<section class="jm-panel"><h3>👤 Informations du profil</h3><p class="jm-muted">Renseignez les informations du poste à évaluer.</p></section>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    job_title = st.text_input(
        "Intitulé du poste *",
        placeholder="Ex. : Data Analyst"
    )

with col2:
    experience_level = st.selectbox(
        "Niveau d'expérience *",
        ["Entry", "Mid", "Senior", "Executive"]
    )

country = st.text_input(
    "Pays *",
    placeholder="Ex. : United States",
    value="United States"
)

st.write("")

if st.button("✨  Estimer le salaire"):
    if not job_title.strip() or not country.strip():
        st.warning("Veuillez renseigner le poste et le pays.")
    else:
        try:
            salaire = predict_salary(
                job_title.strip(),
                experience_level,
                country.strip()
            )

            st.markdown("### Résultat de l'estimation")

            with st.container(border=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.caption("SALAIRE ANNUEL ESTIMÉ")
                    st.markdown(f"## {salaire:,.2f} USD")
                    st.caption("Estimation indicative générée par JobMatch.")

                with col2:
                    st.caption("PROFIL ANALYSÉ")
                    st.write(f"**Poste :** {job_title}")
                    st.write(f"**Expérience :** {experience_level}")
                    st.write(f"**Pays :** {country}")

        except Exception as erreur:
            st.error(f"Erreur lors de la prédiction : {erreur}")

st.divider()

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("🛡️ **Données exploitées**")
    st.caption("Informations issues du dataset du projet.")

with col_b:
    st.markdown("⚡ **Estimation rapide**")
    st.caption("Résultat calculé par le modèle entraîné.")

with col_c:
    st.markdown("🧠 **Modèle prédictif**")
    st.caption("Estimation à partir du poste, de l'expérience et du pays.")

render_footer()
