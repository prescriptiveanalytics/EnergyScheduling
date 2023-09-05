from typing import Optional, List
from pydantic import BaseModel

class NetworkBusModel(BaseModel):
    identifier: str
    voltage: int
    category: str
    type: str

class NetworkEntityModel(BaseModel):
    identifier: str
    name: str
    latitude: float
    longitude: float
    address: str
    type: str
    category: str

class NetworkLineModel(BaseModel):
    from_bus: str
    to_bus: str
    std_type: str
    length_km: float

class NetworkModel(BaseModel):
    entities: List[NetworkEntityModel]
    bus: List[NetworkBusModel]
    lines: List[NetworkLineModel]

class ScenarioNetworkModel(BaseModel):
    network: NetworkModel