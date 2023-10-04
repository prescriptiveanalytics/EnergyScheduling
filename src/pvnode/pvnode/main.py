import os
import logging
import json
from pathlib import Path
from typing import List
import base64
# import pvgis_connector
# import configuration_model
import generator_model
import dill as pickle

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

from domain_models.Pv import PvModel, PvCollection
from PvNode import PvNode

# {
#   "topic": "pvnode/1/model",
#   "payload": {
#       "lat": 48.370,
#       "lon": 14.513,
#       "peakpower": 1,
#       "loss": 14,
#       "angle": 0,
#       "aspect": 0,
#       "outputformat": "json",
#       "mountingplace": "building",
#       "startyear": 2005,
#       "endyear": 2020,
#       "usehorizon": 1,
#       "pvcalculation": 1
#   }
# }


# create and configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = Path("config.json")
config = None

with open(config_file, "rt") as input_file:
    config = json.load(input_file)
# end TODO

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

logging.debug("using config=%s", config)
    
pvs: PvCollection = None

# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)

pv_node = PvNode = PvNode(None)

def create_model_map(pvs_arg: List[PvModel], model_path: str):
    
    model_map_local:dict = {}
    # for p in pvs_arg:
    #     with open(Path(model_path) / p.profile_identifier, "rb") as inf:
    #         model_map_local[p.identifier] = pickle.load(inf)
    return model_map_local

@app_dat.application("pvnode/")
async def pv_topic_endpoint_callback(message: SpaMessage, socket: SpaSocket, state: PvNode=pv_node):
    """Basic pv topic subscription"""
    logging.info("pv_topic_endpoint_callback=%s", message)
    await socket.publish(
        SpaMessage(
            payload=f"available",
            topic=f"{message.response_topic}",
        )
    )

@app_dat.application("pvnode/+/model")
async def pv_model_update_callback(message: SpaMessage, socket: SpaSocket, state: PvNode=pv_node):
    logging.info("pv_model_update_callback: received request")
    pv_identifier = message.topic.split("/")[1]
    logging.debug("update pv model for pvnode=%s", pv_identifier)
    logging.info("update model for %s", pv_identifier)
    payload_json = json.loads(message.payload)
    logging.info("payload: %s", payload_json)
    model = generator_model.PVGisGenerator('pv1', payload_json)
    logging.info(type(model))
    
    # convert model to binary
    m = pickle.dumps(model)
    model_binary = json.dumps({ 'file:': base64.b64encode(m).decode('ascii') })
    
    await socket.publish(
        SpaMessage(
            client_name="spa-dat-responder",
            content_type="application/json",
            payload=model_binary,
            topic=message.response_topic
        )
    )   
    
if __name__ == '__main__':
    app_dat.start()