from pydantic import BaseModel
from typing import List, Optional

class VeilleRequest(BaseModel):
    requetes: List[str]
    jours: int = 180
    max_repos: int = 300

class VeilleResponse(BaseModel):
    status: str
    count: int
    rapport_html: str
    timestamp: str
