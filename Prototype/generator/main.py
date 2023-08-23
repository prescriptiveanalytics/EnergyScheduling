from fastapi import FastAPI
import json
import random
from datetime import datetime
import pydantic
from models.GeneratorModel import GeneratorModel
from models.PowerGenerationModel import PowerGenerationModel
from typing import List

config_file = "config.json"
config = None

# usage in Wh
generation_min = 10000
generation_max = 30000
category_unit = "Wh"

with open(config_file, "r") as input_file:
    config = json.load(input_file)

generators: List[GeneratorModel] = [GeneratorModel(**consumer) for consumer in config['generators']]

app = FastAPI()

@app.get("/")
def read_root():
    return { "Name": "generator api" }

@app.get("/generator/all")
def read_all_generators() -> List[GeneratorModel]:
    return generators

@app.get("/generator/{identifier}")
def read_single_generator(identifier: str) -> GeneratorModel:
    return [x for x in generators if x.identifier == identifier][0]

@app.get("/generator/{identifier}/generation/{unix_timestamp_seconds}")
def read_consumption(identifier: str, unix_timestamp_seconds: int):
    power_generation = PowerGenerationModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "generation": random.randint(generation_min, generation_max), "category": "generation", "category_unit": category_unit, "interval": 15, "interval_unit": "minutes"})
    return power_generation