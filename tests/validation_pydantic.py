# VALIDATION PYDANTIC
# =======================
# Librairies nécessaires
# =======================
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# 1. Ce qu'on vérifie en entrée
class InputData(BaseModel):
    question: str = Field(..., min_length=2, description="La question ne doit pas être vide")

# 2. Ce qu'on vérifie en sortie
class OutputData(BaseModel):
    answer: str = Field(..., min_length=1, description="La réponse finale")
    route: str = Field(..., pattern="^(SQL|VECTOR|BOTH)$", description="La route utilisée")
    sources: List[Any] = Field(..., description="Liste des documents sources (même vide)")
    # On autorise le reste (context, definitions...) sans planter si ça change
    class Config:
        extra = "ignore"

# 2. Ce qu'on vérifie pour le découpage des données
class ChunkGuard(BaseModel):
    """Vérifie qu'un morceau de texte est valide avant indexation"""
    text: str = Field(..., min_length=1)
    metadata: Dict