import json
from typing import List
import logging
import pydantic
from domain_models.NetworkModel import NetworkModel
from pathlib import Path
import requests
import uuid

# with open("config.json", 'r') as input_file:
#     data = json.load(input_file)
#     print([x for x in data['network']])
#     network: NetworkModel = NetworkModel(**data['network'])
#     print(network)

config_file = Path("configurations/ex0_one_consumer/config.json")
#config_file = Path("configurations/ex1_three_consumer/config.json")
config = None

with open(config_file, "r") as input_file:
    config = json.load(input_file)

uri = "http://localhost:7020"

r = requests.get(uri)
print(r.json())

scenario_uuid = str(uuid.uuid4())

data = config['network'] #{ 'scenario_data': config }
print(data)
print()

r = requests.post(uri + "/scenario/" + scenario_uuid, json=config)
print(r.json())

# for gm in config['generators']:
#     print(f"update model for {gm['identifier']}")
#     files = { 'model_file': open(model_path / gm["profile_identifier"], 'rb') }

#     r = requests.post(f'{uri}/generator/{gm["identifier"]}/model', files=files)
#     print(r.json())

