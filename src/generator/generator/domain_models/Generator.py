from typing import List, Optional
from pydantic import BaseModel

class GeneratorModel(BaseModel):
    """Represents a generator data object.
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

class GeneratorCollection(BaseModel):
    """Represents a collection of generators.
    """
    generators: Optional[List[GeneratorModel]] = None

class GeneratorModelMap(BaseModel):
    """Maps a geneartor to its generation model.
    """
    model_map: dict

class ScenarioModel(BaseModel):
    """Represents a scenario
    """
    generators: List[GeneratorModel]
