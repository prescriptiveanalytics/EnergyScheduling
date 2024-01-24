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
from domain_models.StorageModel import StorageCollection, StorageModelStateCollection, StorageModel
from domain_models.OptimalPowerFlow import OptimalPowerFlowSolution
import storage_simple_strategy
from domain_models.LoadModel import LoadModelCollection

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)
logging.info("current working directory=%s", os.getcwd())

def create_model_map(models: List, path: str) -> object:
    model_map_local: dict = {}
    for m in models:
        with open(Path(path) / m.ProfileIdentifier, "rb") as inf:
            model_map_local[m.Identifier] = pickle.load(inf)
    return model_map_local


# key is defined as "type" in generator ("generator") or consumer ("load")
model_path: dict[str, str] = {
    "load": "./models/consumer",
    "generator": "./models/generator"
}

config_file = Path("config.json")

with open(config_file, "rt") as input_file:
    config = json.load(input_file)

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

logging.debug("config=%s", config)

initialized: bool = False

network_node: NetworkNode = NetworkNode("")

scenario_file = Path("configurations/ex0_one_consumer/config.json")

with open(scenario_file, "r") as input_file:
    logging.debug("read scenario file")
    scenario = json.load(input_file)["Scenario"]
    scenario["Network"] = NetworkModel(**scenario["Network"])
    network_node.networks = ScenarioNetworkModel(Network=scenario["Network"])
    network_node.consumers = ConsumerCollection(Consumers=scenario["Consumers"])
    network_node.generators = GeneratorCollection(Generators=scenario["Generators"])
    network_node.storages = StorageCollection(Storages=scenario["Storages"])

logging.debug("initial network_node=%s", network_node)

consumer_models = create_model_map(network_node.consumers.Consumers, model_path["load"])
network_node.consumption_models = consumer_models
generator_models = create_model_map(network_node.generators.Generators, model_path["generator"])
network_node.generation_models = generator_models


class UnitConversionException(Exception):
    pass


def convert_magnitude(usage: float, category_unit_input: str, category_unit_output: str):
    conversions = {
        "TWh": 1000000000.0,
        "MWh": 1000000.0,
        "kWh": 1000.0,
        "Wh": 1.0,
        "mWh": 0.001,
        "uWh": 0.000001,
    }

    if category_unit_input not in conversions.keys() or category_unit_output not in conversions.keys():
        raise UnitConversionException()
    converted_value = usage * conversions[category_unit_input] / conversions[category_unit_output]
    return usage * conversions[category_unit_input] / conversions[category_unit_output]


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
        bn = pp.create_bus(net, vn_kv=b.Voltage, name=b.Identifier)
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
        pp.create_load(net, bus=buses[identifier],
                       p_mw=convert_magnitude(load.Usage, load.CategoryUnit, "MWh"),
                       q_mvar=0.0, name=identifier)

    logging.debug("create generations")
    for identifier, generation in generations.Generations.items():
        logging.debug(f"generation power for {identifier}: {generation}")
        pp.create_sgen(net, bus=buses[identifier],
                       p_mw=convert_magnitude(generation.Generation, generation.CategoryUnit, "MWh"),
                       name=identifier, in_service=generation.InService)

    logging.debug("create storages")
    for storage in network_node.storages.Storages:
        logging.debug(f"battery storage for {storage.Identifier}")
        inService = storage.InService
        if storage.MaximumCapacity == 0 or storage.MaximumCapacity < storage.MinimumCapacity:
            inService = False
        store_el = pp.create_storage(net, bus=buses[storage.Identifier], p_mw=0.0, q_mvar=0.0,
                                     max_e_mwh=storage.MaximumCapacity, min_e_mwh=storage.MinimumCapacity,
                                     name=storage.Identifier, soc_percent=storage.StateOfCharge, sn_mva=0.0, in_service=inService)

        storage_simple_strategy.Storage(net=net, gid=store_el, soc_percentage=storage.StateOfCharge)

    logging.debug("create lines")
    x = 1
    for line in network_config.Lines:
        logging.debug(f"create line from {line.FromBus} to {line.ToBus}")
        frombus = buses[line.FromBus]
        tobus = buses[line.ToBus]
        name = f"{line.FromBus}-{line.ToBus}"
        if line.StdType:
            resolved_line = pp.std_types.basic_line_std_types()[line.StdType]
            pp.create_line_from_parameters(net, from_bus=frombus, to_bus=tobus,
                                           length_km=line.LengthKm, name=name, **resolved_line)
        x += 1

    logging.debug("run opf")
    pp.runpp(net, run_control=True)
    logging.debug(f"keys in net={net.keys()}")
    logging.debug(f"calculated net={net}")

    pandapower_result = {'Bus': json.loads(net.bus.to_json()), 'Load': json.loads(net.load.to_json()),
                         'Line': json.loads(net.line.to_json()), 'Sgen': json.loads(net.sgen.to_json()),
                         'ResBus': json.loads(net.res_bus.to_json()), 'ResLine': json.loads(net.res_line.to_json()),
                         'ResLoad': json.loads(net.res_load.to_json()),
                         'ResExtGrid': json.loads(net.res_ext_grid.to_json()),
                         'ResSgen': json.loads(net.res_sgen.to_json()),
                         'Storage': json.loads(net.storage.to_json()),
                         'ResStorage': json.loads(net.res_storage.to_json())}
    logging.debug("result=%s", pandapower_result)
    # transform the datastructure to pascal-case
    pandapower_result = humps.pascalize(pandapower_result)
    logging.debug("result=%s", pandapower_result)
    return OptimalPowerFlowSolution(**pandapower_result)


def fetch_loads(consumers: ConsumerCollection, unix_timestamp_seconds: int):
    consumer_loads = {}
    for c in consumers.Consumers:
        logging.debug("request consumption for %s", c)
        consumption = network_node.consumption_models[c.Identifier].get_consumption(unix_timestamp_seconds)
        consumer_loads[c.Identifier] = PowerConsumptionModel(
            **{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": c.Identifier, "Usage": consumption,
               "Category": "load", "CategoryUnit": "kWh", "Interval": 15, "IntervalUnit": "minutes", "InService": c.InService })
    logging.debug("consumer_loads=%s", consumer_loads)
    return PowerConsumptionCollection(Consumptions=consumer_loads)


def prepare_loads(consumers: ConsumerCollection, unix_timestamp_seconds: int, loads: LoadModelCollection) -> PowerConsumptionCollection:
    consumer_loads = {}
    temp_loads = { l.Identifier: l.Load for l in loads.Loads }
    for c in consumers.Consumers:
        logging.debug("prepare consumption for %s", c)
        consumption = temp_loads[c.Identifier]
        consumer_loads[c.Identifier] = PowerConsumptionModel(
            **{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": c.Identifier, "Usage": consumption,
               "Category": "load", "CategoryUnit": "kWh", "Interval": 15, "IntervalUnit": "minutes",
               "InService": c.InService})
        logging.debug("consumer_loads=%s", consumer_loads)
    return PowerConsumptionCollection(Consumptions=consumer_loads)


def fetch_generations(generators: GeneratorCollection, unix_timestamp_seconds: int):
    generator_generations = {}
    for g in generators.Generators:
        logging.debug("request generations for %s", g)
        generation = network_node.generation_models[g.Identifier].get_generation(unix_timestamp_seconds)
        generator_generations[g.Identifier] = PowerGenerationModel(
            **{"UnixTimestampSeconds": unix_timestamp_seconds, "Identifier": g.Identifier, "Generation": generation,
               "Category": "generation", "CategoryUnit": "Wh", "Interval": 15, "IntervalUnit": "minutes", "InService": g.InService })
    logging.debug("generation_generations=%s", generator_generations)
    return PowerGenerationCollection(Generations=generator_generations)


def calculate_opf(unix_timestamp_seconds: int, loads: PowerConsumptionCollection, generations: PowerGenerationCollection):
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
    loads: PowerConsumptionCollection = fetch_loads(network_node.consumers, unix_timestamp_seconds)
    generations: PowerGenerationCollection = fetch_generations(network_node.generators,
                                                               unix_timestamp_seconds)
    result = calculate_opf(unix_timestamp_seconds, loads, generations)

    logging.debug("opf=%s", result)
    t1 = base64.b64encode(result.model_dump_json().encode("utf-8"))

    await socket.publish(
        SpaMessage(
            ContentType="application/json",
            Payload=t1,
            Topic=message.response_topic
        )
    )


def get_storage(identifier: str) -> StorageModel:
    for sm in network_node.storages.Storages:
        if sm.Identifier == identifier:
            return sm


def process_storage_states(storage_states: StorageModelStateCollection) -> None:
    for state in storage_states.Storages:
        # find storage in storages
        storage = get_storage(state.Identifier)
        storage.StateOfCharge = state.StateOfCharge


@app_dat.application("network/opf_with_state")
async def network_opf_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global network_node
    logging.debug("network_opf__with_state_query_callback=%s", message)

    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)

    unix_timestamp_seconds = int(payload['UnixTimestampSeconds'])
    storage_states = StorageModelStateCollection(**payload['StorageModelStates'])

    if storage_states:
        process_storage_states(storage_states)

    loads: PowerConsumptionCollection = fetch_loads(network_node.consumers, unix_timestamp_seconds)
    generations: PowerGenerationCollection = fetch_generations(network_node.generators,
                                                               unix_timestamp_seconds)
    result = calculate_opf(unix_timestamp_seconds, loads, generations)

    logging.debug("opf=%s", result)
    t1 = base64.b64encode(result.model_dump_json().encode("utf-8"))

    await socket.publish(
        SpaMessage(
            ContentType="application/json",
            Payload=t1,
            Topic=message.response_topic
        )
    )


@app_dat.application("network/opf_data")
async def network_opf_query_data_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global network_node
    logging.debug("network_opf_data_query_callback=%s", message)

    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)

    unix_timestamp_seconds = int(payload['UnixTimestampSeconds'])
    storage_states = StorageModelStateCollection(**payload['StorageModelStates'])
    load_data = LoadModelCollection(**payload['Loads'])

    if storage_states:
        process_storage_states(storage_states)

    if load_data:
        loads = prepare_loads(network_node.consumers, unix_timestamp_seconds, load_data)
        generations: PowerGenerationCollection = fetch_generations(network_node.generators,
                                                               unix_timestamp_seconds)
        result = calculate_opf(unix_timestamp_seconds, loads, generations)

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
    network_node.consumers.Consumers = [c for c in network_node.consumers.Consumers
                                        if c.Identifier != consumer_identifier]
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
    network_node.generators.Generators = [c for c in network_node.generators.Generators
                                          if c.Identifier != generator_identifier]
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

@app_dat.application("storage/+/add")
async def storage_add_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    logging.debug("storage_add_callback: received request")
    storage_identifier = message.topic.split("/")[1]
    logging.info("add storage=%s", storage_identifier)
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    update = False
    for s in network_node.storages.Storages:
        if s.Identifier == storage_identifier:
            logging.info("update storage=%s", storage_identifier)
            update = True
    if not update:
        logging.info("add storage=%s", storage_identifier)
    network_node.storages.Storages = [s for s in network_node.storages.Storages
                                          if s.Identifier != storage_identifier]
    network_node.storages.Storages.append(StorageModel(**payload))

if __name__ == '__main__':
    app_dat.start()
    # we use the default scenario, loaded on script startup
    # opf = calculate_opf(1659439457)
    # print(opf)
