import json
from typing import List
import logging
from pathlib import Path
import requests
import uuid
import sys

consumer_model_path = Path("models/consumer")
generator_model_path = Path("models/generator")

# config_file = Path("scenarios/ex0_one_consumer/config.json")
# config_file = Path("scenarios/ex1_three_consumer/config.json")
# config_file = Path("scenarios/ex2_ten_consumer/config.json")

config_file = sys.argv[1]
config = None

with open(config_file, "r") as input_file:
    config = json.load(input_file)


uri_consumer = "http://localhost:7000"
uri_generator = "http://localhost:7010"
uri_network = "http://localhost:7020"

scenario_uuid = str(uuid.uuid4())

data_consumer = config['scenario']['consumer']#['consumers'] #{ 'scenario_data': config['scenario']['consumer'] }
data_generator = config['scenario']['generator']#['generators'] #{ 'scenario_data': config['scenario']['generator'] }
data_network = config['scenario']['network'] #{ 'scenario_data': config['scenario']['network'] }

# update consumer data
print("update consumer data")
r = requests.post(uri_consumer + "/scenario/" + scenario_uuid, json=data_consumer)
print(r.json())

for cm in data_consumer['consumers']:
    print(cm)
    print(f"update consumer model for {cm['identifier']} with model {cm['profile_identifier']}")
    files = { 'model_file': open(consumer_model_path / cm["profile_identifier"], 'rb') }

    r = requests.post(f'{uri_consumer}/consumer/{cm["identifier"]}/model', files=files)
    print(r.status_code)
    print(r.json())

# update generator data
print("update generator data")
r = requests.post(uri_generator + "/scenario/" + scenario_uuid, json=data_generator)
print(r.json())

for gm in data_generator['generators']:
    print(f"update generator model for {gm['identifier']} with model {gm['profile_identifier']}")
    files = { 'model_file': open(generator_model_path / gm["profile_identifier"], 'rb') }

    r = requests.post(f'{uri_generator}/generator/{gm["identifier"]}/model', files=files)
    print(r.json())

# update network data
print("update network data")
r = requests.post(uri_network + "/scenario/" + scenario_uuid, json=data_network)
print(r.json())