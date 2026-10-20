# JobMatch

Projet étudiant d'analyse et d'estimation salariale à partir d'offres d'emploi.

**Problématique :** peut-on estimer le salaire d'une offre à partir du métier, du niveau d'expérience et de la localisation, afin d'aider les candidats à comprendre les rémunérations proposées ?

Le projet contient une EDA et une expérience de Machine Learning reproductible. La recommandation reste complémentaire : `src/recommender.py` conserve un prototype de score de recouvrement des compétences. L'application Streamlit existante est un squelette réservé à une étape ultérieure ; elle n'a pas été modifiée.

## Données et unités

Source annoncée : **Job Market Intelligence 2024 - Skills Global Dataset**, Kaggle. Les six CSV sources sont conservés sans modification dans `data/raw/`.

- `fact_job_postings.csv` : 55 000 offres, 13 colonnes sources, une ligne par offre.
- `bridge_job_skills.csv` : 247 398 liens offre-compétence.
- `dim_skill.csv`, `dim_company.csv`, `dim_country.csv`, `dim_platform.csv` : tables de référence.

Une offre peut demander plusieurs compétences. Les effectifs et pourcentages de compétences comptent des offres distinctes, sans compter deux fois une famille pour une même offre.

La cible est **le milieu de la fourchette salariale** : `(salary_min_usd + salary_max_usd) / 2`. Ce milieu n'est ni une médiane ni un salaire effectivement versé. La médiane est ensuite calculée entre les milieux des offres d'un groupe.

Les sources et les modèles restent en **USD**. L'EDA présente les montants en **EUR**, au taux indicatif fixe de **1 USD = 0,92 EUR**, centralisé dans `src/analysis.py`. Ce taux n'est pas actuel ou officiel. La période salariale et la méthode de collecte ne sont pas établies par les seuls CSV : les montants ne doivent pas être qualifiés d'annuels sans confirmation de la source.

## Organisation

```text
JobMatch/
├── data/raw/
│   ├── fact_job_postings.csv
│   ├── bridge_job_skills.csv
│   ├── dim_skill.csv
│   ├── dim_company.csv
│   ├── dim_country.csv
│   └── dim_platform.csv
├── notebooks/
│   ├── 01_EDA.ipynb
│   └── 02_Machine_Learning.ipynb
├── src/
│   ├── analysis.py
│   ├── salary_prediction.py
│   └── recommender.py
├── tests/
│   ├── test_analysis.py
│   └── test_salary_prediction.py
├── app/                       # fichiers Streamlit existants conservés
├── README.md
├── requirements.txt
└── .gitignore                 # inchangé
```

Les environnements et configurations locaux existants sont conservés. Aucun dossier `data/processed/` ni modèle sérialisé n'est nécessaire : le découpage, les variables et les prédictions sont recalculés en mémoire. Les exports sont facultatifs.

## Installation et exécution

Environnement de validation : Python 3.13 sous Windows. Les versions des bibliothèques d'analyse et d'exécution sont fixées dans `requirements.txt`.

Depuis la racine du projet, dans PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

Choisir le Python de `.venv/Scripts/python.exe` comme noyau et exécuter chaque notebook depuis un noyau neuf, dans l'ordre des cellules.

Exécution automatique :

```powershell
.\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_EDA.ipynb
.\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_Machine_Learning.ipynb
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.salary_prediction
```

Le script salarial n'entraîne rien lors de son import. Il affiche les scores de l'expérience principale sans écrire de fichiers. Pour exporter volontairement :

```powershell
.\.venv\Scripts\python.exe -m src.salary_prediction --export CHEMIN_DE_SORTIE
```

## EDA

Le notebook suit seize étapes : objectifs, dataset, chargement, relations, qualité, métiers, salaires, expérience, modes de travail, compétences, compétences par métier, Entry/Senior, pays, associations statistiques, limites et conclusion.

Il conserve les distributions, les comparaisons salariales, les familles et leurs paires avec support/lift, les pourcentages par groupe, les tests du chi² avec correction de Bonferroni, Pearson, Spearman, V de Cramér et η². Les 13 pays sont tous présentés. Business Analyst est absent ; Business Intelligence Analyst est un intitulé distinct.

Les écarts salariaux observés sont surtout associés au métier (η² ≈ 0,672). Les écarts selon l'expérience et le pays sont faibles dans ce fichier. Cela ne démontre ni une causalité ni une absence d'influence sur le marché réel. Un test non significatif ne prouve pas l'égalité des groupes. L'uniformité des répartitions ne suffit pas à conclure que les données ont été fabriquées.

## Modélisation et résultats

Le découpage est identique pour toutes les configurations : **44 000 offres d'entraînement, 11 000 de test**, graine 42. Les identifiants et les bornes salariales sont exclus de X. L'encodage et le vocabulaire de compétences sont ajustés uniquement à partir de l'entraînement. Aucun hyperparamètre n'est choisi sur le test.

Expérience principale : métier, expérience et pays, Ridge alpha=10 avec solveur lsqr.

| Modèle | MAE (USD) | RMSE (USD) | R² |
|---|---:|---:|---:|
| Moyenne globale — DummyRegressor | 31 452,33 | 36 998,20 | ≈ 0 |
| Moyenne par métier | 17 870,60 | 21 318,46 | 0,668 |
| Ridge — métier, expérience, pays | 17 867,75 | 21 320,21 | 0,668 |

Ridge apporte seulement 2,85 USD de gain en MAE par rapport à la moyenne par métier, et son RMSE est légèrement supérieur. Aucun avantage pratique marqué n'est établi.

Deux configurations existantes sont conservées pour comparaison :

- Ancien modèle enrichi : métier, pays, expérience, mode, contrat et compétences ; alpha=10, lsqr ; MAE Ridge **17 872,05 USD**.
- Dernier script métier/expérience : alpha=1, solveur automatique ; MAE Ridge **17 870,14 USD**.

Le changement du score principal provient des variables explicitement retenues, sans conversion de devise ni modification des données. Les scores de l'ancien modèle enrichi sont préservés à la précision affichée. La référence par métier est désormais calculée directement comme dans le dernier script ; l'écart avec l'ancienne résolution par régression linéaire est inférieur à 0,00001 USD de MAE.

La MAE est la métrique principale ; RMSE et R² la complètent. Les erreurs sont aussi examinées par métier, pays et expérience. Les résultats concernent un test aléatoire au sein du fichier, sans validation temporelle ou externe. Une erreur moyenne proche de 18 000 USD limite l'usage individuel.

## Nettoyage et traçabilité

Une sauvegarde complète externe a été créée et vérifiée avant les modifications. Les anciennes versions y restent récupérables.

| Contenu ancien | Traitement |
|---|---|
| `EDA.ipynb` + `01_data_understanding.ipynb` | Fusion dans `01_EDA.ipynb`, avec conservation de l'histogramme salarial, du nuage salaire/candidats et des pourcentages par métier. |
| `04_data_science.ipynb` + `05_model_evaluation.ipynb` + `model_training_tests.ipynb` | Fusion dans `02_Machine_Learning.ipynb` : préparation, modèles, scores, exemples d'erreurs et limites. |
| `02_data_cleaning.ipynb`, `03_data_analysis.ipynb` | Squelettes sans analyse supplémentaire ; archivés hors du dossier final. |
| `notebooks/offres.xlsx` | Export redondant archivé ; les CSV sources restent disponibles. |
| `src/data_cleaning.py`, `src/utils.py` | Modules sans appel dans le projet conservé ; archivés. |
| `data/processed/` | Anciens exports archivés ; recalcul en mémoire et export volontaire disponibles. |
| `data/README.md` | Documentation regroupée ici. |
| `models/`, `scripts/`, `tests/.gitkeep` | Dossiers vides ou simples marqueurs retirés après sauvegarde. |

Les numéros suivants sont les **indices de cellules à partir de zéro** dans les anciennes versions sauvegardées :

| Anciennes cellules | Fusion finale |
|---|---|
| EDA 3, 5–10 : aperçu, dimensions et types | EDA 5 : présentation des tables, schéma et exemples. |
| EDA 14–28 : qualité et relations | EDA 7 : contrôles regroupés, y compris les références des dimensions. |
| EDA 21, 23, 35–41 et 70 : statistiques salariales | EDA 14, 16 et 18 : descriptif, tableaux complets, comparaisons et graphiques distincts en EUR. Le deuxième boxplot par expérience et les impressions de diagnostic sont retirés. |
| EDA 44, 46, 49 : modes de travail | EDA 24 : effectifs et pourcentages par expérience, métier et groupe croisé. |
| EDA 52, 54, 57, 60, 63, 64 | EDA 27, 29, 32, 35, 36 : analyses de compétences conservées. |
| EDA 49, 70, 73 : associations | EDA 42–43 : coefficients, η², chi² et nuage salaire/candidats. |
| ML 04 : cellules 4–11 | Diagnostics répétés retirés ; un seul affichage pertinent des variables et des scores. |
| ML 05 : cellules 1 et 5 | Entraînement centralisé ; mêmes IDs pour toutes les comparaisons. |
| ML 05 : cellules 6, 8, 9 | Exemples d'erreurs et recalcul de MAE conservés dans le notebook unique. |

Les fonctions `skill_pairs`, `skill_prevalence`, `group_percentages`, le regroupement des familles, la conversion salariale, les résumés et les coefficients d'association sont centralisés dans `src/analysis.py`. `missing_values_report`, inutilisée, a été retirée. Les modèles sont centralisés dans `evaluate_salary_model`.

### Devises des cellules finales

| Notebook et cellules (indices à partir de zéro) | Convention |
|---|---|
| EDA 3 | Chargement des sources USD, calcul du milieu et des colonnes EUR ; taux centralisé. |
| EDA 5 | Schéma des sources USD ; exemples de montants en EUR. |
| EDA 7 | Contrôle des bornes sources USD ; seuls des effectifs sont affichés. |
| EDA 14, 16 et 18 | Descriptif, comparaisons et graphiques salariaux en EUR. |
| EDA 42–43 | Coefficients sans unité calculés sur des variables salariales EUR ; nuage salarial en EUR. |
| Machine Learning 1, 3, 6, 8, 10, 12 | Cibles, prédictions, MAE et RMSE en USD ; R² sans unité. |

Le formatage français ne change pas les valeurs de calcul. Les effectifs restent des entiers.

## Vérifications et limites restantes

- Deux notebooks exécutés depuis un noyau neuf : 17 cellules de code pour l'EDA, 6 pour le Machine Learning.
- 14 tests réussis : dénominateurs, dédoublonnage, familles, conversion, coefficients, IDs, catégories inconnues, bornes invalides et prévention des fuites.
- Dépendances installées cohérentes (`pip check`).
- Contenu des six CSV vérifié par SHA-256 après déplacement.
- Fichiers Streamlit, Git, configuration du dépôt et `.gitignore` préservés.
- Les limites restantes concernent la documentation de collecte, la période salariale, la représentativité et la généralisation du modèle ; elles ne sont pas corrigées artificiellement.

## Groupe

Claudia, Kenny, Béatrice, Nelson et Kim.
