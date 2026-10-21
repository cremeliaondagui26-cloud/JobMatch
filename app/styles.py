"""Shared visual styling and navigation helpers for the Streamlit app."""

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


NAV_ITEMS = (
    ("Accueil", "/", "home"),
    ("Offres d'emploi", "/offres", "offers"),
    ("Prédiction salariale", "/Prediction", "prediction"),
)


def apply_theme() -> None:
    """Apply the shared JobMatch theme once per page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --jm-navy: #102A43;
            --jm-blue: #2563EB;
            --jm-blue-hover: #174DBB;
            --jm-bg: #F3F5F7;
            --jm-border: #DCE3E9;
            --jm-muted: #62758A;
        }

        .stApp {
            background: var(--jm-bg);
            color: var(--jm-navy);
            font-family: Inter, Arial, sans-serif;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 0;
            padding-bottom: 3.5rem;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            display: none;
        }

        .jm-header {
            background: #fff;
            border-bottom: 1px solid var(--jm-border);
            margin: 0 calc((1200px - 100vw) / 2) 0;
            min-height: 116px;
            padding: 0 max(1.5rem, calc((100vw - 1200px) / 2));
            display: grid;
            grid-template-columns: 240px 1fr;
            align-items: center;
            gap: 2rem;
        }

        .jm-brand-lockup {
            align-items: center;
            display: flex;
            gap: 0.8rem;
        }

        .jm-brand-mark {
            align-items: center;
            background: var(--jm-navy);
            color: #fff;
            display: flex;
            font-size: 1.55rem;
            font-weight: 700;
            height: 58px;
            justify-content: center;
            position: relative;
            width: 58px;
        }

        .jm-brand-mark::after {
            background: var(--jm-blue);
            bottom: 10px;
            content: "";
            height: 4px;
            position: absolute;
            right: -8px;
            width: 20px;
        }

        .jm-brand-name {
            color: var(--jm-navy);
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.05;
        }

        .jm-brand-tagline {
            color: var(--jm-muted);
            font-size: 0.68rem;
            line-height: 1.25;
            margin-top: 0.35rem;
            max-width: 120px;
        }

        .jm-nav {
            align-items: stretch;
            display: flex;
            gap: 2.25rem;
            height: 100%;
            justify-content: center;
        }

        .jm-nav a {
            color: var(--jm-navy) !important;
            display: flex;
            align-items: center;
            border-bottom: 3px solid transparent;
            font-size: 0.98rem;
            font-weight: 500;
            opacity: 1 !important;
            text-align: center;
            text-decoration: none;
            white-space: nowrap;
        }

        .jm-nav a:hover,
        .jm-nav a.jm-active {
            color: var(--jm-blue) !important;
            border-bottom-color: var(--jm-blue);
        }

        .jm-hero, .jm-panel, .jm-card {
            background: #fff;
            border: 1px solid var(--jm-border);
            padding: 1.35rem 1.5rem;
        }

        .jm-hero { margin-bottom: 1.25rem; }
        .jm-hero h1 { color: var(--jm-navy); margin: 0 0 0.45rem; }
        .jm-hero p, .jm-muted { color: var(--jm-muted); }
        .jm-panel { margin-bottom: 1.25rem; }
        .jm-card h3 { color: var(--jm-navy); margin-top: 0; }

        .jm-home-hero {
            align-items: center;
            display: grid;
            gap: 4rem;
            grid-template-columns: minmax(0, 1fr) minmax(420px, 0.95fr);
            padding: 5.5rem 0 4rem;
        }

        .jm-eyebrow {
            border-top: 2px solid var(--jm-blue);
            color: var(--jm-blue);
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            padding-top: 0.25rem;
            text-transform: uppercase;
        }

        .jm-home-hero h1 {
            color: var(--jm-navy);
            font-size: clamp(2.8rem, 5vw, 4.5rem);
            letter-spacing: -0.055em;
            line-height: 0.98;
            margin: 1.8rem 0 1.5rem;
            max-width: 600px;
        }

        .jm-home-hero .jm-lead {
            color: var(--jm-muted);
            font-size: 1.15rem;
            line-height: 1.6;
            max-width: 570px;
        }

        .jm-market-card {
            background: #fff;
            border: 1px solid #bfcddd;
        }

        .jm-market-head {
            border-bottom: 1px solid var(--jm-border);
            padding: 1.45rem 1.6rem;
        }

        .jm-market-kicker {
            color: var(--jm-muted);
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .jm-market-title {
            color: var(--jm-navy);
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 0.65rem;
        }

        .jm-market-body {
            display: grid;
            grid-template-columns: 1fr 1.1fr;
            min-height: 245px;
            padding: 2.5rem 1.6rem 1.4rem;
        }

        .jm-market-label {
            color: var(--jm-muted);
            font-size: 0.82rem;
        }

        .jm-market-value {
            color: var(--jm-navy);
            font-size: 2.25rem;
            font-weight: 700;
            margin-top: 1rem;
        }

        .jm-chart {
            align-items: end;
            border-bottom: 1px solid var(--jm-border);
            display: flex;
            gap: 0.45rem;
            height: 150px;
            padding: 0 0.35rem;
        }

        .jm-chart i {
            background: #7599e3;
            display: block;
            flex: 1;
        }

        .jm-chart i:last-child { background: var(--jm-blue); }

        .jm-market-stats {
            border-top: 1px solid var(--jm-border);
            display: grid;
            grid-template-columns: repeat(3, 1fr);
        }

        .jm-market-stat {
            border-right: 1px solid var(--jm-border);
            padding: 1rem;
        }

        .jm-market-stat:last-child { border-right: 0; }
        .jm-market-stat small { color: var(--jm-muted); display: block; }
        .jm-market-stat strong { color: var(--jm-navy); display: block; margin-top: 0.5rem; }

        div[data-testid="stMetric"] {
            background: #fff;
            border: 1px solid var(--jm-border);
            padding: 1rem;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: var(--jm-navy) !important;
            opacity: 1 !important;
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600;
        }

        div.stButton > button {
            background: var(--jm-blue);
            border: 1px solid var(--jm-blue);
            border-radius: 0;
            color: #fff;
            font-weight: 600;
            min-height: 2.8rem;
        }

        div.stButton > button:hover {
            background: var(--jm-blue-hover);
            border-color: var(--jm-blue-hover);
            color: #fff;
        }

        input, textarea, [data-baseweb="select"] > div {
            background: #fff !important;
            border-radius: 0 !important;
            border-color: var(--jm-border) !important;
        }

        input, textarea,
        [data-baseweb="select"] *,
        [data-testid="stTextInput"] input {
            color: var(--jm-navy) !important;
        }

        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label,
        [data-testid="stTextInput"] label {
            color: var(--jm-navy) !important;
            font-size: 0.86rem !important;
            font-weight: 600 !important;
        }

        .jm-page-intro {
            border-bottom: 1px solid var(--jm-border);
            margin: 2.5rem 0 2rem;
            padding-bottom: 1.25rem;
        }

        .jm-page-intro h1 {
            color: var(--jm-navy);
            font-size: 2rem;
            letter-spacing: -0.025em;
            margin: 0 0 0.45rem;
        }

        .jm-page-intro p {
            color: var(--jm-muted);
            margin: 0;
        }

        .jm-section-title {
            color: var(--jm-navy);
            font-size: 1.15rem;
            font-weight: 700;
            margin: 2rem 0 0.85rem;
        }

        .jm-filter-panel {
            background: #fff;
            border: 1px solid var(--jm-border);
            padding: 1.25rem 1.35rem 0.5rem;
        }

        .jm-result-count {
            background: #fff;
            border-left: 4px solid var(--jm-blue);
            border-top: 1px solid var(--jm-border);
            border-right: 1px solid var(--jm-border);
            border-bottom: 1px solid var(--jm-border);
            color: var(--jm-navy);
            font-size: 1.25rem;
            font-weight: 700;
            margin: 1.5rem 0;
            padding: 1rem 1.25rem;
        }

        .jm-chart-panel {
            background: #fff;
            border: 1px solid var(--jm-border);
            padding: 1rem 1.25rem;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--jm-border);
        }

        .jm-footer {
            background: var(--jm-navy);
            color: #fff;
            margin: 3rem calc((1200px - 100vw) / 2) -3.5rem;
            padding: 2.5rem max(1.5rem, calc((100vw - 1200px) / 2));
        }

        .jm-footer-inner {
            align-items: center;
            display: flex;
            justify-content: space-between;
            margin: 0 auto;
            max-width: 1200px;
        }

        .jm-footer strong { font-size: 1rem; }
        .jm-footer span { color: #b9c8d8; font-size: 0.8rem; }

        .jm-footer a {
            color: #fff;
            margin-left: 1.5rem;
            text-decoration: none;
        }

        @media (max-width: 640px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .jm-header {
                margin-left: -1rem;
                margin-right: -1rem;
                padding-left: 1rem;
                padding-right: 1rem;
                grid-template-columns: 1fr;
                gap: 1rem;
                padding-bottom: 1rem;
                padding-top: 1rem;
            }
            .jm-nav { gap: 1rem; justify-content: flex-start; overflow-x: auto; }
            .jm-nav a { font-size: 0.82rem; }
            .jm-footer { margin-left: -1rem; margin-right: -1rem; }
            .jm-footer-inner { align-items: flex-start; flex-direction: column; gap: 1rem; }
            .jm-footer a { margin-left: 0; margin-right: 1rem; }
            .jm-home-hero {
                gap: 2rem;
                grid-template-columns: 1fr;
                padding: 3rem 0;
            }
            .jm-market-body { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(active_page: str) -> None:
    """Render the shared brand and links to the Streamlit multipage routes."""
    links = "".join(
        f'<a class="{"jm-active" if key == active_page else ""}" href="{path}">{label}</a>'
        for label, path, key in NAV_ITEMS
    )
    st.markdown(
        f"""
        <header class="jm-header">
            <div class="jm-brand-lockup">
                <div class="jm-brand-mark">J</div>
                <div>
                    <div class="jm-brand-name">JobMatch</div>
                    <div class="jm-brand-tagline">L’emploi éclairé par la donnée</div>
                </div>
            </div>
            <nav class="jm-nav">{links}</nav>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render the shared application footer."""
    st.markdown(
        """
        <footer class="jm-footer">
            <div class="jm-footer-inner">
                <div>
                    <strong>JobMatch</strong><br>
                    <span>L’emploi éclairé par la donnée</span>
                </div>
                <div>
                    <a href="/">Accueil</a>
                    <a href="/offres">Offres d'emploi</a>
                    <a href="/Prediction">Prédiction salariale</a>
                </div>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def render_intro(title: str, description: str, icon: str = "") -> None:
    """Render a consistent page introduction."""
    st.markdown(
        f"""
        <section class="jm-page-intro">
            <h1>{icon + " " if icon else ""}{title}</h1>
            <p>{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
