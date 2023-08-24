from fastapi import FastAPI
import json
import dill as pickle
from pathlib import Path
from datetime import datetime
from domain_models.GeneratorModel import GeneratorModel
from domain_models.PowerGenerationModel import PowerGenerationModel
from typing import List

config_file = Path("configurations/ex1_three_consumer/config.json")
config = None

with open(config_file, "r") as input_file:
    config = json.load(input_file)

generators: List[GeneratorModel] = [GeneratorModel(**consumer) for consumer in config['generators']]

def create_model_map(generators, model_path):
    model_map = {}
    for c in generators:
        with open(Path(model_path) / c.profile_identifier, "rb") as inf:
            model_map[c.identifier] =  pickle.load(inf)
    return model_map

model_map = create_model_map(generators, "generator_models")

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
    #power_generation = PowerGenerationModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "generation": int(random.randint(generation_min, generation_max)/4), "category": "generation", "category_unit": category_unit, "interval": 15, "interval_unit": "minutes"})
    current_generation = int(model_map[identifier].get_generation(unix_timestamp_seconds))
    power_generation = PowerGenerationModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "generation": int(current_generation), "category": "generation", "category_unit": "Wh", "interval": 15, "interval_unit": "minutes"})
    return power_generation