import os
import pandapower as pp
import json
import requests
import logging
from typing import List
from pathlib import Path

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
    scenario["network"] = NetworkModel(**scenario["network"])
    network_node.networks = ScenarioNetworkModel(network=scenario["network"])

logging.debug("initial network_node=%s", network_node)

def fetch_loads(consumers, unix_timestamp_seconds):
    consumer_loads = {}
    for c in consumers:
        logging.debug(f"request consumption for {c}")
        request_consumers = f"{config['consumer_api']}/consumer/{c.identifier}/consumption/{unix_timestamp_seconds}"
        logging.debug(f"request consumption url {request_consumers}")
        result = requests.get(request_consumers)
        logging.debug(f"got customer {c.identifier}={result.json()}")
        consumer_loads[c.identifier] = PowerConsumptionModel(**result.json())
    logging.debug(f"fetched consumer loads: {consumer_loads}")
    return consumer_loads

def fetch_generations(generators, unix_timestamp_seconds):
    generators_power = {}
    for g in generators:
        logging.debug(f"request generation for {g}")
        request_generators = f"{config['generator_api']}/generator/{g.identifier}/generation/{unix_timestamp_seconds}"
        logging.debug(f"request generator url {request_generators}")
        result = requests.get(request_generators)
        logging.debug(f"got generator {g.identifier}={result.json()}")
        generators_power[g.identifier] = PowerGenerationModel(**result.json())
    logging.debug(f"fetched generators: {generators_power}")
    return generators_power

# TODO:
def fetch_pvs(pvs, unix_timestamp_seconds):
    pv_power = {}
    for p in pvs:
        logging.debug(f"request pvnode for {p}")
        request_pvs = f"{config['pvnode_api']}/pvnode/{p.identifier}/pv/{unix_timestamp_seconds}"
        logging.debug(f"request pvnode url {request_pvs}")
        result = requests.get(request_pvs)
        logging.debug(f"got pvnode {p.identifier}={result.json()}")
        pv_power[p.identifier] = PowerPvModel(**result.json())
    logging.debug(f"fetched pvs: {pv_power}")
    return pv_power
# end TODO   

def initialize_network(network_config, generations: PowerGenerationCollection, loads: PowerConsumptionCollection) -> OptimalPowerFlowSolution:
    # create network
    logging.debug("initialize_network=%s", network_config)
    net = pp.create_empty_network()

    # create buses
    logging.debug("create buses")
    bus_data = network_config.bus
    buses = {} # dictionary holding all created buses
    for b in bus_data:
        logging.debug("create bus=%s", b.identifier)
        bn = pp.create_bus(net, vn_kv=b.voltage/1000, name=b.identifier)
        buses[b.identifier] = bn

    # create grid connection
    logging.debug(f"create network entities")
    grid_connections = [x for x in network_config.bus if x.type == "grid_connection"]
    if len(grid_connections) != 1:
        logging.error("No or more than one grid connection")
    gc = grid_connections[0]
    gc_entity = [x for x in network_config.entities if x.identifier == gc.identifier][0]
    pp.create_ext_grid(net, bus=buses[gc.identifier], vm_pu=1.02, name=gc_entity.name)

    # create load
    logging.debug(f"create loads")
    for identifier, load in loads.consumptions.items():
        logging.debug(f"consumer load for {identifier}: {load}")
        pp.create_load(net, bus=buses[identifier], p_mw=load.usage/1000000, q_mvar=0.05, name=identifier)

    logging.debug(f"create generations")
    for identifier, generation in generations.generations.items():
        logging.debug(f"generation power for {identifier}: {generation}")
        pp.create_sgen(net, bus=buses[identifier], p_mw=generation.generation/1000000, name=identifier)

    logging.debug(f"create lines")
    x = 1
    for line in network_config.lines:
        logging.debug(f"create line from {line.from_bus} to {line.to_bus}")
        frombus = buses[line.from_bus]
        tobus = buses[line.to_bus]
        name = f"{line.from_bus}-{line.to_bus}"
        #pp.create_line(net, from_bus=frombus, to_bus=tobus, length_km=line.length_km, std_type=line.std_type)
        pp.create_line_from_parameters(net, from_bus=frombus, to_bus=tobus, length_km=line.length_km, r_ohm_per_km=0.001, x_ohm_per_km=0, c_nf_per_km=0, r0_ohm_per_km=0, x0_ohm_per_km=0, c0_nf_per_km=0, max_i_ka=100)
        x += 1

    logging.debug("run opf")
    pp.runpp(net)
    logging.debug(f"keys in net={net.keys()}")
    logging.debug(f"calculated net={net}")

    result = {}
    result['bus'] = json.loads(net.bus.to_json())
    result['load'] = json.loads(net.load.to_json())
    result['line'] = json.loads(net.line.to_json())
    result['sgen'] = json.loads(net.sgen.to_json())
    result['res_bus'] = json.loads(net.res_bus.to_json())
    result['res_line'] = json.loads(net.res_line.to_json())
    result['res_load'] = json.loads(net.res_load.to_json())
    result['res_ext_grid'] = json.loads(net.res_ext_grid.to_json())
    result['res_sgen'] = json.loads(net.res_sgen.to_json())
    return OptimalPowerFlowSolution(**result)

# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)

async def fetch_loads_dat(consumers: ConsumerCollection, unix_timestamp_seconds: int, socket: SpaSocket):
    consumer_loads = {}
    for c in consumers.consumers:
        logging.debug("request consumption for %s", c)
        consumption = await socket.request(
            SpaMessage(
                topic = f"consumer/{c.identifier}/consumption",
                payload = str(unix_timestamp_seconds),
                # response_topic = f"consumer/{c.identifier}/consumption/response"
            )
        )
        consumer_loads[c.identifier] = json.loads(consumption.payload.decode('utf-8'))
    logging.debug("consumer_loads=%s", consumer_loads)
    return PowerConsumptionCollection(consumptions=consumer_loads)

async def fetch_generations_dat(generators: GeneratorCollection, unix_timestamp_seconds: int, socket: SpaSocket):
    generator_generations = {}
    for g in generators.generators:
        logging.debug("request generations for %s", g)
        generation = await socket.request(
            SpaMessage(
                topic = f"generator/{g.identifier}/generation",
                payload = str(unix_timestamp_seconds),
                # response_topic = f"generator/{g.identifier}/generation/response"
            )
        )
        generator_generations[g.identifier] = json.loads(generation.payload.decode('utf-8'))
    logging.debug("generation_generations=%s", generator_generations)
    return PowerGenerationCollection(generations=generator_generations)

async def query_network_participants_dat(network_node: NetworkNode, socket: SpaSocket):
    consumers_response = await socket.request(
        SpaMessage(
            payload = "",
            topic = "consumer/all",
            # response_topic= "consumer/all/response"
        )
    )
    logging.debug("received consumsers=%s", consumers_response)
    logging.debug("consumers=%s", consumers_response.payload)
    logging.debug("parsed json=%s", json.loads(consumers_response.payload.decode('utf-8')))
    consumers = ConsumerCollection(**json.loads(consumers_response.payload.decode('utf-8')))
    logging.info("parsed consumers=%s", consumers)
    network_node.consumers = consumers
    generators_response = await socket.request(
        SpaMessage(
            payload = "",
            topic = "generator/all",
        )
    )
    logging.debug("received generators=%s", generators_response)
    logging.debug("generators=%s", generators_response.payload)
    logging.debug("parsed json=%s", json.loads(generators_response.payload.decode('utf-8')))
    generators = GeneratorCollection(**json.loads(generators_response.payload.decode('utf-8')))
    network_node.generators = generators
    logging.debug("parsed generators=%s", generators)
    logging.debug("network_node=%s", network_node)
    network_node.initialized = True

@app_dat.application("network")
async def network_topic_endpoint_callback(message: SpaMessage, socket: SpaSocket, state: NetworkNode):
    """Basic network topic subscription"""
    logging.debug("network_topic_endpoint_callback=%s", message)
    await socket.publish(
        SpaMessage(
            payload="available",
            topic=message.response_topic
        )
    )

@app_dat.application("network/all")
async def network_all_endpoint_callback(message: SpaMessage, socket: SpaSocket, state: NetworkNode):
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
                content_type = "application/json",
                payload = network_node.networks.model_dump_json(),
                topic = message.response_topic
            )
        )

@app_dat.application("network/opf")
async def network_opf_query_callback(message: SpaMessage, socket: SpaSocket, state: NetworkNode):
    global network_node
    logging.debug("network_opf_query_callback=%s", message)
    logging.debug("network_opf_query_callback: state=%s", state)

    unix_timestamp_seconds = int(message.payload)

    if not network_node.initialized:
        logging.info("initialize network")
        await query_network_participants_dat(network_node, socket)
        if network_node.initialized:
            logging.debug("network successfully initialized")
    
    if network_node.initialized:
        loads: PowerConsumptionCollection = await fetch_loads_dat(network_node.consumers, unix_timestamp_seconds, socket)
        generations: PowerGenerationCollection = await fetch_generations_dat(network_node.generators, unix_timestamp_seconds, socket)
        opf = initialize_network(network_node.networks.network, generations, loads)
        logging.debug("opf=%s", opf)
        await socket.publish(
            SpaMessage(
                content_type="application/json",
                payload = opf.model_dump_json(),
                topic=message.response_topic
            )
        )

    else:
        logging.debug("error: network not initialized")
        await socket.publish(
            SpaMessage(
                payload = "error: network could not be initialized",
                topic=message.response_topic
            )
        )

@app_dat.application("network/scenario")
async def network_scenario_update_callback(message: SpaMessage, socket: SpaSocket, state: NetworkNode):
    global network_node
    payload = json.loads(message.payload)
    logging.debug("update scenario=%s", payload)
    scenario_identifier = payload['scenario_identifier']
    network_node = NetworkNode(scenario_identifier=scenario_identifier)
    snm = NetworkModel(**payload['network'])
    network_node.networks = ScenarioNetworkModel(network=snm)
    logging.debug("update scenario network_node=%s", network_node)

if __name__ == '__main__':
    app_dat.start()
