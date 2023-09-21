from typing import List, Optional
from pydantic import BaseModel

class ConsumerModel(BaseModel):
    """Represents a single consumer data object.
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

class ConsumerCollection(BaseModel):
    """Represents a collection of consumers.
    """
    consumers: Optional[List[ConsumerModel]] = None

class ConsumerModelMap(BaseModel):
    """Maps a consumer to its consumption model
    """
    model_map: dict

class ScenarioModel(BaseModel):
    """Represents a scenario
    """
    consumers: List[ConsumerModel]
