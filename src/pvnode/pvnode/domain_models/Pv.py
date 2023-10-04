from typing import List, Optional
from pydantic import BaseModel

class PvModel(BaseModel):
    """Represents a single pv data object.
    """
    name: str
    identifier: str
    level: int
    latitude: float
    longitude: float
    address: str
    type: str
    category: str
    profile_identifier: str
    
class PvCollection(BaseModel):
    """Represents a collection of photovoltaics.
    """
    pvs: Optional[List[PvModel]] = None
    
class PvModelMap(BaseModel):
    """Maps a photovoltaic to its pv model.
    """
    pv_map: dict
    
class ScenarioModel(BaseModel):
    """Represents a scenario.
    """
    pvs: List[PvModel]