from pydantic import BaseModel, Json
from typing import Dict
from datetime import datetime

class PowerPvModel(BaseModel):
    identifier: str
    datetime: datetime
    usage: int
    category: str
    category_unit: str
    interval: int
    interval_unit: str

class PowerPvCollection(BaseModel):
    pvs: Dict[str, PowerPvModel]