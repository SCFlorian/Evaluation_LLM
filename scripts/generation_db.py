# GENERATION DES TABLES DE LA BDD
# =======================
# Librairies nécessaires
# =======================
from sqlalchemy.orm import sessionmaker
import sys,os
# ================
# Imports du repo
# ================
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.config import DATABASE_URL
from database.creation_db import (Player, Stats, Base, engine)
from database.preprocessing_excel import (cleaning_player, cleaning_stats, dict_def_stats)

def generate_sql_db():
    # ==============================================
    # Récupération des dataframes (après nettoyage)
    # ==============================================
    df_player = cleaning_player()
    df_stats = cleaning_stats()
    # ======================================================
    # Connexion à une session afin de se connecter à la BDD
    # ======================================================
    SessionLocal = sessionmaker(bind=engine)
    # Initialisation de la Class principal avec le moteur sqlalchemy
    Base.metadata.create_all(engine)
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

    # ==========================================================
    # Enregistrement des statistiques par joueur dans une table
    # ==========================================================
    session_stats = SessionLocal()

    for _, row in df_stats.iterrows():
        stats = Stats(
            Player =row["Player"],
            GP =row["GP"],
            W =row["W"],
            L =row["L"],
            Min =row["Min"],
            PTS =row["PTS"],
            FGM =row["FGM"],
            FGA =row["FGA"],
            FG_P =row["FG_P"],
            MIN_15 =row["MIN_15"],
            PTS_3 =row["PTS_3"],
            PTS_3_P =row["PTS_3_P"],
            FTM =row["FTM"],
            FTA =row["FTA"],
            FT_P =row["FT_P"],
            OREB =row["OREB"],
            DREB =row["DREB"],
            REB =row["REB"],
            AST =row["AST"],
            TOV =row["TOV"],
            STL =row["STL"],
            BLK =row["BLK"],
            PF =row["PF"],
            FP =row["FP"],
            DD2 =row["DD2"],
            TD3 =row["TD3"],
            PLUS_MINUS =row["PLUS_MINUS"],
            OFFRTG =row["OFFRTG"],
            DEFRTG =row["DEFRTG"],
            NETRTG =row["NETRTG"],
            AST_P =row["AST_P"],
            AST_TO =row["AST_TO"],
            AST_RATIO =row["AST_RATIO"],
            OREB_P =row["OREB_P"],
            DREB_P =row["DREB_P"],
            REB_P =row["REB_P"],
            TO_RATIO =row["TO_RATIO"],
            EFG_P =row["EFG_P"],
            TS_P =row["TS_P"],
            USG_P =row["USG_P"],
            PACE =row["PACE"],
            PIE =row["PIE"],
            POSS =row["POSS"]
        )
        session_stats.add(stats)

    session_stats.commit()
    session_stats.close()

    print("Données insérées avec SQLAlchemy ORM")
