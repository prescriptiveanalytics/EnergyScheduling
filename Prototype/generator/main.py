from fastapi import FastAPI, File, UploadFile
import json
import dill as pickle
from pathlib import Path
from datetime import datetime
from domain_models.Generator import GeneratorModel, ScenarioModel
from domain_models.PowerGenerationModel import PowerGenerationModel
from typing import List
import logging

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

# config_file = Path("configurations/ex1_three_consumer/config.json")
config_file = Path("configurations/ex0_one_consumer/config.json")
config = None

with open(config_file, "r") as input_file:
    config = json.load(input_file)

scenario_identifier = ""
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
    global generators
    global config
    global model_map
    global scenario_identifier
    return generators

@app.get("/generator/{identifier}")
def read_single_generator(identifier: str) -> GeneratorModel:
    global generators
    global config
    global model_map
    global scenario_identifier
    return [x for x in generators if x.identifier == identifier][0]

@app.get("/generator/{identifier}/generation/{unix_timestamp_seconds}")
def read_consumption(identifier: str, unix_timestamp_seconds: int):
    global generators
    global config
    global model_map
    global scenario_identifier
    current_generation = int(model_map[identifier].get_generation(unix_timestamp_seconds))
    power_generation = PowerGenerationModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "generation": int(current_generation), "category": "generation", "category_unit": "Wh", "interval": 15, "interval_unit": "minutes"})
    return power_generation

@app.post("/generator/{identifier}/model")
def create_model(identifier: str, model_file: UploadFile = File(...)):
    global generators
    global config
    global model_map
    global scenario_identifier
    content = model_file.file.read()
    model = pickle.loads(content)
    logging.debug(f"update generator model for {identifier} with model {len(content)}")
    model_map[identifier] = model
    return { "Status": "Success" }

@app.post("/scenario/{identifier}")
def create_scenario(identifier: str, scenario_data: ScenarioModel):
    global generators
    global config
    global model_map
    global scenario_identifier
    logging.debug(f"load new scenario {identifier}")
    logging.debug(f"scenario data: {scenario_data}")
    scenario_identifier = identifier
    generators = scenario_data.generators
    model_map = dict()
    for c in scenario_data.generators:
        model_map[c.identifier] = None
    logging.debug(f"model_map={model_map}")
    return { "Status": "Success" }