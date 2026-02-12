# Assistant RAG avec Llama

Ce projet implémente un assistant virtuel basé sur un modèle Llama, utilisant la technique de Retrieval-Augmented Generation (RAG) pour fournir des réponses précises et contextuelles à partir d'une base de connaissances personnalisée.
L'objectif est de reprendre un prototype réalisé qui était fonctionnel et de procéder à quelques améliorations afin d'obtenir des meilleurs résultats.
Les améliorations seront visibles avec une comparaison des métriques ragas sur le prototype vs la nouvelle structuration du projet.

## Fonctionnalités

- 🗄️ **Création des vecteurs** avec HuggingFaceEmbeddings.
- 🗄️ **Recherche sémantique** avec FAISS pour trouver les documents pertinents (PDF à disposition).
- 🗄️ **Recherche dans une base relationnelle** avec une base de données PostreSQL pour effectuer une recherche des éléments chiffrés.
- 🔍 **Choix du système** pour sélectionner le bon type de donnée à prendre.
- 🤖 **Génération de réponses** avec un modèle Llama (llama-3.3-70b-versatile) via Groq.
- ⚙️ **Paramètres personnalisables** (modèle, nombre de documents, score minimum, etc).

## Prérequis

- Python 3.9+ 
- Clé API Groq (avoir un compte et se diriger vers : https://console.groq.com/keys)
- Avoir une solution de stockage en local (PostreSQL utilisé ici)

## Installation

1. **Cloner le dépôt**

```
git clone git@github.com:SCFlorian/Evaluation_LLM.git
cd Evaluation_LLM
```

2. **Installez les dépendances : Le projet utilise pyproject.toml pour la gestion des dépendances :**
```
poetry install --no-root
```
3. **Ouvrir le projet dans VS Code :**
```
code .
```
4. **Configurez l’environnement Python dans VS Code**
	1.	Installez l’extension Python (si ce n’est pas déjà fait).
	2.	Appuyez sur Ctrl+Shift+P (Windows/Linux) ou Cmd+Shift+P (Mac).
	4.	Recherchez “Python: Select Interpreter”.
	5.	Sélectionnez l’environnement créé par Poetry ou celui dans lequel tu as installé le projet.

5. **Configurer la clé API**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
GROQ_API_KEY=votre_clé_api_groq
DATABASE_URL="postgresql://**user**:**mdp**e@localhost:5432/**nom_bdd**"
```

## Structure du projet

```
.
├── data/                                      # Dossier contenant nos fichiers csv d'évaluation
│   └── processed/  
│       ├──first_ragas_results.csv             # Résultats de la première évaluation ragas
│       ├──resultat_evaluation.csv             # Génération des questions/réponses
│   └── raw/                                   # Scripts de génération des évaluations
│       ├──Reddit 1.pdf                        # Premier fichier Reddit
│       ├──Reddit 2.pdf                        # Deuxième fichier Reddit
│       ├──Reddit 3.pdf                        # Troisième fichier Reddit
│       ├──Reddit 4.pdf                        # Quatrième fichier Reddit
│       ├──regular NBA.xlsx                    # Fichier excel avec les statistiques par joueur
├── database/                                  # Création et génération de la BDD
│   ├──creation_db.py                          # Script avec les classes de nos tables
│   ├──generation_db.py                        # Génération de notre BDD et ajout du fichier excel
│   ├──sql_tool.py                             # Préparation de la chaîne pour récupérer les informations depuis la BDD
├── evaluations/                               # Scripts de génération des évaluations
│   ├──first_ragas_evaluation.py               # Script de la première évaluation ragas
│   ├──generation_answers.py                   # Script de la génération des questions/réponses
├── notebooks/                                 # Dossier contenant les notebooks pour une meilleure compréhension des données
│   ├──notebook_analyse_exploratoire.ipynb     # Notebook sur la préparation du fichier excel pour les évaluations
├── rag/                                       # Scripts contenant les fonctions du projet
│   ├──cleaning_excel.py                       # Script préparant les fichiers excel (dont nettoyage) pour la BDD
│   ├──config.py                               # Script contenant les configurations (le nom des paramètres, des modèles etc)
│   ├──creation_llm.py                         # Script contenant la création du LLM (initialisation du modèle, génération de la réponse)
│   ├──data_loader.py                          # Script contenant le chargement des documents
│   ├──retrieval.py                            # Script contenant la recherche dans la documentation
│   ├──schema_validation.py                    # Script contenant les schémas de validation Pydantic
│   ├──vector_store.py                         # Script contenant les différentes fonctions allant de la création des découpages à l'enregistrement des vecteurs
├── scripts/                                   # Dossier avec l'enregistrement de notre base vectorielle
│   ├──build_index.py                          # Les documents découpés en format pkl
│   ├──chat.py                                 # la base d'index FAISS
│   ├──generation_db.py                        # la base d'index FAISS
├── tests/                                     # Dossier avec l'enregistrement de notre base vectorielle
│   ├──valisation_pydantic.py                  # Les documents découpés en format pkl
├── vector_db/                                 # Dossier avec l'enregistrement de notre base vectorielle
│   ├──document_chunks.pkl                     # Les documents découpés en format pkl
│   ├──faiss_index.idx                         # la base d'index FAISS
├── .env                                       # Enregistrement des informations qui ne doivent pas être publiées
├── .gitignore                                 # Permet de ne pas afficher les éléments sélectionnés sur GitHub
├── app.py                                     # Orchestre la vectorisation et la sauvegarde
├── MistralChat.py                             # Script pour le lancement de l'API et de l'interface avec Streamlit
├── poetry.lock                                # Pas versionné sur Git
├── pyproject.toml                             # Gestion des dépendances Poetry
├── README.md                                  # Documentation du projet

```
## Utilisation rapide
Proposition ici d'une installation rapide pour visionner l'API Rest et l'interface Streamlit.
Nous avons effectué beaucoup de changements entre le prototype et la nouvelle version alors dans le rapport technique nous irons en détail dans le fonctionnement et les explications de ce que nous utilisons dans cette nouvelle proposition du chatbot.

### 1. Ajouter des documents

Placez vos documents dans le dossier `data/raw`.
Deux formats sont suportés pour le projet, il est possible de placer des documents en PDF ainsi que des fichiers excel.
- Les documents en PDF seront transformés et enregistrés dans une base vectorielle.
- Les fichiers excel seront nettoyés et ajoutés dans une base de données relationnelle (PostreSQL utilisé ici).
- Pour maintenir une cohérence et une fiabilité dans nos données, les fichiers excel doivent respecter un certain format (vous pouvez par exemple celui utilisé  dans data/raw).

### 2. Génération des documents et de la base de données
#### Pour la création des vecteurs des documents en PDF
- Dans un premier temps assurez-vous d'avoir un dossier `vector_db/` dans le repo.
- Deux solutions s'offrent à vous :

1. Lancer le script `scripts/build_index.py`
Cela va permettre la génération des vecteurs dans le dossier `vector_db/`
2. Lancer l'app.py
```
poetry run python app.py
```
Puis ouvrez un navigateur et se rendre sur la documentation swagger de notre API
```
http://localhost:7860/docs
```
Ici vous pouvez générer la base d'index via le bouton `rebuild_index`.
Cela va permettre également la génération des vecteurs dans le dossier `vector_db/`

#### Pour la création de la base de données
L'enregistrement des datas dans la base données se fait dans une base PostreSQL en local.
1. Connexion à une base PostreSQL
Choix de la BDD PostreSQL pour sa simplicité avec l'ORM SQLAlchemy.
Création d'une BDD en local :
- Ouvrez votre terminal puis lancez les commandes une à une :
```
psql
CREATE DATABASE sportsee_nba_stats;
CREATE USER sportsee_user WITH PASSWORD '***';
GRANT ALL PRIVILEGES ON DATABASE sportsee_nba_stats TO sportsee_user;
ALTER DATABASE sportsee_nba_stats OWNER TO sportsee_user;
```
- Accès à la BDD
```
psql -U sportsee_user -d sportsee_nba_stats
```
2. Initialisation de la base de données
- Deux solutions s'offrent à vous :
- Initialisation de la base de données avec `scripts/generation_db.py`
Lancement de ce script va importer vos données excel dans votre base.
- Initialisation de la base de données depuis l'API Rest :
Depuis la documentation Swagger vous pouvez générer la base de données via le bouton `rebuild_SQL_Base`.
- Les tables sont désormais à jour. Si vous avez installé pgAdmin, vous pouvz siualsier facilement l'intégration des données.


## Rapport technique - du prototype au système actuel
### Reprise d'un prototype existant
Pour mener à bien cette mission, nous avons eu à disposition un prototype du chatbot. Dans un premier temps l'objectif a été de comprendre ce qui a été fait, quelle structure nous avons et ensuite de passer à une évaluation du système actuel via une évaluation des métriques Ragas.
### Audit du prototype
1. **Organisation du projet**
La structure de l'ancien fichier était la suivante :
```
├── inputs/                   # Dossier contenant les données à utiliser
│   ├──Reddit 1.pdf           # Capture d'écran de Reddit
│   ├──Reddit 2.pdf           # Capture d'écran de Reddit
│   ├──Reddit 3.pdf           # Capture d'écran de Reddit
│   ├──Reddit 4.pdf           # Capture d'écran de Reddit
│   ├──regular NBA.xlsx       # Fichier excel avec des statistiques NBA par joueur
├── utils/                    # Scripts pour alimenter le fichier principal
│   ├──config.py              # Script contenant les configurations (le nom des paramètres, des modèles etc)
│   ├──data_loader.py         # Script contenant le chargement des documents
│   ├──vector_store.py        # Script contenant les différentes fonctions allant de la création des découpages à l'enregistrement des vecteurs
├── vector_db/                # Dossier avec l'enregistrement de notre base vectorielle
│   ├──document_chunks.pkl    # Les documents découpés en format pkl
│   ├──faiss_index.idx        # La base d'index FAISS
├── indexer.py                # Lancement de l'enregistrement de la base vectorielle
├── MistralChat.py            # Lancement du chatbot sur une interface Streamlit
├── README.md                 # Documentation du projet
├── requirements.txt          # Fichier des dépendances
```

2. **Technologies utilisées**
- Language : Python
- Interface : Streamlit
- LLM & Embeddings MistralAI (mistral-small-latest /mistral-embed)
- Orchestration : Langchain
- Gestion des dépendances : fichier requirements

3. **Lancement de l'interface**
- Nous avons commencé par lancer le projet afin de voir si il était fonctionnel.
- On lance l'interface Streamlit. Sur votre terminal (bien vérifier que vous êtes dans le bon dossier)
```
streamlit run MistralChat.py
```
- L'application fonctionne, on peut intéragir avec le chatbot et il propose des réponses argumentées.
- À ce stade il est difficile d'évaluer la cohérence et la pertinence des réponses apportées par le chatbot.

4. **Analyse des performances du système**

L'entreprise nous a signalé que les réponses n'étaient pas suffisantes pour eux. 
Afin de s'en rendre compte nous allons évaluer le système avec les métriques de Ragas pour se faire notre propre avis.

- **Génération des questions/réponses**

L'objectif est d'évaluer le modèle avec ragas, pour cela il faut avoir un jeu de questions/réponses pour obtenir les métriques. 
Création du fichier **generation_answers.py** dans un nouveau dossier evaluations.

On y retouve 15 questions et 15 réponses (humaines) portant sur le fichier excel avec plusieurs degrés de complexité :
- Questions faciles (valeurs directes)
- Questions intermédiaires (comparaison simple)
- Questions plus difficiles (questions bruitées)
    
À la suite de ces questions, nous appelons notre système pour obtenir les réponses du chatbot.

Dans le fichier csv généré (dans le dossier resultat_evaluation.csv) nous retrouvons en plus des questions/réponses (humaines + chatbot) :
- la liste des contextes utilisés par le chatbot pour fournir une réponse (obligatoire pour ragas)
- le numéro des documents sélectionnés ainsi que son score de similarité
- **Lancement de l'évaluation ragas**
Nous chargeons les métriques que nous voulons utiliser pour évaluer le modèle (dans le fichier : first_ragas_evaluation.py) :
- **faithfulness** Génération: fidèle au contexte ?
- **answer_relevancy** Génération: réponse pertinente à la question ?
- **context_precision** Récupération: contexte précis (peu de bruit) ?
- **context_recall** Récupération: infos clés récupérées ?

Nous n'avons pas modifié le modèle afin d'évaluer le prototype tel quel, nous avons juste ajouté une instruction au prompt pour demander au LLM de faire des réponses courtes afin d'ajouter une certaine cohérence avec les réponses que nous avons généré de notre côté. Ensuite nous avons lancé l'évaluation.
Ce qu'il se passe :
- chaque question est analysée
- génération de 4 colonnes supplémentaires (les 4 métriques) dans le csv 
- Les scores sont entre 0 et 1, ce sont des scores normalisés, le 1 indique alors le meilleur score possible.

#### **Résultats de l'évaluation sur l'ensemble des questions**
- Nous récupérons notre csv et nous avons décortiqué les résultats dans un notebook dédié.
- Nous avons déjà regardé les scores moyens au global sur les 15 questions :

![alt text](notebooks/graph/Moyenne_metriques_ragas.png)

- Sur ce graphique nous avons déjà de la manière pour une interprétation :

- On voit un score de "answer relevancy", pertinence de la réponse, élevé en moyenne avec 0.91. Pour rappel lors du calcul de cette métrique, le LLM va générer des questions implicites à partir de la réponse, il va comparer les questions avec la question originale et le score est basé sur la similarité sémantique.
    - Cela signifie que les réponses sont bien alignées sémantiquement avec la question. Par contre une réponse peut être pertinente mais fausse.
- Le score de "faitfulness", la fidelité de la réponse, est très bas avec 0.12 en moyenne sur les 15 questions. Cette métrique permet de découper la réponse générée en affirmation factuelle. Pour chaque affirmation, il y a une vérification qu'elles sont bien supportées par au moins un contexte. 
    - Le score atteste que les affirmations de la réponse ne sont pas beaucoup appuyées sur le contexte généré. Cela peut indiquer des hallucinations importantes.
- Le score de "context_precision", les documents récupérés sont-ils utiles, est aussi bas avec 0.24 en moyenne. Pour chaque contexte,le LLM juge “Ce contexte est-il nécessaire pour répondre à la question ?”.
    - Un score de 0.24 signifie beaucoup de documents récupérés et peu pertinents.Le système de retrieval ramène beaucoup de bruit.
- Le score de "context_recall", avons-nous récupéré toutes les infos nécessaires, est bas avec 0.21 en moyenne. Ici le LLM va identifier les informations clés requises pour répondre à la question. Ensuite il va vérifier si elles apparaissent dans le context.
    - 0.21 signifie qu'on ne récupère pas les bons documents ou on ne récupère qu’une petite partie des informations nécessaires.

- En conlusion de la moyenne globale :
- la relevancy élevée montre que le LLM comprend bien la question.
- la faithfulness très basse, il invente ou extrapole.
- la precision basse, le retriever ramène du bruit.
- le recall bas, il manque des infos clés.

#### **Résultats de l'évaluation par type de question**
- Regardons les résultats par type de question :

![alt text](notebooks/graph/Moyenne_metriques_ragas_par_question.png)

On voit avec ce graphique que les scores globaux sont tirés vers le haut par les questions simples :
- Sur des questions factuelles, en posant des questions simples, courtes et précises, le système s'en sort mieux qu'au global mais les scores restent très bas (hors answer relevancy). On devrait avoir des résultats bein supéreiurs sur ce type de question.
- Sur les questions intermédiaires, c'est à dire des questions un peu plus longues, des questions avec des comparaisons simples, les scores se dégradent pour toutes les métriques. On y voit nettement plus d'hallucinations et les réponses ne s'appuyent pas sur le contexte mais de plus en plus sur des recherches internet via le LLM.
- Sur les questions bruitées, cela reste des questions avec des réponses se trouvenat dans notre fichier excel mais elles sont volontairement moins explicites avec des formulations plus complexes, nous avons deux métriques à 0 (faithfulness et context_recall). Cela laisse paraître une mauvaise récupération des documents.

- **Conclusion de cette première évaluation ragas**
En regardant uniquement les réponses de l'interface du chatbot, il arrive à répondre à toutes les questions mais en analysant les réponses attendues et celles du chatbot ainsi que les résultats des métriques, on identifie très vite les limites du modèle actuel.
Les scores démontrent un manque d'efficacité à récupérer les documents utiles pour apporter une réponse cohérente et factuelle et va s'appuyer sur une recherche internet que par notre système RAG.

Nous avons alors regarder comment les documents sont générés et nous avons identifier ce qui pourrait être le problème. 
**Actuellement le modèle prend en compte le fichier excel comme un fichier texte.** En l'état, le modèle prend en compte les données en texte et va les découper, il va alors se "perdre" lors du retrieval et ne va pas être capable de porposer des calculs si par exemple on lui demande de calculer le nombre de points d'une équipe en particulier.

- **Définition de notre nouveau objectif**
Une des étapes d'amélioration va être de créer une base de données pour y déposer notre fichier de statistique, cela va permettre une meilleure organisation et permettre le calcul des données si besoin.
