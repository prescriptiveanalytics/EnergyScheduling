import os
import json
import logging
from pathlib import Path
from typing import List
import base64
import dill as pickle

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

from domain_models.Consumer import (ConsumerCollection, ConsumerModel,
                                    ScenarioModel)
from domain_models.PowerConsumptionModel import PowerConsumptionModel
from ConsumerNode import ConsumerNode

""" 
This script is designed to manage consumer models and their associated power consumption data using the spa-dat package
and MQTT communication. It is used to control and to interact with simulated consumers in a power grid system.
"""

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

#scenario_file = Path("configurations/ex1_three_consumer/config.json")
scenario_file = Path("configurations/ex0_one_consumer/config.json")
scenario = None

# read consumer nodes and initialize models
with open(scenario_file, "r") as input_file:
    scenario = json.load(input_file)

consumers: ConsumerCollection = None
if scenario:
    consumers = ConsumerCollection(Consumers=scenario['Consumers'])

# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)

consumer_node: ConsumerNode = ConsumerNode(None)

def create_model_map(consumers_arg: List[ConsumerModel], model_path: str):
    model_map_local:dict  = {}
    for c in consumers_arg:
        with open(Path(model_path) / c.ProfileIdentifier, "rb") as inf:
            model_map_local[c.Identifier] =  pickle.load(inf)
    return model_map_local

model_map = create_model_map(consumers.Consumers, "consumption_models")
consumer_node.consumers = consumers
consumer_node.consumption_models = model_map

# subscribe to general topic, to be able to answer requests
# here, the slash is needed, else it does not work
@app_dat.application("consumer/")
async def consumer_topic_endpoint_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """Basic consumer topic subscription"""
    logging.info("consumer_topic_endpoint_callback=%s", message)
    await socket.publish(
        SpaMessage(
            Payload=f"available",
            Topic=f"{message.response_topic}",
        )
    )

@app_dat.application("consumer/all")
async def consumer_all_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """Subscribe to """
    logging.info("consumer_all_query_callback=%s", message)
    t1 = base64.b64encode(consumer_node.consumers.model_dump_json().encode("utf-8"))
    await socket.publish(
        SpaMessage(
            ContentType="application/json",
            Payload=t1,
            Topic=message.response_topic,
        )
    )

@app_dat.application("consumer/+/information")
async def consumer_information_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.info("consumer_information_callback=%s", message)
    logging.info("consumer_information_callback: state=%s", state)
    consumer_identifier = message.topic.split("/")[1]
    logging.debug("query consumer=%s", consumer_identifier)
    logging.info("consumer_nodes.consumers=%s", consumer_node.consumers)
    relevant_consumer_set = [c for c in consumer_node.consumers.consumers if c.identifier == consumer_identifier]
    if len(relevant_consumer_set) == 1:
        relevant_consumer = relevant_consumer_set[0]
        logging.debug(relevant_consumer)
        t1 = base64.b64encode(relevant_consumer.model_dump_json().encode("utf-8"))
        await socket.publish(
            SpaMessage(
                ContentType="application/json",
                Payload=t1,
                Topic=message.response_topic,
            )
        )
    else:
        logging.info("information for consumer not available (consumer=%s)", relevant_consumer)

# @app_dat.application("consumer/+/consumption")
# async def consumer_consumption_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
#     logger.info("consumer_consumption_callback: received request=%s", message.payload)
#     consumer_identifier = message.topic.split("/")[1]
#     if consumer_identifier in consumer_node.consumption_models:
#         unix_timestamp_seconds = int(message.payload)
#         consumption = int(consumer_node.get_consumption(consumer_identifier, unix_timestamp_seconds)*1000)
#         logging.debug("consumption for %s=%s", consumer_identifier, consumption)
#         power_consumption = PowerConsumptionModel(**{"datetime": unix_timestamp_seconds, "identifier": consumer_identifier, "usage":consumption, "category": "load", "category_unit": "Wh", "interval": 15, "interval_unit": "minutes"})
    
#         await socket.publish(
#             SpaMessage(
#                 client_name="spa-dat-responder",
#                 content_type="application/json",
#                 payload=power_consumption.model_dump_json(),
#                 topic=message.response_topic,
#             )
#         )
#     else:
#         logging.info("information for consumer not available (consumer=%s)", consumer_identifier)

@app_dat.application("consumer/+/consumption")
async def consumer_consumption_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logger.info("consumer_consumption_callback: received request=%s", message.payload)
    consumer_identifier = message.topic.split("/")[1]
    if consumer_identifier in consumer_node.consumption_models:
        payload = message.payload.decode("utf-8")
        payload = base64.b64decode(payload)
        payload = json.loads(payload)
        unix_timestamp_seconds = int(payload["UnixTimestampSeconds"])
        consumption = int(consumer_node.get_consumption(consumer_identifier, unix_timestamp_seconds)*1000)
        logging.debug("consumption for %s=%s", consumer_identifier, consumption)
        power_consumption = PowerConsumptionModel(**{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": consumer_identifier, "Usage":consumption, "Category": "load", "CategoryUnit": "Wh", "Interval": 15, "IntervalUnit": "minutes"})

        # encode payload correctly
        t1 = base64.b64encode(power_consumption.model_dump_json().encode("utf-8"))
        await socket.publish(
            SpaMessage(
                ClientName="spa-dat-responder",
                ContentType="application/json",
                Payload=t1,
                Topic=message.response_topic,
            )
        )
    else:
        logging.info("information for consumer not available (consumer=%s)", consumer_identifier)

# @app_dat.application("consumer/+/model")
# async def consumer_model_update_callback(message: SpaMessage, socket: SpaSocket, state: ConsumerNode=consumer_node):
#     global consumer_node
#     logging.info("consumer_model_update_callback: received request") #=%s", message.payload)
#     consumer_identifier = message.topic.split("/")[1]
#     logging.debug("update consumer model for consumer=%s", consumer_identifier)
#     if consumer_identifier in consumer_node.consumption_models:
#         logging.info("update model for %s", consumer_identifier)
#         payload_json = json.loads(message.payload)
#         file_content_bytes = bytes(payload_json['file'], 'ascii')
#         model_file_bytes = base64.b64decode(file_content_bytes)
#         model = pickle.loads(model_file_bytes)
#         consumer_node.consumption_models[consumer_identifier] = model
#     else:
#         logging.info("information for consumer not available (consumer=%s)", consumer_identifier)

@app_dat.application("consumer/+/model")
async def consumer_model_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.info("consumer_model_update_callback: received request") #=%s", message.payload)
    consumer_identifier = message.topic.split("/")[1]
    logging.debug("update consumer model for consumer=%s", consumer_identifier)
    if consumer_identifier in consumer_node.consumption_models:
        logging.info("update model for %s", consumer_identifier)
        cnt = message.payload.decode("utf-8")
        usable_payload = base64.b64decode(cnt)
        payload_json = json.loads(usable_payload)
        file_content_bytes = bytes(payload_json['File'], 'ascii')
        model_file_bytes = base64.b64decode(file_content_bytes)
        model = pickle.loads(model_file_bytes)
        consumer_node.consumption_models[consumer_identifier] = model
    else:
        logging.info("information for consumer not available (consumer=%s)", consumer_identifier)

# @app_dat.application("consumer/scenario")
# async def consumer_scenario_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
#     global consumer_node
#     logging.debug(f"received: {message}")
#     cnt = message.payload.decode("utf-8")
#     usable_payload = base64.b64decode(cnt)
#     payload = json.loads(usable_payload)
#     logging.debug("update scenario=%s", payload)
#     scenario_identifier = payload['scenario_identifier']
#     consumer_node = ConsumerNode(scenario_identifier=scenario_identifier)
#     consumer_node.consumers = ScenarioModel(consumers=payload['consumers'])
#     consumer_node.consumption_models = { consumer.identifier: None for consumer in consumer_node.consumers.consumers }
#     logging.debug("update scenario consumer_node=%s", consumer_node)

@app_dat.application("consumer/scenario")
async def consumer_scenario_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global consumer_node
    logging.debug(f"update scenario: {message}")
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    # payload = humps.decamelize(payload)
    logging.debug("update scenario=%s", payload)
    scenario_identifier = payload['ScenarioIdentifier']
    consumer_node = ConsumerNode(scenario_identifier=scenario_identifier)
    consumer_node.consumers = ScenarioModel(Consumers=payload['Consumers'])
    consumer_node.consumption_models = { consumer.Identifier: None for consumer in consumer_node.consumers.Consumers }
    logging.debug("update scenario consumer_node=%s", consumer_node)

if __name__ == '__main__':
    app_dat.start()
