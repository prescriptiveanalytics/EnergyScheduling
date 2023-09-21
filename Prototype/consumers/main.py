from fastapi import FastAPI, File, UploadFile
import json
import dill as pickle
from pathlib import Path
from domain_models.Consumer import ConsumerModel, ScenarioModel
from domain_models.PowerConsumptionModel import PowerConsumptionModel
from typing import List
import logging

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = Path("configurations/ex1_three_consumer/config.json")
#config_file = Path("configurations/ex0_one_consumer/config.json")
config = None

# read consumer nodes and initialize models
with open(config_file, "r") as input_file:
    config = json.load(input_file)

scenario_identifier: str | None = None
consumers = dict()

if config:
    consumers: List[ConsumerModel] = [ConsumerModel(**consumer) for consumer in config['consumers']]

def create_model_map(consumers, model_path):
    model_map = {}
    for c in consumers:
        with open(Path(model_path) / c.profile_identifier, "rb") as inf:
            model_map[c.identifier] =  pickle.load(inf)
    return model_map

model_map = create_model_map(consumers, "consumption_models")

app = FastAPI()

@app.get("/")
def read_root():
    return { "name": "consumer api", "version": "v1", "date": "2023-08-30" }

@app.get("/consumer/all")
def read_all_consumers() -> List[ConsumerModel]:
    global consumers
    global model_map
    global scenario_identifier
    global config
    return consumers

@app.get("/consumer/{identifier}")
def read_single_consumer(identifier: str) -> ConsumerModel:
    global consumers
    global model_map
    global scenario_identifier
    global config
    return [x for x in consumers if x.identifier == identifier][0]

@app.get("/consumer/{identifier}/consumption/{unix_timestamp_seconds}")
def read_consumption(identifier: str, unix_timestamp_seconds: int) -> PowerConsumptionModel:
    global consumers
    global model_map
    global scenario_identifier
    global config
    consumption = int(model_map[identifier].get_consumption(unix_timestamp_seconds)*1000)
    print(consumption)
    return PowerConsumptionModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "usage":consumption, "category": "load", "category_unit": "Wh", "interval": 15, "interval_unit": "minutes"})

@app.post("/consumer/{identifier}/model")
def create_model(identifier: str, model_file: UploadFile = File(...)):
    global consumers
    global model_map
    global scenario_identifier
    global config
    content = model_file.file.read()
    model = pickle.loads(content)
    logging.debug(f"update consumer model {identifier} with model {model_file.filename}")
    model_map[identifier] = model
    return { "Status": "Success" }

@app.post("/scenario/{identifier}")
def create_scenario(identifier: str, scenario_data: ScenarioModel):
    global consumers
    global model_map
    global scenario_identifier
    global config
    logging.debug(f"load new scenario {identifier}")
    logging.debug(f"scenario data: {scenario_data}")
    scenario_identifier = identifier
    consumers = scenario_data.consumers
    model_map = dict()
    for c in scenario_data.consumers:
        model_map[c.identifier] = None
    logging.debug(f"model_map={model_map}")
    return { "Status": "Success" }