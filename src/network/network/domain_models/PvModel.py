from typing import List, Optional
from pydantic import BaseModel

class PvModel(BaseModel):
    Name: str
    Identifier: str
    Level: int
    Latitude: float
    Longitude: float
    Address: str
    Type: str
    Category: str
    ProfileIdentifier: str
    
class PvCollection(BaseModel):
    """Represents a collection of photovoltaics.
    """
    Pvs: Optional[List[PvModel]] = None