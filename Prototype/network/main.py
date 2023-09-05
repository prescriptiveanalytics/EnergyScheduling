from fastapi import FastAPI
import pandapower as pp
import json
import requests
import logging
from typing import List
from pathlib import Path
from domain_models.NetworkModel import NetworkModel, ScenarioNetworkModel
from domain_models.PowerConsumptionModel import PowerConsumptionModel
from domain_models.ConsumerModel import ConsumerModel
from domain_models.GeneratorModel import GeneratorModel
from domain_models.PowerGenerationModel import PowerGenerationModel
from domain_models.OptimalPowerFlow import OptimalPowerFlowSolution

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = Path("configurations/ex0_one_consumer/config.json")
config = None

with open(config_file, "r") as input_file:
    config = json.load(input_file)
    config["network"] = NetworkModel(**config["network"])

initialized: bool = False
consumers: List[ConsumerModel] = None
generators: List[GeneratorModel] = None
network: NetworkModel = None

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

def initialize_network(network_config, consumers, generations, loads):
    # create network
    logging.debug(f"initialize_network={network_config}")
    net = pp.create_empty_network()

    # create buses
    logging.debug(f"create buses")
    bus_data = network_config.bus
    buses = {} # dictionary holding all created buses
    for b in bus_data:
        logging.debug(f"create bus {b.identifier}")
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
    for identifier, load in loads.items():
        logging.debug(f"consumer load for {identifier}: {load}")
        pp.create_load(net, bus=buses[identifier], p_mw=load.usage/1000000, q_mvar=0.05, name=identifier)

    logging.debug(f"create generations")
    for identifier, generation in generations.items():
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
    return result

app = FastAPI()

@app.get("/")
def read_root():
    return { "Name": "network api" }

@app.get("/network")
def read_network():
    if not initialized:
        return { "Result": "Network not initialized, please call /initialize"}
    else:
        return network

@app.get("/initialize")
def read_initialize():
    global initialized
    global consumers
    global generators
    global config
    global network
    logging.debug("/initialize")
    network = config["network"].network #NetworkModel(**config["network"])
    logging.debug(f"config loaded: {config}")
    request_consumers = f"{config['consumer_api']}/consumer/all"
    result = requests.get(request_consumers)
    logging.debug(f"result.text={result.text}")
    consumers = [ConsumerModel(**consumer) for consumer in json.loads(result.text)]
    logging.debug(f"consumers loaded: {consumers}")
    request_generators = f"{config['generator_api']}/generator/all"
    result = requests.get(request_generators)
    generators = [GeneratorModel(**generator) for generator in json.loads(result.text)]
    logging.debug(f"generators loaded: {generators}")
    initialized = True
    return { "Action": "initialize" }

@app.get("/opf/{unix_timestamp_seconds}")
def read_opf(unix_timestamp_seconds:int):
    global consumers
    global generators
    global config
    global network
    if not initialized:
        return { "Result": "Network not initialized, please call /initialize"}
    loads: PowerConsumptionModel = fetch_loads(consumers, unix_timestamp_seconds)
    generations: PowerGenerationModel = fetch_generations(generators, unix_timestamp_seconds)
    opf = initialize_network(network, consumers, generations, loads)
    # return opf
    return OptimalPowerFlowSolution(**opf)

@app.post("/scenario/{identifier}")
def create_scenario(identifier: str, scenario_data: ScenarioNetworkModel):
    global initialized
    global consumers
    global generators
    global config
    global network
    initialized = False
    logging.debug(f"load new scenario {identifier}")
    logging.debug(f"scenario data: {scenario_data}")
    config["network"] = scenario_data
    logging.debug(f"new config={config}")
    return { "Status": "Success" }