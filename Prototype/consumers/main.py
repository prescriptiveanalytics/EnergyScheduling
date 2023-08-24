from fastapi import FastAPI
import json
import random
import dill as pickle
from pathlib import Path
from datetime import datetime
from data_models.ConsumerModel import ConsumerModel
from data_models.PowerConsumptionModel import PowerConsumptionModel
from typing import List

config_file = Path("configurations/ex1_three_consumer/config.json")
config = None

# read consumer nodes and initialize models
with open(config_file, "r") as input_file:
    config = json.load(input_file)

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
    return { "Name": "consumer api" }

@app.get("/consumer/all")
def read_all_consumers() -> List[ConsumerModel]:
    return consumers

@app.get("/consumer/{identifier}")
def read_single_consumer(identifier: str) -> ConsumerModel:
    return [x for x in consumers if x.identifier == identifier][0]

@app.get("/consumer/{identifier}/consumption/{unix_timestamp_seconds}")
def read_consumption(identifier: str, unix_timestamp_seconds: int) -> PowerConsumptionModel:
    consumption = int(model_map[identifier].get_consumption(unix_timestamp_seconds)*1000)
    print(consumption)
    return PowerConsumptionModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "usage":consumption, "category": "load", "category_unit": "Wh", "interval": 15, "interval_unit": "minutes"})