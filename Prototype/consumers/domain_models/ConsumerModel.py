from pydantic import BaseModel
from typing import List

class ConsumerModel(BaseModel):
    name: str
    identifier: str
    level: int
    latitude: float
    longitude: float
    address: str
    type: str
    category: str
    profile_identifier: str

class ScenarioModel(BaseModel):
    consumers: List[ConsumerModel]