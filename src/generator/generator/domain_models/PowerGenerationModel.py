from pydantic import BaseModel, Json
from datetime import datetime

class PowerGenerationModel(BaseModel):
    Identifier: str
    UnixTimestampSeconds: int
    Generation: int
    Category: str
    CategoryUnit: str
    Interval: int
    IntervalUnit: str
