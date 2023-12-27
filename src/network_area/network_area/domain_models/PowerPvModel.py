from pydantic import BaseModel, Json
from typing import Dict
from datetime import datetime

class PowerPvModel(BaseModel):
    Identifier: str
    UnixTimestampSeconds: int
    Usage: int
    Category: str
    CategoryUnit: str
    Interval: int
    IntervalUnit: str

class PowerPvCollection(BaseModel):
    Pvs: Dict[str, PowerPvModel]