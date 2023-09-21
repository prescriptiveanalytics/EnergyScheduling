from typing import List, Optional
from pydantic import BaseModel

class GeneratorModel(BaseModel):
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