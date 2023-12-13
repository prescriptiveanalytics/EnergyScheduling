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

from domain_models.Generator import GeneratorModel, GeneratorCollection, ScenarioModel
from domain_models.PowerGenerationModel import PowerGenerationModel
from GeneratorNode import GeneratorNode

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = Path("config.json")
config = None

with open(config_file, "rt") as input_file:
    config = json.load(input_file)

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])
# config_file = Path("configurations/ex1_three_consumer/config.json")
scenario_file = Path("configurations/ex0_one_consumer/config.json")
scenario = None

with open(scenario_file, "r") as input_file:
    scenario = json.load(input_file)

scenario_identifier = ""

generators: GeneratorCollection = None
if scenario:
    generators: GeneratorCollection = GeneratorCollection(Generators=scenario['Generators'])

socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)

generator_node: GeneratorNode = GeneratorNode(None)

def create_model_map(generators_arg: List[GeneratorModel], model_path: str):
    model_map_local: dict = {}
    for g in generators_arg:
        with open(Path(model_path) / g.ProfileIdentifier, "rb") as inf:
            model_map_local[g.Identifier] =  pickle.load(inf)
    return model_map_local

model_map = create_model_map(generators.Generators, "generator_models")
generator_node.generators = generators
generator_node.generation_models = model_map

@app_dat.application("generator/")
async def generator_topic_endpoint_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """Basic generator topic subscription"""
    logging.info("generator_topic_endpoint_callback=%s", message)
    await socket.publish(
        SpaMessage(
            Payload="available",
            Topic=message.response_topic,
        )
    )

@app_dat.application("generator/all")
async def generator_all_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """Subscribe to """
    logging.info("generator_all_query_callback=%s", message)
    t1 = base64.b64encode(generator_node.generators.model_dump_json().encode("utf-8"))
    await socket.publish(
        SpaMessage(
            ContentType="application/json",
            Payload=t1,
            Topic=message.response_topic,
        )
    )

@app_dat.application("generator/+/information")
async def generator_information_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.info("generator_information_callback=%s", message)
    generator_identifier = message.topic.split("/")[1]
    logging.debug("query generator=%s", generator_identifier)
    logging.info("generator_nodes.generators=%s", generator_node.generators)
    relevant_generator_set = [c for c in generator_node.Generators.Generators if c.Identifier == generator_identifier]
    if len(relevant_generator_set) == 1:
        relevant_generator = relevant_generator_set[0]
        logging.debug(relevant_generator)
        t1 = base64.b64encode(relevant_generator.model_dump_json().encode("uf-8"))
        await socket.publish(
            SpaMessage(
                ContentType="application/json",
                Payload=t1,
                Topic=message.response_topic,
            )
        )
    else:
        logging.info("information for generator not available (generator=%s)", generator_identifier)

# @app_dat.application("generator/+/generation")
# async def generator_consumption_callback(message: SpaMessage, socket: SpaSocket, state: GeneratorNode=generator_node):
#     logger.info("generator_consumption_callback: received request=%s", message.payload)
#     generator_identifier = message.topic.split("/")[1]
#     if generator_identifier in generator_node.generation_models:
#         unix_timestamp_seconds = int(message.payload)
#         generation = int(generator_node.get_generation(generator_identifier, unix_timestamp_seconds)*1000)
#         logging.debug("generation for %s=%s", generator_identifier, generation)
#         power_generation = PowerGenerationModel(**{"datetime": unix_timestamp_seconds, "identifier": generator_identifier, "generation": generation, "category": "load", "category_unit": "Wh", "interval": 15, "interval_unit": "minutes"})
    
#         await socket.publish(
#             SpaMessage(
#                 client_name="spa-dat-responder",
#                 content_type="application/json",
#                 payload=power_generation.model_dump_json(),
#                 topic=message.response_topic,
#             )
#         )
#     else:
#         logging.info("information for generator not available (generator=%s)", generator_identifier)

@app_dat.application("generator/+/generation")
async def generator_consumption_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logger.info("generator_consumption_callback: received request=%s", message.payload)
    generator_identifier = message.topic.split("/")[1]
    if generator_identifier in generator_node.generation_models:
        payload = message.payload.decode("utf-8")
        payload = base64.b64decode(payload)
        payload = json.loads(payload)
        unix_timestamp_seconds = int(payload["UnixTimestampSeconds"])
        generation = int(generator_node.get_generation(generator_identifier, unix_timestamp_seconds)*1000)
        logging.debug("generation for %s=%s", generator_identifier, generation)
        power_generation = PowerGenerationModel(**{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": generator_identifier, "Generation": generation, "Category": "load", "CategoryUnit": "Wh", "Interval": 15, "IntervalUnit": "minutes"})
    
        t1 = base64.b64encode(power_generation.model_dump_json().encode("utf-8"))
        await socket.publish(
            SpaMessage(
                ClientName="spa-dat-responder",
                ContentType="application/json",
                Payload=t1,
                Topic=message.response_topic,
            )
        )
    else:
        logging.info("information for generator not available (generator=%s)", generator_identifier)

# # TODO: Finish this function
# @app_dat.application("generator/+/model")
# async def generator_model_update_callback(message: SpaMessage, socket: SpaSocket, state: GeneratorNode=generator_node):
#     logging.info("generator_model_update_callback: received request")
#     generator_identifier = message.topic.split("/")[1]
#     logging.debug("update generator model for generator=%s", generator_identifier)
#     if generator_identifier in generator_node.generation_models:
#         logging.info("update model for %s", generator_identifier)
#         payload_json = json.loads(message.payload)
#         file_content_bytes = bytes(payload_json['file'], 'ascii')
#         model_file_bytes = base64.b64decode(file_content_bytes)
#         model = pickle.loads(model_file_bytes)
#         generator_node.generation_models[generator_identifier] = model
#     else:
#         logging.info("information for generator not available (generator=%s)", generator_identifier)

# TODO: Finish this function
@app_dat.application("generator/+/model")
async def generator_model_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.info("generator_model_update_callback: received request")
    generator_identifier = message.topic.split("/")[1]
    logging.debug("update generator model for generator=%s", generator_identifier)
    if generator_identifier in generator_node.generation_models:
        logging.info("update model for %s", generator_identifier)
        cnt = message.payload.decode("utf-8")
        usable_payload = base64.b64decode(cnt)
        payload_json = json.loads(usable_payload)
        file_content_bytes = bytes(payload_json['File'], 'ascii')
        model_file_bytes = base64.b64decode(file_content_bytes)
        model = pickle.loads(model_file_bytes)
        generator_node.generation_models[generator_identifier] = model
    else:
        logging.info("information for generator not available (generator=%s)", generator_identifier)


# @app_dat.application("generator/scenario")
# async def generator_scenario_update_callback(message: SpaMessage, socket: SpaSocket, state: GeneratorNode=generator_node):
#     global generator_node
#     payload = json.loads(message.payload)
#     logging.debug("update scenario=%s", payload)
#     scenario_identifier = payload['scenario_identifier']
#     generator_node = GeneratorNode(scenario_identifier=scenario_identifier)
#     generator_node.generators = ScenarioModel(generators=payload['generators'])
#     generator_node.generation_models = { consumer.identifier: None for consumer in generator_node.generators.generators }
#     logging.debug("update scenario generator_node=%s", generator_node)

@app_dat.application("generator/scenario")
async def generator_scenario_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global generator_node
    logging.debug("update scenario=%s", message)   
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    scenario_identifier = payload['ScenarioIdentifier']
    generator_node = GeneratorNode(scenario_identifier=scenario_identifier)
    generator_node.generators = ScenarioModel(Generators=payload['Generators'])
    generator_node.generation_models = { generator.Identifier: None for generator in generator_node.generators.Generators }
    logging.debug("update scenario generator_node=%s", generator_node)

if __name__ == '__main__':
    app_dat.start()
