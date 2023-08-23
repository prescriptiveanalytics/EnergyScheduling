from pydantic import BaseModel, Json
from datetime import datetime

class PowerGenerationModel(BaseModel):
    identifier: str
    datetime: datetime
    generation: int
    category: str
    category_unit: str
    interval: int
    interval_unit: str
