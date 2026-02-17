# Assistant RAG avec Llama


# Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Structure du projet](#structure-du-projet)
5. [Résultats de l'évaluation sur l'ensemble des questions](#résultats-de-lévaluation-sur-lensemble-des-questions)
6. [Résultats de l'évaluation par type de question](#résultats-de-lévaluation-par-type-de-question)
7. [Conclusion de cette première évaluation ragas](#conclusion-de-cette-première-évaluation-ragas)
8. [Mise en place de la nouvelle structure](#mise-en-place-de-la-nouvelle-structure)
9. [Comparaison entre les 2 systèmes avec les métriques ragas](#comparaison-entre-les-2-systèmes-avec-les-métriques-ragas)
10. [Suivre les performances](#suivre-les-performances)
11. [API & Documentation Swagger](#api--documentation-swagger)
11. [Intéraction avec le chatbot](#intéraction-avec-le-chatbot)

---

Ce projet implémente un assistant virtuel basé sur un modèle Llama, utilisant la technique de Retrieval-Augmented Generation (RAG) pour fournir des réponses précises et contextuelles à partir d'une base de connaissances personnalisée.
L'objectif est de reprendre un prototype réalisé qui était fonctionnel et de procéder à des améliorations afin d'obtenir des meilleurs résultats.
Les améliorations seront visibles avec une comparaison des métriques ragas sur le prototype vs la nouvelle structure du projet.


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
│   └── processed/                             # Création de nouveaux fichiers csv 
│       ├──concat_eval_ragas.csv               # Tableau récapitulatif avec les deux évaluations Ragas
│       ├──first_ragas_results.csv             # Résultats de la première évaluation ragas
│       ├──first_eval_results.csv              # Génération des questions/réponses de la première évaluation
│       ├──second_ragas_results.csv            # Résultats de la deuxième évaluation ragas
│       ├──second_eval_results.csv             # Génération des questions/réponses de la deuxième évaluation
│   └── raw/                                   # Les éléments de base du projet
│       ├──Reddit 1.pdf                        # Premier fichier Reddit
│       ├──Reddit 2.pdf                        # Deuxième fichier Reddit
│       ├──Reddit 3.pdf                        # Troisième fichier Reddit
│       ├──Reddit 4.pdf                        # Quatrième fichier Reddit
│       ├──regular NBA.xlsx                    # Fichier excel avec les statistiques par joueur
├── database/                                  # Création et génération de la BDD
│   ├──creation_db.py                          # Script avec les classes de nos tables
│   ├──preprocessing_excel.py                  # Script préparant les fichiers excel (dont nettoyage) pour la BDD
│   ├──sql_tool.py                             # Préparation de la chaîne pour récupérer les informations depuis la BDD
├── notebooks/                                 # Dossier contenant les notebooks pour une meilleure compréhension des données
│   └── graph/                                 # Dossier contenant les graphiques utilisés pour la documentation
│   ├──notebook_analyse_excel.ipynb            # Notebook sur la préparation du fichier excel pour les évaluations
│   ├──notebook_evaluation_ragas.ipynb         # Notebook sur la préparation des résultats des évaluations des métriques ragas
├── rag/                                       # Scripts contenant les fonctions du système RAG
│   ├──config.py                               # Script contenant les configurations (le nom des paramètres, des modèles etc)
│   ├──creation_llm.py                         # Script contenant la création du LLM (initialisation du modèle, génération de la réponse)
│   ├──data_loader.py                          # Script contenant le chargement des documents
│   ├──embeddings.py                           # Script contenant les différentes fonctions allant de la création des découpages à la création des vecteurs
│   ├──retrieval.py                            # Script contenant la recherche dans la documentation
│   ├──router.py                               # Script contenant le choix par un "agent" de décider si le RAG va chercher les infos dans la BDD ou la base vectorielle
│   ├──vector_store.py                         # Script contenant l'enregistrement des vecteurs
├── scripts/                                   # Scripts généraux
│   └── evaluations/                           # Dossier contenant les scripts des évaluations des métriques ragas
│       ├──new_system                          # À l'intérieur on retrouve un fichier de génération des questions/réponses et un fichier évaluant les métriques pour le nouveau projet
│           ├──second_generation_answers.py    # Génération des questions/réponses pour la deuxième évaluation
│           ├──second_ragas_evaluation.py      # Génération des métriques ragas pour la deuxième évaluation
│       ├──prototype                           # À l'intérieur on retrouve un fichier de génération des questions/réponses et un fichier évaluant les métriques pour le prototype
│           ├──second_generation_answers.py    # Génération des questions/réponses pour la première évaluation
│           ├──second_ragas_evaluation.py      # Génération des métriques ragas pour la première évaluation
│   ├──build_index.py                          # Script de création de la base vectorielle
│   ├──chat.py                                 # Script de génération de la réponse du chatbot
│   ├──generation_db.py                        # Script de génération de la base de données
├── tests/                                     # Dossier avec l'enregistrement de notre base vectorielle
│   ├──valisation_pydantic.py                  # Tests d'entrées/sorties et des chunk avec Pydantic
├── vector_db/                                 # Dossier avec l'enregistrement de notre base vectorielle
│   ├──faiss_index.pkl                         # Les documents découpés en format pkl
│   ├──faiss_index.faiss                       # la base d'index FAISS
├── .env                                       # Enregistrement des informations qui ne doivent pas être publiées
├── .gitignore                                 # Permet de ne pas afficher les éléments sélectionnés sur GitHub
├── app.py                                     # Orchestre la vectorisation et la sauvegarde
├── InterfaceChat.py                           # Script pour le lancement de l'API et de l'interface avec Streamlit
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
- Les tables sont désormais à jour. Si vous avez installé pgAdmin, vous pouvez visualiser facilement l'intégration des données.

#### Pour lancer le projet, vous avez plusieurs options :

- La méthode privilégiée pour exécuter l'interface est **Docker**, garantissant un environnement isolé et stable.
1. Prérequis
- Docker installé sur votre machine.
- Une clé API Groq active.
2. Construction (Build)
- Construction de l'image
```
docker build -t sportsee-streamlit .
```
3. Lancement (Run)
- Démarrez le conteneur en lui passant les variables d'environnement :
```
docker run -d \
  --name sportsee-streamlit \
  -p 7860:7860 \
  --env-file .env \
  sportsee-streamlit
```

On peut également générer le projet via la documentation swagger de FastAPI : détails dans [API & Documentation Swagger](#api--documentation-swagger)


# Rapport technique - du prototype au système actuel
## Reprise d'un prototype existant

Pour mener à bien cette mission, nous avons eu à disposition un prototype du chatbot. Dans un premier temps l'objectif a été de comprendre ce qui a été fait, quelle structure nous avons et nous sommes passé ensuite à une évaluation du système actuel via une évaluation des métriques Ragas.

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

L'entreprise nous a signalé que les réponses n'étaient pas suffisantes pour eux. Elle a confié que les résultats sur les archives textuelles étaient encourageantes mais ils deviennent moins bons en interrogeant avec des questions plus précises sur les statistiques par exemple.
Afin de s'en rendre compte nous allons évaluer le système avec les métriques Ragas pour se faire notre propre avis.

- **Génération des questions/réponses**

L'objectif est d'évaluer le modèle avec ragas, pour cela il faut avoir un jeu de questions/réponses pour obtenir les métriques. 
Création du fichier **generation_answers.py** dans un nouveau dossier scripts/evaluation (vous le trouverez dans le dossier prototype)

On y retouve 20 questions et 20 réponses (humaines) portant sur le fichier excel avec plusieurs degrés de complexité :
- Questions faciles (valeurs directes)
- Questions intermédiaires (comparaison simple)
- Questions plus difficiles (questions bruitées)
- Vu la demande de l'entreprise, on a réalisé plus de question sur la partie statistique :
    - 14 questions sur le fichier excel
    - 3 questions sur les fichiers reddit
    - 3 questions sur le couple excel/reddit
    
**À la suite de ces questions, nous appelons notre système pour obtenir les réponses du chatbot.**

Dans le fichier csv généré (dans le dossier resultat_evaluation.csv) nous retrouvons en plus des questions/réponses (humaines + chatbot) :
- la liste des contextes utilisés par le chatbot pour fournir une réponse (obligatoire pour ragas)
- le numéro des documents sélectionnés
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

- Sur ce graphique nous avons déjà de la matière pour une interprétation :

- On voit un score de "answer relevancy", pertinence de la réponse, élevé en moyenne avec 0.92. Pour rappel lors du calcul de cette métrique, le LLM va générer des questions implicites à partir de la réponse, il va comparer les questions avec la question originale et le score est basé sur la similarité sémantique.
    - Cela signifie que les réponses sont bien alignées sémantiquement avec la question. Par contre une réponse peut être pertinente mais fausse.
- Le score de "faitfulness", la fidelité de la réponse, est très bas avec 0.17 en moyenne sur les 20 questions. Cette métrique permet de découper la réponse générée en affirmation factuelle. Pour chaque affirmation, il y a une vérification qu'elles soient bien supportées par au moins un contexte. 
    - Le score atteste que les affirmations de la réponse ne sont pas beaucoup appuyées sur le contexte généré. Cela peut indiquer des hallucinations importantes.
- Le score de "context_precision", les documents récupérés sont-ils utiles, est aussi bas avec 0.20 en moyenne. Pour chaque contexte,le LLM juge “Ce contexte est-il nécessaire pour répondre à la question ?”.
    - Un score de 0.20 signifie beaucoup de documents récupérés et peu pertinents. Le système de retrieval ramène beaucoup de bruit.
- Le score de "context_recall", avons-nous récupéré toutes les infos nécessaires, est bas avec 0.33 en moyenne. Ici le LLM va identifier les informations clés requises pour répondre à la question. Ensuite il va vérifier si elles apparaissent dans le context.
    - 0.33 signifie qu'on ne récupère pas les bons documents ou on ne récupère qu’une petite partie des informations nécessaires.

- En conlusion de la moyenne globale :
- la relevancy élevée montre que le LLM comprend bien la question.
- la faithfulness très basse, il invente ou extrapole.
- la precision basse, le retriever ramène du bruit.
- le recall bas, il manque des infos clés.

#### **Résultats de l'évaluation par type de question**
- Regardons les résultats par type de question :

![alt text](notebooks/graph/Moyenne_metriques_ragas_par_question.png)

On voit avec ce graphique que les scores globaux sont tirés vers le haut par les questions simples :
- Sur des questions factuelles, en posant des questions simples, courtes et précises, le système s'en sort légèrement mieux qu'au global mais les scores restent très bas (hors answer relevancy). On devrait avoir des résultats bein supéreiurs sur ce type de question.
- Sur les questions compliquées et bruitées, c'est à dire des questions un peu plus longues, et des questions volontairement moins explicites, les scores se dégradent. On y voit nettement plus d'hallucinations et les réponses ne s'appuyent pas sur le contexte mais de plus en plus sur des recherches internet via le LLM.

- **Conclusion de cette première évaluation ragas**
En regardant uniquement les réponses de l'interface du chatbot, il arrive à répondre à toutes les questions mais en analysant les réponses attendues et celles du chatbot ainsi que les résultats des métriques, on identifie très vite les limites du modèle actuel.
Les scores démontrent un manque d'efficacité à récupérer les documents utiles pour apporter une réponse cohérente et factuelle et va s'appuyer sur une recherche internet que par notre système RAG.

Nous avons alors regardé comment les documents sont générés et nous avons identifié ce qui pourrait être le problème. 
**Actuellement le modèle prend en compte le fichier excel comme un fichier texte.** En l'état, le modèle prend en compte les données en texte et va les découper, il va alors se "perdre" lors du retrieval et ne va pas être capable de porposer des calculs si par exemple on lui demande de calculer le nombre de points d'une équipe en particulier.

## Mise en place de la nouvelle structure

L'idée n'a pas été de repartir totalement d'une page blanche. Il y a désormais une nouvelle structure avec des fonctions bien séparées et plus modulables.

1. **Technologies utilisées**
- Language : Python
- Interface : Streamlit
- LLM : utilisation de Groq et choix du modèle llama-3.3-70b-versatile
    - Groq va nous permettre de pouvoir utilsier d'autres modèles si besoin et surtout permet une meilleure visibilité sur les coûts générés
- Embeddings : utilisation de HuggingFaceEmbeddings pour la création des vecteurs et choix de l'index FLatL2 de FAISS pour la base vectorielle
- Orchestration : Langchain
- Gestion des dépendances : environnement poetry

2. **Définition de notre nouveau objectif**
Dans un premier temps nous avons amélioré la structure de notre projet. Ensuite nous avons ajouté des améliorations comme la mise en place d'une base de données et une méthode supplémentaire de récupération des données. Nous verrons également comment nous suivons les résultats et les performances du système.

3. **Nouvelle organisation du projet**

Désormais nous avons une organisation plus fluide, nous avons mis en place par exemple :
- un environnement géré par poetry
- un dossier rag qui va être le coeur du projet avec tous les scripts nécessaires pour faire tourner le système RAG
- un dossier database qui va permttre la création de notre base de données
- un dossier `scripts` avec 3 scripts principaux qui vont regrouper les fonctions principales :
    - build_index qui va construire ou reconstruire la base vectorielle
    - chat qui permet de générer la réponse du chatbot
    - generation_db qui va permettre de créer ou mettre à jour la base de données SQL
- Mise en place d'un fichier app pour la mise en place de notre API Rest qui est en plus de l'interface Streamlit.

4. **Mise en place de la base de données**

Nous avons détaillé l'installation de la base de données un peu plus haut. Nous avons fait le choix d'utiliser une base en local pour le moement avec PostreSQL. 
Après avoir initialisée et générée la base de données comme indiqué en introduction, nous avons une BDD sur laquelle s'appuyer.
Dans le pipeline de la BDD, avant d'être intégrées, les données du fichier excel sont préalablement nettoyées automatiquement avec le script `preprocessing_excel.py`.

Nous avons désormais 2 tables sur lesquelles notre système RAG va pouvoir prendre de l'information.

- La table `player`, où l'on va retrouver les informations d'un joueur de la NBA avec son âge et l'équipe où il joue.

![alt text](notebooks/screenshot/table_player.png)

- La table `stats`, où l'on va retrouver les statistiques par jour (nombre de matchs, nombre de points etc).

![alt text](notebooks/screenshot/table_stats.png)

- Dans la table `stats`, nous voyons que les catégories sont des acronymes alors nous retrouverons la définition de ces derniers dans les métadonnées pour aider le modèle à ne pas se tromper lorsqu'il sélectionnera une colonne en particulier.

5. **Mise en place d'un routeur pour sélectionner les bonnes données**

Maintenant nous avons 2 sources de données, une provenant d'une base vectorielle et une autre d'une base de données.

L'approche n'est plus la même que dans le prototype, il faut mettre en place un **agent** qui va prendre la décision si la question répond à un besoin pour une requête SQL, une récupération dans les vecteurs ou dans les 2 bases.

C'est le script `routeur` qui va prendre cette décision via un prompt strcturé dans une chaîne LCEL.
Voici le prompt utilisé pour la génération du choix :
```
 template = """
        Tu es un expert en classification de questions pour un assistant NBA.
        Ton rôle est d'orienter la question vers la bonne source de données.

        SOURCES DISPONIBLES :

        1. "SQL" : Pour les STATISTIQUES PURES, les RECORDS et les FAITS SIMPLES.
           - Utilise ceci pour : Moyennes, totaux, classements, âges, équipes actuelles.
           - Mots-clés : "Combien", "Score", "Stats", "Meilleur marqueur", "Qui a le plus de...".
           - Ex: "Combien de points a Lebron ?", "Qui est le meilleur rebondeur ?", "Dans quelle équipe joue Curry ?"
           - Si la question demande un classement, un "meilleur", un "top", ou une exclusion basée sur des chiffres (matchs, points), C'EST DU SQL.
            Même si le mot "restant" est utilisé.

        2. "VECTOR" : Pour le TEXTE, l'HISTOIRE, les RÈGLES et les CONDITIONS SPÉCIFIQUES.
           - Utilise ceci pour : Règlements, explications ("pourquoi", "comment"), avis de fans, rumeurs.
           - IMPORTANT : Si une question demande "Qui a gagné..." avec une CONDITION NARRATIVE ou un CONTEXTE HISTORIQUE (ex: "sans avantage du terrain", "le plus jeune MVP", "après une blessure", "le plus petit joueur"), c'est du VECTOR. La base SQL ne contient que des noms et des chiffres, pas ces détails.
           - Ex: "Quelles sont les règles des playoffs ?", "Quelle équipe a gagné en 1995 sans l'avantage du terrain ?", "Que pensent les fans de Gobert ?"

        3. "BOTH" : Uniquement si la question demande CLAIREMENT deux choses distinctes (Chiffre + Texte).
           - Ex: "Donne moi les stats de Wembanyama et une analyse de son impact médiatique."

        Instructions :
        - Analyse la question ci-dessous.
        - Réponds UNIQUEMENT par un seul mot : SQL, VECTOR, ou BOTH.

        Question utilisateur : {question}
        Catégorie :
        """
```
En fonction de ce que va choisir cet "agent", dans le script "chat.py" nous avons mis en place la marche à suivre en cas de choix de la base SQL, des vecteurs ou les deux.

Exemple pour la base SQL :
```
            # BLOC SQL
            # =========
            if route in ["SQL", "BOTH"]:
                with logfire.span("2. Exécution Requête SQL"):
                    raw_data = self.sql_tool.run_query(question)
                    used_definitions = df_dict_clean
                    glossary_text = ", ".join([f"{k}={v}" for k, v in df_dict_clean.items()])
                    sources_finales.append({"type": "database", "data": raw_data})
                    
                    sql_section = (
                        f"DONNÉES SQL (SOURCE OFFICIELLE) : {raw_data}\n"
                        f"CONSIGNE TECHNIQUE : Ces données sont le résultat brut d'une requête SQL exécutée spécifiquement pour répondre à la question : '{question}'.\n"
                        f"AIDE GLOSSAIRE : {glossary_text}\n"
                        f"RÈGLE D'INTERPRÉTATION : \n"
                        f"- Si la question demande un classement ou un superlatif, et que tu ne vois que quelques résultats, c'est NORMAL (LIMIT SQL appliqué).\n"
                        f"- N'indique pas que les données viennent de la base SQL ou autre.\n"
                        f"- Ne dis JAMAIS 'je ne peux pas savoir'. Fais confiance à ce résultat.\n")
```

Ensuite la réponse sera reformulée par le LLM.

6. **Évaluation de notre nouveau système**

Nous avons testé le nouveau système RAG avec les 20 mêmes questions/réponses pour pouvoir comparer les deux.

On commence par générer `second_generation_answers.py` :

```
python -m scripts.evaluation.new_system.second_generation_answers
```

Lorsque nous avons la **réponse du LLM** en plus des questions/réponses, on lance `second_ragas_evaluation.py` :

```
python -m scripts.evaluation.new_system.second_ragas_eveluation
```

7. **Résultats de la seconde évaluation ragas**

#### Moyenne global des métriques

![alt text](notebooks/graph/Moyenne_metriques_ragas_seconde_eval.png)

- Sur l'ensemble des 4 métriques, nous avons des résultats solides qui démontrent des réponses cohérentes et documentés sur les 20 questions que nous avons posé.

#### Moyenne par type de question

![alt text](notebooks/graph/Moyenne_metriques_ragas_par_question_seconde_eval.png)

On apercoit une certaine logique avec :
- les meilleurs scores pour les questions simples.
- une légère diminution pour les questions un peu plus compliquées.
- Et une baisse un peu plus prononcé pour les questions bruitées par rapport au simple.

On note facilement pour les perspectives que nous devons encore amélioré notre système pour sécuriser les questions bruitées.

# Comparaison entre les 2 systèmes avec les métriques ragas

Prenons la moyenne des 20 questions :

![alt text](notebooks/graph/Moyenne_metriques_ragas_type_eval.png)

Nous voyons clairement une amélioration significatve de notre modèle.
- Sur faitfulness, context_recall et context_precision, les métriques se sont améliorés et prouvent :
    - une meilleur qualité de récupération des documents
    - les docuements récupérés sont utiles
    - les affirmations des réponses sont basées sur des faits
- Le score pour answer_relevancy a baissé par rapport à la première évaluation :
    - mais il reste bon en étant supérieur à 0.80
    - le score de la première évaluation peut être dû au fait que le système était moins bien cadré, il allait chercher des informations sur internet, les réponses sont fausses mais sémantiquements proches.
    - dans la deuxième évaluation le score a baissé mais la réponse se base uniquement sur les documents récupérés et répond de manière plus pertinent à la question.

# Suivre les performances

Nous avons décidé d'inclure Pydantic Logfire. Logfire est une plateforme qui permet de :
- collecter les logs (messages générés par un programme),
- visualiser ce qui se passe dans une application en temps réel,
- détecter et diagnostiquer les erreurs et bugs,
- analyser les performances d’un système.

Logfire est un outil pour surveiller, comprendre et déboguer une application grâce aux logs.

### **Mise en place dans notre système RAG** 

Afin de pouvoir visualiser pas à pas le fonctionnement de la chaîne RAG/LLM lors de son exécution. Il va nous permettre également d'avoir des dashboard pour s'assurer des bonnes performances de notre modèle.

Pour bénéficier de Logfire, il faut avoir créer un compte :
```
https://logfire.pydantic.dev
```

Il faut également l'initier, lors de votre premier lancement sur un projet, il va vous demander de faire quelques actions, suivi les instructions.

Nous avons utiliser les commandes principales de Logfire pour tracker notre projet :

```
# Configure Logfire avec les paramètres par défaut.
# Cette instruction initialise la connexion à la plateforme Logfire et permet
# de commencer la collecte et l’envoi des logs générés par l’application.
logfire.configure()

# Active l’instrumentation automatique de Pydantic.
# Cette fonctionnalité permet d’enregistrer les opérations liées à la validation
# des données, notamment les succès et les erreurs de validation des modèles.
# Cela facilite le débogage et le suivi des flux de données dans l’application.
logfire.instrument_pydantic()

# Active la collecte des métriques système.
# Cette instruction permet de surveiller les ressources système telles que
# l’utilisation du CPU, de la mémoire et d’autres indicateurs de performance.
# Ces informations sont utiles pour analyser les performances et détecter
# d’éventuels problèmes liés à l’exécution de l’application.
logfire.instrument_system_metrics()

# Crée un span Logfire pour tracer l’exécution d’un bloc de code.
# Un span représente une unité de travail ou une opération spécifique
# dans l’application, par exemple une requête, un calcul ou un appel de fonction.
# Il permet de mesurer la durée d’exécution et d’enregistrer des informations
# associées à cette opération pour faciliter l’analyse et le débogage.
with logfire.span("Router Decision"):
```

**Utilisation de logfire span** dans le `chat.py` et le `second_evaluation_ragas.py` :

### Dans le premier afin d'avoir un suivi clair allant de la question à la réponse du chatbot :

![alt text](notebooks/screenshot/logfire_traitement_question.png)

- Nous pouvons suivre en détail ce qu'il s'est passé et le pipeline passe par la validation Pydantic. 
- Il est possible de voir par exemple le détail de la réponse, quel contexte a été sélectionné :

<p align="left">
  <img src="notebooks/screenshot/output_context.png" width="55%" alt="output_context">
</p>

### Dans le deuxième afin d'avoir un suivi des scores des métriques ragas disponible :

- par question :

![alt text](notebooks/screenshot/logfire_questions_ragas.png)

- au global :

<p align="left">
  <img src="notebooks/screenshot/logfire_ragas_total.png" width="35%" alt="Image_métriques_ragas">
</p>

### Visualation avec des dashboard

Logfire nous permet de suivre plusieurs élements de notre projet comme :

- process count & system CPU

![alt text](notebooks/screenshot/systeme_dashboard.png)

- Les erreurs rencontrées

![alt text](notebooks/screenshot/erreurs_dashboard.png)

### Possibilité de créer ses propres dashboard en créant des reqêutes SQL dans "explore" puis les mettre en dashboard

- Nombre de tokens utilisés :

![alt text](notebooks/screenshot/tokens_dashboard.png)

- Comparaison du temps par question sur la dernière question posée vs la moyenne du temps par question :

<p align="left">
  <img src="notebooks/screenshot/temps_dashboard.png" width="35%" alt="Dashboard des temps de réponse">
</p>

### Affichage si le schéma pydantic n'est pas respecté :

<p align="left">
  <img src="notebooks/screenshot/erreur_pydantic.png" width="155%" alt="Erreur_pydantic">
</p>

# API & Documentation Swagger

Swagger est un outil qui permet de documenter, décrire et tester une API REST de manière claire et interactive.
Plus précisément, la documentation Swagger est une description structurée d’une API qui montre tous les endpoints disponibles, leurs paramètres, les requêtes possibles et les réponses retournées.

Dans notre API qui repose sur `FastAPI` nous avons 4 endpoints :

- `@app.get("/health")` : va permettre de s'assurer que l'API est opérationnel
- `@app.post("/ask")` : va permettre d'intéragir avec le chatbot
- `@app.post("/rebuild_index")` : va permettre la construction ou re-construction de la base vectorielle
- `@app.post('/rebuild_SQL_Base')` : va permettre la construction ou re-construction de la base de données

#### Documentation Swagger :

<p align="left">
  <img src="notebooks/screenshot/doc_swagger.png" width="55%" alt="doc_swagger">
</p>

# Intéraction avec le chatbot

Plusieurs options s'offrent à vous pour intéragir avec le chatbot :

## Utilisation de Postman

Pour tester l'API et sauvegarder vos requêtes, vous pouvez utiliser Postman :

1. **Configurez la requête :**
   - Créez une nouvelle requête.
   - Choisissez la méthode **POST**.
   - Entrez l'URL : `http://localhost:7860/ask`

2. **Ajouter le contenu (Body) :**
   - Allez dans l'onglet **Body**.
   - Sélectionnez **raw**.
   - Dans le menu déroulant à droite (souvent sur "Text"), choisissez **JSON**.
   - Collez votre question au format JSON :
     ```json
     {
       "question": "Qui est le meilleur marqueur de la NBA en ce moment ?"
     }
     ```

3. **Lancer :**
   - Cliquez sur **Send**.
   - La réponse du chatbot apparaîtra en bas dans la fenêtre de réponse.

*Note : Vous pouvez procéder de la même manière pour l'endpoint `/rebuild_index` ou `/rebuild_SQL_Base` (Méthode POST) afin de mettre à jour les données.*

4. Exemple pour le endpoint `ask`

<p align="left">
  <img src="notebooks/screenshot/postman_ask.png" width="75%" alt="postman_ask">
</p>

## Utilisation de Streamlit

Vous avez la possibilité d'utiliser l'interface de Streamlit afin d'avoir une utilisation plus proche de ce que l'utilisateur final aura entre les mains.

Depuis votre terminal (vérifiez bien d'être dans le bon projet) :

```
streamlit run InterfaceChat.py
```

Votre navigateur va s'ouvrir et vous aurez la possibilité d'échanger avec le chatbot :

<p align="left">
  <img src="notebooks/screenshot/interfacechat_reponse.png" width="65%" alt="interfacechat_reponse">
</p>