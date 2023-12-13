from typing import List, Optional
from pydantic import BaseModel

class ConsumerModel(BaseModel):
    """Represents a single consumer data object.
    """
    Name: str
    Identifier: str
    Level: int
    Latitude: float
    Longitude: float
    Address: str
    Type: str
    Category: str
    ProfileIdentifier: str

class ConsumerCollection(BaseModel):
    """Represents a collection of consumers.
    """
    Consumers: Optional[List[ConsumerModel]] = None

class ConsumerModelMap(BaseModel):
    """Maps a consumer to its consumption model
    """
    ModelMap: dict

class ScenarioModel(BaseModel):
    """Represents a scenario
    """
    Consumers: List[ConsumerModel]
