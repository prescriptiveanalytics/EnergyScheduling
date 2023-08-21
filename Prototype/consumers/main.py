from fastapi import FastAPI
import json
import random
from datetime import datetime
import pydantic
from models.ConsumerModel import ConsumerModel
from models.PowerConsumptionModel import PowerConsumptionModel
from typing import List

config_file = "config.json"
config = None

# usage in Wh
load_min = 100
load_max = 3000
category_unit = "Wh"

with open(config_file, "r") as input_file:
    config = json.load(input_file)

consumers: List[ConsumerModel] = [ConsumerModel(**consumer) for consumer in config['consumers']]

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
def read_consumption(identifier: str, unix_timestamp_seconds: int):
    power_consumption = PowerConsumptionModel(**{"datetime": unix_timestamp_seconds, "identifier": identifier, "usage": random.randint(load_min, load_max), "category": "load", "category_unit": category_unit, "interval": 15, "interval_unit": "minutes"})
    return power_consumption