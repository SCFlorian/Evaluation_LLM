    # CREATION DE NOTRE BASE DE DONNÉES
# =======================
# Librairies nécessaires
# =======================
from sqlalchemy import (create_engine, Column, Integer, Float, String, ForeignKey)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.config import DATABASE_URL
# ======================
# Préparation de la BDD
# ======================
# Prend l'URL de connexion et renvoie un moteur sqlalchemy
# echo=True permet la journalisation
engine = create_engine(DATABASE_URL, echo=True)
# Connexion à une session afin de se connecter à la BDD
SessionLocal = sessionmaker(bind=engine)
# Création de la classe principale de tous les modèles des tables
Base = declarative_base()
# ==========================
# Préparation de nos tables
# ==========================
class Player(Base):
    """ Préparation d'une table avec les informations clés des joueurs (nom, âge) et leur équipe."""
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    name = Column(String,nullable=False, unique=True)
    age = Column(Integer)
    acronym_team = Column(String)
    team = Column(String)

    stats = relationship("Stats", back_populates="player_relation")
    
class Stats(Base):
    """ Table des statistiques NBA par joueur."""
    __tablename__= "stats"
    id = Column(Integer, primary_key=True)
    Player = Column(String, ForeignKey('player.name'), nullable=False)
    GP = Column(Integer)
    W = Column(Integer)
    L = Column(Integer)
    Min = Column(Float)
    PTS = Column(Integer)
    FGM = Column(Integer)
    FGA = Column(Integer)
    FG_P = Column(Float)
    MIN_15 = Column(Integer)
    PTS_3 = Column(Integer)
    PTS_3_P = Column(Float)
    FTM = Column(Integer)
    FTA = Column(Integer)
    FT_P = Column(Float)
    OREB = Column(Integer)
    DREB = Column(Integer)
    REB = Column(Integer)
    AST = Column(Integer)
    TOV = Column(Integer)
    STL = Column(Integer)
    BLK = Column(Integer)
    PF = Column(Integer)
    FP = Column(Integer)
    DD2 = Column(Integer)
    TD3 = Column(Integer)
    PLUS_MINUS = Column(Float)
    OFFRTG = Column(Float)
    DEFRTG = Column(Float)
    NETRTG = Column(Float)
    AST_P = Column(Float)
    AST_TO = Column(Float)
    AST_RATIO = Column(Float)
    OREB_P = Column(Float)
    DREB_P = Column(Float)
    REB_P = Column(Float)
    TO_RATIO = Column(Integer)
    EFG_P = Column(Float)
    TS_P = Column(Float)
    USG_P = Column(Float)
    PACE = Column(Float)
    PIE = Column(Float)
    POSS = Column(Float)

    player_relation = relationship("Player", back_populates="stats")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Base de données et tables créées avec succès.")