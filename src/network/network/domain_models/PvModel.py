from typing import List, Optional
from pydantic import BaseModel

class PvModel(BaseModel):
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