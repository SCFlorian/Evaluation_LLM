# NETTOYAGE DU FICHIER EXCEL POUR INGESTION AVEC SQL
# =======================
# Librairies nécessaires
# =======================
import pandas as pd
import datetime as dt

# ======================================================================
# Création d'un nouveau fichier pour avoir les informations des joueurs
# ======================================================================
def cleaning_player():
    """On va créer un nouveau fichier afin d'obtenir une fiche d'identité des joueurs avec leur âge et leur équipe"""
    # Chargement du fichier avec les stats par joueur
    df_stats = pd.read_excel(
        "data/raw/regular_NBA.xlsx",
        sheet_name="Données NBA", header=1)
    # Chargement du fichier avec le nom des équipes
    df_name_team = pd.read_excel(
        "data/raw/regular_NBA.xlsx",
        sheet_name="Equipe")
    # On fait une copie du dataframe
    df = df_stats.copy()
    # On choisit les colonnes du fichier statistiques par joueur qui nous intéressent
    df = df[['Player','Age','Team']]
    # On transforme le noms des équipes en dictionnaire
    team_dict = dict(zip(df_name_team["Code"], df_name_team["Nom complet de l'équipe"]))
    # On ajoute les définitions des équipes dans le fichier final
    df["Team_full_name"] = df["Team"].map(team_dict)
    df_player = df

    return df_player
    
# ==============================================================================
# Nettoyage de l'onglet "Données NBA" qui retracent les statistiques par joueur
# ==============================================================================

def cleaning_stats():
    """ On sélectionne les statistiques NBA et on doit procéder à quelques changements,
      notamment la suppression des colonnes vides. Les entêtes étaient décalées alors nous prenons le
      header = 1 et nous enlevons les données que l'on va retrouver dans la table Player. On va renommer
      également des colonnes afin d'avoir une bonne intégration sous PostreSQL.
      """
    df_stats = pd.read_excel(
    "data/raw/regular_NBA.xlsx",
    sheet_name="Données NBA", header=1)
    # Suppression des colonnes vides ou présentent dans l'autre table
    delet_cols = [
        'Team','Age','Unnamed: 45','Unnamed: 46', 'Unnamed: 47',
        'Unnamed: 48', 'Unnamed: 49', 'Unnamed: 50', 'Unnamed: 51','Unnamed: 52']
    # Renommage des colonnes pour avoir une bonne intégration dans notre base PostreSQL
    df_stats_clean = df_stats.drop(columns=delet_cols)
    df_stats_new = df_stats_clean.rename(columns={
    "FG%":"FG_P",
    # Format spécial pour cette colonne qui est en datatime
    dt.time(15, 0): "MIN_15",
    "3PA":"PTS_3",
    "3P%":"PTS_3_P",
    "FT%":"FT_P",
    "+/-":"PLUS_MINUS",
    "AST%":"AST_P",
    "AST/TO":"AST_TO",
    "AST RATIO":"AST_RATIO",
    "OREB%":"OREB_P",
    "DREB%":"DREB_P",
    "REB%":"REB_P",
    "TO RATIO":"TO_RATIO",
    "EFG%":"EFG_P",
    "TS%":"TS_P",
    "USG%":"USG_P"
})
    return df_stats_new

# ========================================================
# Préparation du fichier qui servira dans les métadonnées
# ========================================================

def dict_def_stats():
    """ Chargement du fichier des définitions des colonnes de stats
    (pour intégration plus tard dans les métadonnées)"""
    # On charge le fichier excel    
    df_dict_stats = pd.read_excel(
        "data/raw/regular_NBA.xlsx",
        sheet_name="Dictionnaire des données")
    # on charge une copie du fichier
    df_dict_stats_transform = df_dict_stats.copy()
    # On renomme la colonne qui n'avait pas d'entête
    df_dict_stats_transform = df_dict_stats_transform.rename(columns={
    'Unnamed: 1':'Definition_acronyme'
    })
    # On renomme le noms des acronymes des stats pour caler à la table Stats
    df_dict_clean = df_dict_stats_transform.set_index("Dictionnaire des données").rename({
        "FG%":"FG_P",
        # Format spécial pour cette colonne qui est en datatime
        dt.time(15, 0): "Min_15",
        "3PA":"PTS_3",
        "3P%":"PTS_3_P",
        "FT%":"FT_P",
        "+/-":"PLUS_MINUS",
        "AST%":"AST_P",
        "AST/TO":"AST_TO",
        "AST RATIO":"AST_RATIO",
        "OREB%":"OREB_P",
        "DREB%":"DREB_P",
        "REB%":"REB_P",
        "TO RATIO":"TO_RATIO",
        "EFG%":"EFG_P",
        "TS%":"TS_P",
        "USG%":"USG_P"
    },axis=0)
    df_dict_clean = dict(df_dict_clean)


    return df_dict_clean


