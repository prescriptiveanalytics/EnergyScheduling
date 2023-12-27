from typing import Optional, List
from pydantic import BaseModel


class NetworkBusModel(BaseModel):
    Identifier: str
    Voltage: int
    Category: str
    Type: str


class NetworkEntityModel(BaseModel):
    Identifier: str
    Name: str
    Latitude: float
    Longitude: float
    Address: str
    Type: str
    Category: str


class NetworkLineModel(BaseModel):
    FromBus: str
    ToBus: str
    StdType: str
    LengthKm: float


class NetworkModel(BaseModel):
    Entities: List[NetworkEntityModel]
    Buses: List[NetworkBusModel]
    Lines: List[NetworkLineModel]


class ScenarioNetworkModel(BaseModel):
    Network: NetworkModel
