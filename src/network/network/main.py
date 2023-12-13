import os
import pandapower as pp
import json
import requests
import logging
from typing import List
from pathlib import Path
import base64

import humps

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

config_file = Path("config.json")
config = None

with open(config_file, "rt") as input_file:
    config = json.load(input_file)
# end TODO

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

initialized: bool = False
consumers: ConsumerCollection = None
generators: GeneratorCollection = None
network: NetworkModel = None

network_node: NetworkNode = NetworkNode("")

scenario_file = Path("configurations/ex0_one_consumer/config.json")
scenario = None
with open(scenario_file, "r") as input_file:
    logging.debug("read scenario file")
    scenario = json.load(input_file)
    scenario["Network"] = NetworkModel(**scenario["Network"])
    network_node.networks = ScenarioNetworkModel(Network=scenario["Network"])

logging.debug("initial network_node=%s", network_node)

def initialize_network(network_config, generations: PowerGenerationCollection, loads: PowerConsumptionCollection) -> OptimalPowerFlowSolution:
    # create network
    logging.debug("initialize_network=%s", network_config)
    net = pp.create_empty_network()

    # create buses
    logging.debug("create buses")
    bus_data = network_config.Buses
    buses = {} # dictionary holding all created buses
    for b in bus_data:
        logging.debug("create bus=%s", b.Identifier)
        bn = pp.create_bus(net, vn_kv=b.Voltage/1000, name=b.Identifier)
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
        pp.create_load(net, bus=buses[identifier], p_mw=load.Usage/1000000, q_mvar=0.05, name=identifier)

    logging.debug("create generations")
    for identifier, generation in generations.Generations.items():
        logging.debug(f"generation power for {identifier}: {generation}")
        pp.create_sgen(net, bus=buses[identifier], p_mw=generation.Generation/1000000, name=identifier)

    logging.debug("create lines")
    x = 1
    for line in network_config.Lines:
        logging.debug(f"create line from {line.FromBus} to {line.ToBus}")
        frombus = buses[line.FromBus]
        tobus = buses[line.ToBus]
        name = f"{line.FromBus}-{line.ToBus}"
        #pp.create_line(net, from_bus=frombus, to_bus=tobus, length_km=line.length_km, std_type=line.std_type)
        pp.create_line_from_parameters(net, from_bus=frombus, to_bus=tobus, length_km=line.LengthKm, r_ohm_per_km=0.001, x_ohm_per_km=0, c_nf_per_km=0, r0_ohm_per_km=0, x0_ohm_per_km=0, c0_nf_per_km=0, max_i_ka=100)
        x += 1

    logging.debug("run opf")
    pp.runpp(net)
    logging.debug(f"keys in net={net.keys()}")
    logging.debug(f"calculated net={net}")

    result = {}
    result['Bus'] = json.loads(net.bus.to_json())
    result['Load'] = json.loads(net.load.to_json())
    result['Line'] = json.loads(net.line.to_json())
    result['Sgen'] = json.loads(net.sgen.to_json())
    result['ResBus'] = json.loads(net.res_bus.to_json())
    result['ResLine'] = json.loads(net.res_line.to_json())
    result['ResLoad'] = json.loads(net.res_load.to_json())
    result['ResExtGrid'] = json.loads(net.res_ext_grid.to_json())
    result['ResSgen'] = json.loads(net.res_sgen.to_json())
    result = humps.pascalize(result)
    logging.debug("result=%s", result)
    return OptimalPowerFlowSolution(**result)

# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)

async def fetch_loads_dat(consumers: ConsumerCollection, unix_timestamp_seconds: int, socket: SpaSocket):
    consumer_loads = {}
    json_message = { 'UnixTimestampSeconds': unix_timestamp_seconds }
    payload_message = base64.b64encode(json.dumps(json_message).encode('utf-8'))
    for c in consumers.Consumers:
        logging.debug("request consumption for %s", c)
        consumption = await socket.request(
            SpaMessage(
                Topic = f"consumer/{c.Identifier}/consumption",
                Payload = payload_message #str(unix_timestamp_seconds)
            )
        )
        cnt = consumption.payload.decode("utf-8")
        usable_payload = base64.b64decode(cnt)
        payload = json.loads(usable_payload)
        consumer_loads[c.Identifier] = payload
    logging.debug("consumer_loads=%s", consumer_loads)
    return PowerConsumptionCollection(Consumptions=consumer_loads)

async def fetch_generations_dat(generators: GeneratorCollection, unix_timestamp_seconds: int, socket: SpaSocket):
    generator_generations = {}
    json_message = { 'UnixTimestampSeconds': unix_timestamp_seconds }
    payload_message = base64.b64encode(json.dumps(json_message).encode('utf-8'))
    for g in generators.Generators:
        logging.debug("request generations for %s", g)
        generation = await socket.request(
            SpaMessage(
                Topic = f"generator/{g.Identifier}/generation",
                Payload = payload_message #str(unix_timestamp_seconds)
            )
        )
        cnt = generation.payload.decode("utf-8")
        usable_payload = base64.b64decode(cnt)
        payload = json.loads(usable_payload)
        generator_generations[g.Identifier] = payload
    logging.debug("generation_generations=%s", generator_generations)
    return PowerGenerationCollection(Generations=generator_generations)

async def query_network_participants_dat(network_node: NetworkNode, socket: SpaSocket):
    consumers_response = await socket.request(
        SpaMessage(
            Payload = "",
            Topic = "consumer/all"
        )
    )
    logging.debug("received consumsers=%s", consumers_response)

    # TODO: rewrite this part
    logging.debug("consumers=%s", consumers_response.payload)
    cnt = consumers_response.payload.decode('utf-8')
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    logging.debug("parsed consumers json=%s", payload)
    consumers = ConsumerCollection(**payload)
    logging.info("parsed consumers=%s", consumers)
    network_node.consumers = consumers

    generators_response = await socket.request(
        SpaMessage(
            Payload = "",
            Topic = "generator/all",
        )
    )
    logging.debug("received generators=%s", generators_response)
    logging.debug("generators=%s", generators_response.payload)
    cnt = generators_response.payload.decode('utf-8')
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    logging.debug("parsed generators json=%s", payload)
    generators = GeneratorCollection(**payload)
    network_node.generators = generators
    logging.debug("parsed generators=%s", generators)
    logging.debug("network_node=%s", network_node)
    network_node.initialized = True

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
        await query_network_participants_dat(network_node, socket)
        if network_node.initialized:
            logging.debug("network successfully initialized")
    
    if network_node.initialized:
        logging.debug("return network")
        await socket.publish(
            SpaMessage(
                ContentType = "application/json",
                Payload = network_node.networks.model_dump_json(),
                Topic = message.response_topic
            )
        )

# @app_dat.application("network/opf")
# async def network_opf_query_callback(message: SpaMessage, socket: SpaSocket, state: NetworkNode):
#     global network_node
#     logging.debug("network_opf_query_callback=%s", message)
#     logging.debug("network_opf_query_callback: state=%s", state)

#     unix_timestamp_seconds = int(message.payload)

#     if not network_node.initialized:
#         logging.info("initialize network")
#         await query_network_participants_dat(network_node, socket)
#         if network_node.initialized:
#             logging.debug("network successfully initialized")
    
#     if network_node.initialized:
#         loads: PowerConsumptionCollection = await fetch_loads_dat(network_node.consumers, unix_timestamp_seconds, socket)
#         generations: PowerGenerationCollection = await fetch_generations_dat(network_node.generators, unix_timestamp_seconds, socket)
#         opf = initialize_network(network_node.networks.network, generations, loads)
#         logging.debug("opf=%s", opf)
#         await socket.publish(
#             SpaMessage(
#                 content_type="application/json",
#                 payload = opf.model_dump_json(),
#                 topic=message.response_topic
#             )
#         )

#     else:
#         logging.debug("error: network not initialized")
#         await socket.publish(
#             SpaMessage(
#                 payload = "error: network could not be initialized",
#                 topic=message.response_topic
#             )
#         )

@app_dat.application("network/opf")
async def network_opf_query_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global network_node
    logging.debug("network_opf_query_callback=%s", message)

    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    # payload = humps.decamelize(payload)

    unix_timestamp_seconds = int(payload['UnixTimestampSeconds'])

    if not network_node.initialized:
        logging.info("initialize network")
        await query_network_participants_dat(network_node, socket)
        if network_node.initialized:
            logging.debug("network successfully initialized")
    
    if network_node.initialized:
        loads: PowerConsumptionCollection = await fetch_loads_dat(network_node.consumers, unix_timestamp_seconds, socket)
        generations: PowerGenerationCollection = await fetch_generations_dat(network_node.generators, unix_timestamp_seconds, socket)
        opf = initialize_network(network_node.networks.Network, generations, loads)
        # TODO: convert opf json into correct payload format.
        logging.debug("opf=%s", opf)
        t1 = base64.b64encode(opf.model_dump_json().encode("utf-8"))

        await socket.publish(
            SpaMessage(
                ContentType="application/json",
                Payload = t1,
                Topic=message.response_topic
            )
        )

    else:
        logging.debug("error: network not initialized")
        await socket.publish(
            SpaMessage(
                Payload = "error: network could not be initialized",
                Topic=message.response_topic
            )
        )

# @app_dat.application("network/scenario")
# async def network_scenario_update_callback(message: SpaMessage, socket: SpaSocket, state: NetworkNode):
#     global network_node
#     payload = json.loads(message.payload)
#     logging.debug("update scenario=%s", payload)
#     scenario_identifier = payload['scenario_identifier']
#     network_node = NetworkNode(scenario_identifier=scenario_identifier)
#     snm = NetworkModel(**payload['network'])
#     network_node.networks = ScenarioNetworkModel(network=snm)
#     logging.debug("update scenario network_node=%s", network_node)

@app_dat.application("network/scenario")
async def network_scenario_update_callback(message: SpaMessage, socket: SpaSocket, **kwargs):
    global network_node
    logging.debug("update scenario=%s", message)
    cnt = message.payload.decode("utf-8")
    usable_payload = base64.b64decode(cnt)
    payload = json.loads(usable_payload)
    scenario_identifier = payload['ScenarioIdentifier']
    network_node = NetworkNode(scenario_identifier=scenario_identifier)
    snm = NetworkModel(**payload['Network'])
    network_node.networks = ScenarioNetworkModel(Network=snm)
    logging.debug("update scenario network_node=%s", network_node)

if __name__ == '__main__':
    app_dat.start()
