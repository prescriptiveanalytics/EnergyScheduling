from typing import List
from pydantic import BaseModel

class ConfigurationEntry(BaseModel):
    lat: float
    lon: float
    peakpower: float
    angle: float
    aspect: float
    loss: float = 14.0
    outputformat: str = 'json'
    mounting: str = 'building'
    startyear: int = 2005
    endyear: int = 2020
    usehorizon: int = 1
    pvcalculation: int = 1

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "lat": 48.368,
                    "lon": 14.513,
                    "peakpower": 3,
                    "angle": 0,
                    "aspect": 0,
                }
            ]
        }
    }

class Configuration(BaseModel):
    configuration: List[ConfigurationEntry]