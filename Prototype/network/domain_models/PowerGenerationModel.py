from pydantic import BaseModel, Json
from typing import Dict
from datetime import datetime

class PowerGenerationModel(BaseModel):
    identifier: str
    datetime: datetime
    generation: int
    category: str
    category_unit: str
    interval: int
    interval_unit: str

class PowerGenerationCollection(BaseModel):
    generations: Dict[str, PowerGenerationModel]
