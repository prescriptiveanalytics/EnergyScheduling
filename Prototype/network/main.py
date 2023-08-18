from fastapi import FastAPI
import pandapower as pp
import json
import requests
import logging

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = "config.json"
config = None

initialized = False
consumers = None
network = None

def load_config():
    with open(config_file, "r") as input_file:
        config = json.load(input_file)
        return config

def fetch_loads(consumers, unix_timestamp_seconds):
    consumer_loads = {}
    for c in consumers:
        logging.debug(f"request consumption for {c}")
        request_consumers = f"{config['consumer_api']}/consumer/{c['identifier']}/consumption/{unix_timestamp_seconds}"
        logging.debug(f"request consumption url {request_consumers}")
        result = requests.get(request_consumers)
        consumer_loads[c['identifier']] = json.loads(json.loads(result.text))
    logging.debug(f"fetched consumer loads: {consumer_loads}")
    return consumer_loads

def initialize_network(network_config, consumers, loads):
    # create network
    net = pp.create_empty_network()

    # create buses
    bus_data = network_config["bus"]
    buses = {} # dictionary holding all created buses
    for b in bus_data:
        bn = pp.create_bus(net, vn_kv=b["voltage"]/1000, name=b["identifier"])
        buses[b['identifier']] = bn

    # create grid connection
    grid_connections = [x for x in network_config["bus"] if x["type"] == "grid_connection"]
    if len(grid_connections) != 1:
        logging.error("No or more than one grid connection")
    gc = grid_connections[0]
    # logging.debug(f"grid_connection: {gc}")
    # gcb = pp.create_bus(net, vn_kv=gc["voltage"]/1000, name=gc["identifier"])
    gc_entity = [x for x in network_config["entities"] if x['identifier']==gc['identifier']][0]
    # buses[gc['identifier']] = gcb
    pp.create_ext_grid(net, bus=buses[gc['identifier']], vm_pu=1.02, name=gc_entity["name"])

    # create load
    for identifier, load in loads.items():
        logging.debug(f"consumer load for {identifier}: {load}")
        pp.create_load(net, bus=buses[identifier], p_mw=load['usage']/1000000, q_mvar=0.05, name=identifier)

    for line in network_config['lines']:
        logging.debug(f"create line from {line['from_bus']} to {line['to_bus']}")
        frombus = buses[line['from_bus']]
        tobus = buses[line['to_bus']]
        name = f"{line['from_bus']}-{line['to_bus']}"
        pp.create_line(net, from_bus=frombus, to_bus=tobus, length_km=line['length_km'], std_type=line['std_type'])

    logging.debug("run opf")
    pp.runpp(net)

    result = {}
    result['res_bus'] = json.loads(net.res_bus.to_json())
    result['res_line'] = json.loads(net.res_line.to_json())
    result['res_load'] = json.loads(net.res_load.to_json())
    result['res_ext_grid'] = json.loads(net.res_ext_grid.to_json())
    return json.dumps(result)


app = FastAPI()

@app.get("/")
def read_root():
    return { "Name": "network api" }

@app.get("/network")
def read_network():
    if not initialized:
        return { "Result": "Network not initialized, please call /initialize"}
    else:
        return json.dumps(config["network"])

@app.get("/initialize")
def read_initialize():
    global initialized
    global consumers
    global config
    logging.debug("/initialize")
    # read all customers, read network and set initialized to true
    config = load_config()
    logging.debug(f"config loaded: {config}")
    request_consumers = f"{config['consumer_api']}/consumer/all"
    result = requests.get(request_consumers)
    consumers = json.loads(json.loads(result.text))
    logging.debug(f"consumers loaded: {consumers}")
    initialized = True
    return { "Action": "initialize" }

@app.get("/opf/{unix_timestamp_seconds}")
def read_opf(unix_timestamp_seconds:int):
    global consumers
    global config
    global network
    if not initialized:
        return { "Result": "Network not initialized, please call /initialize"}
    loads = fetch_loads(consumers, unix_timestamp_seconds)
    opf = initialize_network(config["network"], consumers, loads)
    return opf