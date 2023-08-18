from fastapi import FastAPI
import json
import random
from datetime import datetime


config_file = "config.json"
config = None

# usage in Wh
usage_min = 100
usage_max = 3000
usage_unit = "Wh"

with open(config_file, "r") as input_file:
    config = json.load(input_file)

app = FastAPI()

@app.get("/")
def read_root():
    return { "Name": "consumer api" }

@app.get("/consumer/all")
def read_all_consumers():
    return json.dumps(config["consumers"], indent=2)

@app.get("/consumer/{identifier}")
def read_single_consumer(identifier: str):
    return json.dumps([x for x in config["consumers"] if x["identifier"] == identifier][0], indent=2)

@app.get("/consumer/{identifier}/consumption/{unix_timestamp_seconds}")
def read_consumption(identifier: str, unix_timestamp_seconds: int):
    obj = { "datetime": unix_timestamp_seconds, "identifier": identifier, "usage": random.randint(usage_min, usage_max), "category": "usage", "usage_unit": usage_unit, "interval": 15, "interval_unit": "minutes", "forecast": {}}
    return json.dumps(obj)