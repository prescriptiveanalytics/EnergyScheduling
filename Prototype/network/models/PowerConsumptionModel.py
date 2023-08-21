from pydantic import BaseModel, Json
from datetime import datetime

class PowerConsumptionModel(BaseModel):
    identifier: str
    datetime: datetime
    usage: int
    category: str
    category_unit: str
    interval: int
    interval_unit: str
