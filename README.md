💼 JobMatch

Application intelligente d’analyse et de recommandation d’offres d’emploi

🎯 Présentation

JobMatch est une application qui utilise les données du marché de l’emploi pour aider un utilisateur à identifier les offres correspondant le mieux à son profil.

L’objectif est de permettre à l’utilisateur de :

* 🔎 rechercher des offres d’emploi ;
* 📊 comprendre les tendances du marché du travail ;
* 💡 identifier les compétences les plus demandées ;
* 📍 analyser les opportunités selon la localisation ;
* 💼 explorer les métiers et secteurs qui recrutent ;
* 🤝 obtenir des recommandations d’offres adaptées à son profil.

❓ Problématique

Comment utiliser les données du marché de l’emploi pour aider un utilisateur à identifier les offres qui correspondent le mieux à son profil et à ses compétences ?

⸻

📊 Dataset

Le projet utilise le dataset Job Market Intelligence 2024 - Skills Global Dataset disponible sur Kaggle.

Le dataset contient plusieurs fichiers permettant d’analyser les offres d’emploi, les entreprises, les compétences, les pays et les plateformes de recrutement. (Kaggle)

Fichiers utilisés

* fact_job_postings.csv → informations principales sur les offres d’emploi
* dim_skill.csv → liste des compétences
* dim_company.csv → informations sur les entreprises
* dim_country.csv → informations géographiques
* dim_platform.csv → plateformes de recrutement
* bridge_job_skills.csv → relation entre les offres et les compétences

🔗 Source

Kaggle — Job Market Intelligence 2024-Skills Global Dataset

⸻

🧹 Nettoyage des données

Avant l’analyse, les données seront étudiées et nettoyées afin de garantir leur qualité.

Les étapes principales sont :

* compréhension des fichiers ;
* identification des colonnes ;
* identification des clés et des relations ;
* vérification des types de données ;
* recherche des valeurs manquantes ;
* recherche des doublons ;
* détection des incohérences ;
* standardisation des données ;
* préparation des données pour l’analyse et l’application.

⸻

📈 Analyse des données

L’analyse permettra notamment de répondre aux questions suivantes :

* Quels sont les métiers les plus recherchés ?
* Quelles sont les compétences les plus demandées ?
* Quelles entreprises recrutent le plus ?
* Dans quelles régions ou pays trouve-t-on le plus d’opportunités ?
* Quels types de contrats sont les plus fréquents ?
* Quel est le niveau d’expérience demandé ?
* Quelle est la répartition du travail à distance ?
* Existe-t-il des relations entre les métiers et les compétences demandées ?

Les analyses seront réalisées avec Python, Pandas, NumPy et Matplotlib.

⸻

🤖 Data Science

Une partie Data Science sera consacrée à la création d’un système de recommandation d’offres.

L’utilisateur pourra renseigner son profil, par exemple :

Métier : Data Analyst
Compétences : Python, SQL, Excel, Power BI
Expérience : Junior
Localisation : France
Type de travail : Télétravail / Hybride / Présentiel

Le système analysera ensuite la correspondance entre le profil de l’utilisateur et les offres disponibles.

Le score de recommandation pourra prendre en compte plusieurs critères :

* compétences ;
* métier recherché ;
* niveau d’expérience ;
* localisation ;
* type de travail.

Les critères et leur importance seront définis et testés pendant la partie Data Science.

⸻

🖥️ Application

L’application sera développée avec Streamlit.

Elle pourra être organisée autour de plusieurs pages :

🏠 Accueil
📊 Dashboard
👤 Mon profil
🔎 Recherche d'offres
🤝 Recommandations

L’objectif final est d’obtenir une application fonctionnelle, interactive et facilement utilisable.

⸻

🛠️ Technologies utilisées

* Python
* Pandas
* NumPy
* Matplotlib
* Scikit-learn
* Streamlit
* Jupyter Notebook
* Git
* GitHub
* Kaggle

⸻

📁 Structure du projet

JobMatch/
│
├── app/
│
├── data/
│
├── models/
│
├── pages/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_data_analysis.ipynb
│   ├── 04_data_science.ipynb
│   └── 05_model_evaluation.ipynb
│
├── src/
│
├── tests/
│
├── app.py
├── README.md
└── requirements.txt

📓 Organisation des notebooks

01 — Data Understanding

Comprendre la structure et le contenu des données.

02 — Data Cleaning

Nettoyer, corriger et préparer les données.

03 — Data Analysis

Analyser les tendances et produire des visualisations.

04 — Data Science

Développer le système de recommandation.

05 — Model Evaluation

Évaluer les résultats du modèle et vérifier sa pertinence.

⸻

👥 Membres du groupe

* Claudia
* Kenny
* Béatrice
* Nelson
* Kim

⸻

👨‍💻 Organisation du projet

Le travail est réparti autour de plusieurs domaines :

* Dataset & Data Cleaning → compréhension et nettoyage des données
* Data Analysis → analyses et visualisations
* Data Science → modèle de recommandation et évaluation
* Application → développement de l’interface Streamlit

Chaque membre doit également comprendre le fonctionnement global du projet.

⸻

🚀 Objectif final

L’objectif de JobMatch est de transformer les données du marché de l’emploi en une application concrète permettant à un utilisateur de mieux comprendre les opportunités professionnelles disponibles et de trouver des offres correspondant à son profil.

De la donnée → à l’analyse → au modèle → à une application fonctionnelle.