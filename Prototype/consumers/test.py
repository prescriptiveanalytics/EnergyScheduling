import json
import requests
from typing import List
import uuid
from pathlib import Path

# from models.ConsumerModel import ConsumerModel

# cm = ConsumerModel(name="location 1", identifier="e6c8200f-d84b-499b-ad13-4313eec39ca2", level=7, latitude=48.1, longitude=14.1, address="none", type="consumer", category="household", network_entity="load", profile_identifier="none")
# print(f"print(cm)={cm}")
# print(f"print(cm.model_dump())={cm.model_dump()}")

# with open("config.json", 'r') as input_file:
#     data = json.load(input_file)
#     print([x for x in data['consumers']])
#     consumers: List[ConsumerModel] = [ConsumerModel(**consumer) for consumer in data['consumers']]
#     print(consumers[0])

# config_file = Path("configurations/ex0_one_consumer/config.json")
config_file = Path("configurations/ex1_three_consumer/config.json")
config = None

model_path = Path("consumption_models")

# read consumer nodes and initialize models
with open(config_file, "r") as input_file:
    config = json.load(input_file)

#print(config)

uri = "http://localhost:7000"

r = requests.get(uri)
print(r.json())

scenario_uuid = str(uuid.uuid4())
data = { 'scenario_data': config }
#print(data)
r = requests.post(uri + "/scenario/" + scenario_uuid, json=config)
print(r.json())

for cm in config['consumers']:
    print(f"update model for {cm['identifier']}")
    files = { 'model_file': open(model_path / cm["profile_identifier"], 'rb') }

    r = requests.post(f'{uri}/consumer/{cm["identifier"]}/model', files=files)
    print(r.json())
