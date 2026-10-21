
import streamlit as st
from src.predictor import predict_salary

st.set_page_config(
    page_title="JobMatch | Prédiction salariale",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080f1e, #101c32);
    color: #f1f5f9;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0b1425;
    border-right: 1px solid #233451;
}

.hero {
    background: linear-gradient(110deg, #14284a, #203c78);
    border: 1px solid #2b4776;
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 2.4rem;
    margin-bottom: 10px;
}

.hero p {
    color: #c2d2ef;
    font-size: 1.05rem;
}

.panel {
    background: #111e33;
    border: 1px solid #263957;
    border-radius: 18px;
    padding: 26px;
    margin-bottom: 22px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #1b2b45;
    color: #f1f5f9;
    border-color: #354b6d;
    border-radius: 10px;
}

div.stButton > button {
    width: 100%;
    min-height: 48px;
    border: none;
    border-radius: 10px;
    color: white;
    font-weight: 600;
    background: linear-gradient(90deg, #347cf6, #6258f5);
    transition: 0.2s ease;
}

div.stButton > button:hover {
    border: 1px solid #8ab4ff;
    color: white;
    filter: brightness(1.12);
}

div[data-testid="stMetric"] {
    background: #172943;
    border: 1px solid #304667;
    border-radius: 14px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📊 Prédiction salariale</h1>
    <p>
        Estimez votre valeur sur le marché selon le poste,
        l'expérience et le pays.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="panel">
    <h3>👤 Informations du profil</h3>
    <p>Renseignez les informations du poste à évaluer.</p>
</div>
""", unsafe_allow_html=True)

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
