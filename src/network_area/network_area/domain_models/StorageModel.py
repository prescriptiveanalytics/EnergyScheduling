from typing import List, Optional
from pydantic import BaseModel


class StorageModelState(BaseModel):
    Identifier: str
    StateOfCharge: Optional[float]


class StorageModelStateCollection(BaseModel):
    Storages: Optional[List[StorageModelState]] = None


class StorageModel(BaseModel):
    Name: str
    Identifier: str
    Level: int
    Latitude: float
    Longitude: float
    Address: str
    Type: str
    Category: str
    MinimumCapacity: float
    MaximumCapacity: float
    CapacityUnit: str
    MinimumActivePower: float
    MaximumActivePower: float
    MinimumReactivePower: float
    MaximumReactivePower: float
    CurrentActivePower: float
    StateOfCharge: float
    InService: bool

class StorageCollection(BaseModel):
    """Represents a collection of generators.
    """
    Storages: Optional[List[StorageModel]] = None
