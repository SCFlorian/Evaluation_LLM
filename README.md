# Assistant RAG avec Mistral

Ce projet implémente un assistant virtuel basé sur le modèle Mistral, utilisant la technique de Retrieval-Augmented Generation (RAG) pour fournir des réponses précises et contextuelles à partir d'une base de connaissances personnalisée.
L'objectif est de reprendre un prototype réalisé qui était fonctionnel et de procéder à quelques améliorations afin d'obtenir des meilleurs résultats.
Les améliorations seront visibles avec une comparaison des métriques ragas sur le prototype vs la nouvelle structuration du projet.

## Fonctionnalités

- 🗄️ **Recherche sémantique** avec FAISS pour trouver les documents pertinents (PDF à disposition)
- 🗄️ **Recherche dans une base relationnelle** avec une base de données PostreSQL pour effectuer une recherche des éléments chiffrés.
- 🔍 **Choix du système** pour sélectionner le bon type de donnée à prendre.
- 🤖 **Génération de réponses** avec les modèles Mistral (Small ou Large)
- ⚙️ **Paramètres personnalisables** (modèle, nombre de documents, score minimum)

## Prérequis

- Python 3.9+ 
- Clé API Mistral (obtenue sur [console.mistral.ai](https://console.mistral.ai/))
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
MISTRAL_API_KEY=votre_clé_api_mistral
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
## Utilisation

### 1. Ajouter des documents

Placez vos documents dans le dossier `data/raw`.
Deux formats sont suportés pour le projet, il est possible de placer des documents en PDF ainsi que des fichiers excel.
- Les documents en PDF seront transformés et enregistrés dans une base vectorielle.
- Les fichiers excel seront nettoyés et ajoutés dans une base de données relationnelle (PostreSQL utilisé ici).
- Pour maintenir une cohérence et une fiabilité dans nos données, les fichiers excel doivent respecter un certain format (vous pouvez par exemple celui utilisé  dans data/raw).


### 2. Enregistrement des documents
#### Indexer les documents (PDF)

Exécutez le script d'indexation pour traiter les documents et créer l'index FAISS :

```bash
python build_index.py
```
Le fichier va s'appuyer sur les fonctions se trouvant dans **vector_store** & **embeddings**
Ce script va :
1. Charger les documents depuis le dossier `data/raw` avec le script data_loader.
2. Découper les documents en chunks en appelant le script embeddings.
Une fois le texte extrait (en mémoire après lancement de l’indexer,) il est trop long pour être envoyé tel quel à un LLM. Il faut le découper en morceaux digeste pour le modèle.

Utilisation de `Langchain` avec `RecursiveCharacterTextSplitter`

**La stratégie utilisée ici :**

- **`CHUNK_SIZE = 1500`** : Chaque morceau fait environ 1500 caractères (environ 300-400 mots).
- **`CHUNK_OVERLAP = 150`** : Il y a un chevauchement de 150 caractères entre deux morceaux consécutifs.

 Cela permet d’éviter de couper une phrase importante en plein milieu. Si une phrase est coupée, la fin se retrouvera au début du morceau suivant grâce à l'overlap.
3. Générer des embeddings avec Mistral
**Script :** `rag/embeddings.py`
C'est l'étape de traduction. L'ordinateur ne comprend pas le texte, il comprend les chiffres.
- **Outil :** API Mistral (`mistral-embed`).
- **Action :** Chaque découpage de texte est envoyé à Mistral, qui renvoie une liste de nombres (un vecteur) représentant le **sens** du texte.
4. Créer un index FAISS pour la recherche sémantique
**Script :** `rag/vector_store.py`
- **Outil :** `FAISS` (Facebook AI Similarity Search).
- **Action :** Tous ces vecteurs sont stockés dans un fichier `vector_db/faiss_index.idx`. C'est une base de données ultra-rapide optimisée pour trouver les vecteurs "voisins".
- **Métadonnées :** En plus du vecteur, le script stocke le lien vers le fichier source (`filename: "Reddit 1.pdf"`, `page: 2`).
- **`IndexFlatIP`** : Produit scalaire (cosine similarity après normalisation). Il fournit des résultats de recherche de voisins les plus proches exacts, ce qui le rend adapté aux applications où la précision est essentielle. le **produit scalaire** sert tout simplement à mesurer à quel point deux vecteurs se ressemblent.
Pourquoi on utilise ça (au lieu de la distance) ? Le produit scalaire mesure l’**alignement.** Et dans les embeddings modernes (texte, images, IA) : des choses similaires pointent dans la même direction dans l’espace.
5. Sauvegarder l'index et les chunks dans le dossier `vector_db/`

#### Enregistrements des éléments chiffrés

L'enregistrement des datas dans la base données se fait dans une base PostreSQL en local.
1. Connexion à une base PostreSQL
Choix de la BDD PostreSQL pour sa simplicité avec l'ORM SQLAlchemy.
Création d'une bDD en local :
a. Ouvrez votre terminal puis lancez les commandes une à une :
```
psql
CREATE DATABASE sportsee_nba_stats;
CREATE USER sportsee_user WITH PASSWORD '***';
GRANT ALL PRIVILEGES ON DATABASE sportsee_nba_stats TO sportsee_user;
ALTER DATABASE sportsee_nba_stats OWNER TO sportsee_user;
```
b. Accès à la BDD
```
psql -U sportsee_user -d sportsee_nba_stats
```
2. Initialisation de la base avec `database/creation_db`

Ce script va nous permettre d'initialiser notre base afin qu'elle soit accessible. On utilise PostreSQL avc l'ORM SQLAlchemy pour faire le lien netre Python et PostrezSQL.
On va y créer deux tables :
- la table player : retrace les informations des joueurs (nom, âge, équipe)
- la table stats : retrace les performances statistiques de chaque joueur.
Exemple pour la table player :
```
class Player(Base):
    """ Préparation d'une table avec les informations clés des joueurs (nom, âge) et leur équipe."""
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    name = Column(String,nullable=False, unique=True)
    age = Column(Integer)
    acronym_team = Column(String)
    team = Column(String)

    stats = relationship("Stats", back_populates="player_relation")
```
3. Nettoyage des fichiers excel
Avant de pouvoir récupérer les informations dans les tables, il y a quelques ajustements à réaliser sur le fichier excel.
- On doit procéder à du nettoyage sur le dataframe des statistiques des joueurs comme la suppression de colonnes vides ou encore le renommage de certaines colonnes.
- On doit créer un fichier player car il n'existe pas en tant que tel dans les informations données par l'entreprise.
- On prépare un fichier avec la définition des acronymes du noms des varibales statistiques pour qu'elles soient visibles dans les métadonnées.

4. Lancement de `generation_db.py`
Ce script va faire le lien entre le script creation_db et va permettre d'envoyer les données dans la BDD.
- A l'interieur il est indiqué de prendre chaque ligne des nouveaux fichiers excel et de les ajouter.
Exemple pour la table player :
```
# =====================================================
# Enregistrement du nom des équipes NBA dans une table
# =====================================================
session_player = SessionLocal()
for _, row in df_player.iterrows():
    team = Player(
        name=row["Player"],
        age =row["Age"],
        acronym_team = row["Team"],
        team = row["Team_full_name"]
    )
    session_player.add(team)

session_player.commit()
session_player.close()
```
- Les tables sont désormais à jour. Si vous avez installé pgAdmin, vous pouvz siualsier facilement l'intégration des données.

