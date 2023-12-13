from pydantic import BaseModel, Json
from datetime import datetime

class PowerConsumptionModel(BaseModel):
    Identifier: str
    UnixTimestampSeconds: int
    Usage: int
    Category: str
    CategoryUnit: str
    Interval: int
    IntervalUnit: str
