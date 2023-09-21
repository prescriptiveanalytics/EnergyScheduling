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

# create and configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = "config.json"
config = None
with open(config_file, "rt", encoding='utf-8') as input_file:
    config = json.load(input_file)

socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_update_scenario = DistributedApplication(socket_provider)

consumer_model_path = Path("models/consumer")
generator_model_path = Path("models/generator")

# config_file = Path("scenarios/ex0_one_consumer/config.json")
# config_file = Path("scenarios/ex1_three_consumer/config.json")
# config_file = Path("scenarios/ex2_ten_consumer/config.json")

if len(sys.argv) != 2:
    logging.error("wrong number of arguments")
    # sys.exit(1)
    scenario_file = '.\scenarios\ex1_three_consumer\config.json'
else:
    scenario_file = sys.argv[1]
scenario = None

with open(scenario_file, "rt", encoding='utf-8') as input_file:
    scenario = json.load(input_file)

scenario_uuid = str(uuid.uuid4())

data_consumer = scenario['scenario']['consumer']
data_generator = scenario['scenario']['generator']
data_network = scenario['scenario']['network']

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
    for cm in data_consumer['consumers']:
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
    for gm in data_generator['generators']:
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

app_update_scenario.start()