from typing import List, Optional
from pydantic import BaseModel


class ConsumerModel(BaseModel):
    Name: str
    Identifier: str
    Level: int
    Latitude: float
    Longitude: float
    Address: str
    Type: str
    Category: str
    ProfileIdentifier: str
    InService: bool


class ConsumerCollection(BaseModel):
    """Represents a collection of generators.
    """
    Consumers: Optional[List[ConsumerModel]] = None
