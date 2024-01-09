from pydantic import BaseModel, Json
from typing import Dict
from datetime import datetime

class PowerGenerationModel(BaseModel):
    Identifier: str
    UnixTimestampSeconds: int
    Generation: float
    Category: str
    CategoryUnit: str
    Interval: int
    IntervalUnit: str
    InService: bool


class PowerGenerationCollection(BaseModel):
    Generations: Dict[str, PowerGenerationModel]
