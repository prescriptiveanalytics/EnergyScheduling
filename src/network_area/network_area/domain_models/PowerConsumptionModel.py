from pydantic import BaseModel, Json
from typing import Dict

class PowerConsumptionModel(BaseModel):
    Identifier: str
    UnixTimestampSeconds: int
    Usage: float
    Category: str
    CategoryUnit: str
    Interval: int
    IntervalUnit: str

class PowerConsumptionCollection(BaseModel):
    Consumptions: Dict[str, PowerConsumptionModel]
