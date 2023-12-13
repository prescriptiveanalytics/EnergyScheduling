from typing import List, Optional
from pydantic import BaseModel

class GeneratorModel(BaseModel):
    """Represents a generator data object.
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

class GeneratorCollection(BaseModel):
    """Represents a collection of generators.
    """
    Generators: Optional[List[GeneratorModel]] = None

class GeneratorModelMap(BaseModel):
    """Maps a geneartor to its generation model.
    """
    ModelMap: dict

class ScenarioModel(BaseModel):
    """Represents a scenario
    """
    Generators: List[GeneratorModel]
