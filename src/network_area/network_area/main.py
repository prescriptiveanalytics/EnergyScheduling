import os

import humps
import pandapower as pp
import json
import logging
from typing import List
from pathlib import Path
import base64
import dill as pickle

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

from NetworkNode import NetworkNode
from domain_models.NetworkModel import NetworkModel, ScenarioNetworkModel
from domain_models.PowerConsumptionModel import PowerConsumptionModel, PowerConsumptionCollection
from domain_models.ConsumerModel import ConsumerModel, ConsumerCollection
from domain_models.GeneratorModel import GeneratorModel, GeneratorCollection
from domain_models.PowerGenerationModel import PowerGenerationModel, PowerGenerationCollection
from domain_models.OptimalPowerFlow import OptimalPowerFlowSolution

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


def create_model_map(models: List, path: str) -> object:
    model_map_local: dict = {}
    for m in models:
        with open(Path(path) / m.ProfileIdentifier, "rb") as inf:
            model_map_local[m.Identifier] = pickle.load(inf)
    return model_map_local


# key is defined as "type" in generator ("generator") or consumer ("load")
model_path: dict[str, str] = {
    "load": "models/consumer",
    "generator": "models/generator"
}

config_file = Path("config.json")
config = dict()

with open(config_file, "rt") as input_file:
    config = json.load(input_file)

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

logging.debug("config=%s", config)

initialized: bool = False
#consumers: ConsumerCollection = None
#generators: GeneratorCollection = None
#network: NetworkModel = None

network_node: NetworkNode = NetworkNode("")

scenario_file = Path("configurations/ex0_one_consumer/config.json")
scenario = None
with open(scenario_file, "r") as input_file:
    logging.debug("read scenario file")
    scenario = json.load(input_file)
    scenario["Network"] = NetworkModel(**scenario["Network"])
    network_node.networks = ScenarioNetworkModel(Network=scenario["Network"])
    network_node.consumers = ConsumerCollection(Consumers=scenario["Consumers"])
    network_node.generators = GeneratorCollection(Generators=scenario["Generators"])

logging.debug("initial network_node=%s", network_node)

consumer_models = create_model_map(network_node.consumers.Consumers, model_path["load"])
network_node.consumption_models = consumer_models
generator_models = create_model_map(network_node.generators.Generators, model_path["generator"])
network_node.generation_models = generator_models


def initialize_network(network_config, generations: PowerGenerationCollection,
                       loads: PowerConsumptionCollection) -> OptimalPowerFlowSolution:
    # create network
    logging.debug("initialize_network=%s", network_config)
    net = pp.create_empty_network()

    # create buses
    logging.debug("create buses")
    bus_data = network_config.Buses
    buses = {}  # dictionary holding all created buses
    for b in bus_data:
        logging.debug("create bus=%s", b.Identifier)
        bn = pp.create_bus(net, vn_kv=b.Voltage / 1000, name=b.Identifier)
        buses[b.Identifier] = bn

    # create grid connection
    logging.debug("create network entities")
    grid_connections = [x for x in network_config.Buses if x.Type == "grid_connection"]
    if len(grid_connections) != 1:
        logging.error("No or more than one grid connection")
    gc = grid_connections[0]
    gc_entity = [x for x in network_config.Entities if x.Identifier == gc.Identifier][0]
    pp.create_ext_grid(net, bus=buses[gc.Identifier], vm_pu=1.02, name=gc_entity.Name)

    # create load
    logging.debug("create loads")
    for identifier, load in loads.Consumptions.items():
        logging.debug(f"consumer load for {identifier}: {load}")
        pp.create_load(net, bus=buses[identifier], p_mw=load.Usage / 1000, q_mvar=0.05, name=identifier)

    logging.debug("create generations")
    for identifier, generation in generations.Generations.items():
        logging.debug(f"generation power for {identifier}: {generation}")
        pp.create_sgen(net, bus=buses[identifier], p_mw=generation.Generation / 1000, name=identifier)

    logging.debug("create lines")
    x = 1
    for line in network_config.Lines:
        logging.debug(f"create line from {line.FromBus} to {line.ToBus}")
        frombus = buses[line.FromBus]
        tobus = buses[line.ToBus]
        name = f"{line.FromBus}-{line.ToBus}"
        #pp.create_line(net, from_bus=frombus, to_bus=tobus, length_km=line.length_km, std_type=line.std_type)
        if line.StdType:
            resolved_line = pp.std_types.basic_line_std_types()[line.StdType]
            pp.create_line_from_parameters(net, from_bus=frombus, to_bus=tobus, length_km=line.LengthKm, **resolved_line)
        x += 1

    logging.debug("run opf")
    pp.runpp(net)
    logging.debug(f"keys in net={net.keys()}")
    logging.debug(f"calculated net={net}")

    pandapower_result = {'Bus': json.loads(net.bus.to_json()), 'Load': json.loads(net.load.to_json()),
              'Line': json.loads(net.line.to_json()), 'Sgen': json.loads(net.sgen.to_json()),
              'ResBus': json.loads(net.res_bus.to_json()), 'ResLine': json.loads(net.res_line.to_json()),
              'ResLoad': json.loads(net.res_load.to_json()), 'ResExtGrid': json.loads(net.res_ext_grid.to_json()),
              'ResSgen': json.loads(net.res_sgen.to_json())}
    logging.debug("result=%s", pandapower_result)
    # transform the datastructure to pascal-case
    pandapower_result = humps.pascalize(pandapower_result)
    return OptimalPowerFlowSolution(**pandapower_result)


def fetch_loads(consumers: ConsumerCollection, unix_timestamp_seconds: int):
    consumer_loads = {}
    for c in consumers.Consumers:
        logging.debug("request consumption for %s", c)
        consumption = network_node.consumption_models[c.Identifier].get_consumption(unix_timestamp_seconds)
        consumer_loads[c.Identifier] = PowerConsumptionModel(
            **{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": c.Identifier, "Usage": consumption,
               "Category": "load", "CategoryUnit": "Wh", "Interval": 15, "IntervalUnit": "minutes"})
    logging.debug("consumer_loads=%s", consumer_loads)
    return PowerConsumptionCollection(Consumptions=consumer_loads)


def fetch_generations(generators: GeneratorCollection, unix_timestamp_seconds: int):
    generator_generations = {}
    for g in generators.Generators:
        logging.debug("request generations for %s", g)
        generation = network_node.generation_models[g.Identifier].get_generation(unix_timestamp_seconds)
        generator_generations[g.Identifier] = PowerGenerationModel(
            **{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": g.Identifier, "Generation": generation,
               "Category": "generation", "CategoryUnit": "Wh", "Interval": 15, "IntervalUnit": "minutes"})
    logging.debug("generation_generations=%s", generator_generations)
    return PowerGenerationCollection(Generations=generator_generations)


def calculate_opf(unix_timestamp_seconds: int):
    loads: PowerConsumptionCollection = fetch_loads(network_node.consumers, unix_timestamp_seconds)
    generations: PowerGenerationCollection = fetch_generations(network_node.generators,
                                                               unix_timestamp_seconds)
    opf = initialize_network(network_node.networks.Network, generations, loads)
    return opf


# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)


@app_dat.application("network")
async def network_topic_endpoint_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """Basic network topic subscription"""
    logging.debug("network_topic_endpoint_callback=%s", message)
    await socket.publish(
        SpaMessage(
            Payload="available",
            Topic=message.response_topic
        )
    )


@app_dat.application("network/all")
async def network_all_endpoint_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """Query network information"""
    global network_node
    logging.debug("network_all_endpoint_callback")
    if not network_node.initialized:
        logging.info("initialize network")
        # TODO: gather all information an initialize network
        # await query_network_participants_dat(network_node, socket)
        if network_node.initialized:
            logging.debug("network successfully initialized")

    if network_node.initialized:
        logging.debug("return network")
        await socket.publish(
            SpaMessage(
                ContentType="application/json",
                Payload=network_node.networks.model_dump_json(),
                Topic=message.response_topic
            )
        )


@app_dat.application("network/opf")
async def network_opf_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global network_node
    logging.debug("network_opf_query_callback=%s", message)

    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)

    unix_timestamp_seconds = int(payload['UnixTimestampSeconds'])

    result = calculate_opf(unix_timestamp_seconds)

    logging.debug("opf=%s", result)
    t1 = base64.b64encode(result.model_dump_json().encode("utf-8"))

    await socket.publish(
        SpaMessage(
            ContentType="application/json",
            Payload=t1,
            Topic=message.response_topic
        )
    )


@app_dat.application("network/scenario")
async def network_scenario_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    """retrieve a new scenario
    """
    global network_node
    logging.debug("update scenario=%s", message)
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    scenario_identifier = payload['ScenarioIdentifier']
    new_network_node = NetworkNode(scenario_identifier=scenario_identifier)
    snm = NetworkModel(**payload['Network'])
    new_network_node.networks = ScenarioNetworkModel(Network=snm)
    logging.debug("update scenario network_node=%s", network_node)
    network_node.networks = new_network_node.networks


@app_dat.application("consumer/+/add")
async def consumer_add_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.debug("consumer_add_callback: received request")
    consumer_identifier = message.topic.split("/")[1]
    logging.info("consumer_add_callback identified consumer=%s", consumer_identifier)
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    update = False
    for c in network_node.consumers.Consumers:
        if c.Identifier == consumer_identifier:
            logging.info("update consumer=%s", consumer_identifier)
            update = True
    if not update:
        logging.info("add consumer=%s", consumer_identifier)
    network_node.consumers.Consumers = [c for c in network_node.consumers.Consumers if c.Identifier != consumer_identifier]
    network_node.consumers.Consumers.append(ConsumerModel(**payload))


@app_dat.application("consumer/+/model")
async def consumer_model_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.info("consumer_model_update_callback: received request")
    consumer_identifier = message.topic.split("/")[1]
    logging.debug("update consumer model for consumer=%s", consumer_identifier)
    if consumer_identifier in network_node.consumption_models:
        logging.info("update model for %s", consumer_identifier)
        cnt = message.payload.decode("utf-8")
        usable_payload = base64.b64decode(cnt)
        payload_json = json.loads(usable_payload)
        file_content_bytes = bytes(payload_json['File'], 'ascii')
        model_file_bytes = base64.b64decode(file_content_bytes)
        model = pickle.loads(model_file_bytes)
        network_node.consumption_models[consumer_identifier] = model
    else:
        logging.info("information for consumer not available (consumer=%s)", consumer_identifier)


@app_dat.application("generator/+/add")
async def generator_add_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.debug("generator_add_callback: received request")
    generator_identifier = message.topic.split("/")[1]
    logging.info("add generator=%s", generator_identifier)
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    update = False
    for c in network_node.generators.Generators:
        if c.Identifier == generator_identifier:
            logging.info("update generator=%s", generator_identifier)
            update = True
    if not update:
        logging.info("add generator=%s", generator_identifier)
    network_node.generators.Generators = [c for c in network_node.generators.Generators if c.Identifier != generator_identifier]
    network_node.generators.Generators.append(GeneratorModel(**payload))


@app_dat.application("generator/+/model")
async def generator_model_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.info("generator_model_update_callback: received request")
    generator_identifier = message.topic.split("/")[1]
    logging.debug("update generator model for generator=%s", generator_identifier)
    if generator_identifier in network_node.generation_models:
        logging.info("update model for %s", generator_identifier)
        cnt = message.payload.decode("utf-8")
        usable_payload = base64.b64decode(cnt)
        payload_json = json.loads(usable_payload)
        file_content_bytes = bytes(payload_json['File'], 'ascii')
        model_file_bytes = base64.b64decode(file_content_bytes)
        model = pickle.loads(model_file_bytes)
        network_node.generation_models[generator_identifier] = model
    else:
        logging.info("information for generator not available (generator=%s)", generator_identifier)


if __name__ == '__main__':
    app_dat.start()

