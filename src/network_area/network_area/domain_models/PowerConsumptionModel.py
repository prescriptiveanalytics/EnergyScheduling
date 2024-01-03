from pydantic import BaseModel
from typing import Dict


class PowerConsumptionModel(BaseModel):
    Identifier: str
    UnixTimestampSeconds: int
    Usage: float
    Category: str
    CategoryUnit: str
    Interval: int
    IntervalUnit: str
    InService: bool


class PowerConsumptionCollection(BaseModel):
    Consumptions: Dict[str, PowerConsumptionModel]
