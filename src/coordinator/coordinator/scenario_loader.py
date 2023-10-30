import json
from typing import List
import logging
from pathlib import Path
import uuid
import sys
import base64

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

"""
This script loads a scenario or updates a generator or consumer model.

If you want to load a whole scenario, you have to call the script with three arguments:
    1. the name of the script which is called (scenario_loader.py)
    2. what you want to load/update ("scenario")
    3. the path of the scenario to load (config.json-file)
Example call:    python scenario_loader.py scenario path/of/scenario

If you want to update a model to an existing scenario, you have to call the script with four arguments:
    1. the name of the script which is called (scenario_loader.py)
    2. which node you want to update (generator_model or consumer_model)
    3. the uuid of the node (6d1d3eb9-bf54-4dda-b2f9-c86bf200dfc2) - be sure that it is the id from the current loaded config.json scenario-file
    4. the path of the new model you want to load
Example call:    python scenario_loader.py generator_model 6d1d3eb9-bf54-4dda-b2f9-c86bf200dfc2 C:\Projects\SPA_Energie_UseCase\EnergyScheduling\EnergyScheduling\src\coordinator\coordinator\models\generator\hgb_south_10kwp
"""

# create and configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = Path(__file__).parent / "config.json"
config = None
with open(config_file, "rt", encoding='utf-8') as input_file:
    config = json.load(input_file)

socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_update_scenario = DistributedApplication(socket_provider)
app_update_model = DistributedApplication(socket_provider)

consumer_model_path = Path(__file__).parent / "models/consumer"
generator_model_path = Path(__file__).parent / "models/generator"

# config_file = Path("scenarios/ex0_one_consumer/config.json")
# config_file = Path("scenarios/ex1_three_consumer/config.json")
# config_file = Path("scenarios/ex2_ten_consumer/config.json")

# global variables to load scenario
scenario = None
data_consumer = None
data_generator = None
data_network = None

# global variables to update model
model_type = None   # ["generator" | "consumer"]
model_info = {}

# update consumer data
logging.info("update consumer data")

#r = requests.post(uri_consumer + "/scenario/" + scenario_uuid, json=data_consumer)
#print(r.json())


@app_update_scenario.producer()
async def update_scenario(socket: SpaSocket, state):
    """Pushes a full scenario to the mqtt server"""

    scenario_identifier = str(uuid.uuid4())
    logging.info("push new scenario=%s", scenario_identifier)

    # update consumer data
    logging.info("push consumer node data")
    await socket.publish(
        SpaMessage(
            content_type = "application/json",
            payload = json.dumps({'scenario_identifier': scenario_identifier, 'consumers': data_consumer }),
            topic = "consumer/scenario"
        )
    )
    for cm in data_consumer:
        logging.info("update consumer model for consumer=%s, with model %s", cm['identifier'], cm['profile_identifier'])
        with open(consumer_model_path / cm['profile_identifier'], "rb") as model_input_file:
            model_content = model_input_file.read()
            await socket.publish(
                SpaMessage(
                    content_type = 'application/json',
                    payload = json.dumps({ 'file': base64.b64encode(model_content).decode('ascii') }),
                    topic = f"consumer/{cm['identifier']}/model"
                )
            )
            logging.debug("update model for consumer=%s", cm['profile_identifier'])

    # update generator data
    logging.info("push generator node data")
    await socket.publish(
        SpaMessage(
            content_type = "application/json",
            payload = json.dumps({'scenario_identifier': scenario_identifier, 'generators': data_generator }),
            topic = "generator/scenario"
        )
    )
    for gm in data_generator:
        logging.info("update generator model for generator=%s, with model %s", gm['identifier'], gm['profile_identifier'])
        with open(generator_model_path / gm['profile_identifier'], "rb") as model_input_file:
            model_content = model_input_file.read()
            await socket.publish(
                SpaMessage(
                    content_type = 'application/json',
                    payload = json.dumps({ 'file': base64.b64encode(model_content).decode('ascii') }),
                    topic = f"generator/{gm['identifier']}/model"
                )
            )
            logging.debug("update model for generator=%s", gm['profile_identifier'])

    # update network
    logging.info("push network node data")
    await socket.publish(
        SpaMessage(
            content_type = "application/json",
            payload = json.dumps({'scenario_identifier': scenario_identifier, 'network': data_network }),
            topic = "network/scenario"
        )
    )


@app_update_model.producer()
async def update_model(socket: SpaSocket, state):
    """Loads a new generator or consumer model to the mqtt server"""
    
    with open(model_info['path'], "rb") as model_input_file:
        logging.info("updating...")
        model_content = model_input_file.read()
        await socket.publish(
            SpaMessage(
                content_type = 'application/json',
                payload = json.dumps({ 'file': base64.b64encode(model_content).decode('ascii') }),
                topic = f"{model_type}/{model_info['uuid']}/model"
            )
        )
        
# uncomment for debugging:
# sys.argv = ["scenario_loader.py", "generator_model", "6d1d3eb9-bf54-4dda-b2f9-c86bf200dfc2", "C:\\Projects\\SPA_Energie_UseCase\\EnergyScheduling\\EnergyScheduling\\src\\coordinator\\coordinator\\models\\generator\\Hagenberg_peakpower10_angle22_aspect0"]

if __name__ == '__main__':
    # check length of arguments
    print(len(sys.argv))
    if len(sys.argv) == 3:
        logging.info("update scenario")
        if sys.argv[1] == "scenario":
            scenario_file = sys.argv[2]
            with open(scenario_file, "rt", encoding='utf-8') as input_file:
                scenario = json.load(input_file)
            scenario_uuid = str(uuid.uuid4())            
            data_consumer = scenario['scenario']['consumers']
            data_generator = scenario['scenario']['generators']
            data_network = scenario['scenario']['network']
            app_update_scenario.start()
    elif len(sys.argv) == 4:
        logging.info("update model")
        if sys.argv[1] == "generator_model":
            model_type = "generator"
        elif sys.argv[1] == "consumer_model":
            model_type = "consumer"
        model_info["uuid"] = sys.argv[2]
        model_info["path"] = sys.argv[3]
        app_update_model.start()
    else:
        logging.error("Wrong number of arguments")