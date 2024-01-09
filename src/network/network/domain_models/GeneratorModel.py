from typing import List, Optional
from pydantic import BaseModel

class GeneratorModel(BaseModel):
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