import requests
import dill as pickle
import json
import uuid
from pathlib import Path

config_file = Path("configurations/ex0_one_consumer/config.json")
#config_file = Path("configurations/ex1_three_consumer/config.json")
config = None

model_path = Path("generator_models")

# read consumer nodes and initialize models
with open(config_file, "r") as input_file:
    config = json.load(input_file)

uri = "http://localhost:7010"

r = requests.get(uri)
print(r.json())

scenario_uuid = str(uuid.uuid4())
data = { 'scenario_data': config }
print(data)

r = requests.post(uri + "/scenario/" + scenario_uuid, json=config)
print(r.json())

for gm in config['generators']:
   print(f"update model for {gm['identifier']}")
   files = { 'model_file': open(model_path / gm["profile_identifier"], 'rb') }

   r = requests.post(f'{uri}/generator/{gm["identifier"]}/model', files=files)
   print(r.json())
