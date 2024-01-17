from typing import List, Optional
from pydantic import BaseModel


class LoadModel(BaseModel):
    Identifier: str
    Load: float


class LoadModelCollection(BaseModel):
    Loads: Optional[List[LoadModel]] = None
