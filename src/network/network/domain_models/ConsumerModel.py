from typing import List, Optional
from pydantic import BaseModel

class ConsumerModel(BaseModel):
    name: str
    identifier: str
    level: int
    latitude: float
    longitude: float
    address: str
    type: str
    category: str
    profile_identifier: str

class ConsumerCollection(BaseModel):
    """Represents a collection of generators.
    """
    consumers: Optional[List[ConsumerModel]] = None