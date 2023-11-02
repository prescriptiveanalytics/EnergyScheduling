import os
import pandas as pd
import requests
import json
import datetime
import logging
from typing import List, Dict

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

""" 
This Python script is used for querying and processing data related to a power grid scenario. It sets up an environment 
for distributed applications using MQTT, loads configuration from a JSON file and defines various callback functions to query and 
process data related to consumers, generators and the network. The script also includes functions for retrieving data and time 
series information, with a focus on processing and analyzing data related to power load, generators and network entities within 
the power grid scenario.
"""

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
config_file = "config.json"
with open(config_file, "r") as input_file:
    config = json.load(input_file)

config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)

# define spa producer callback decorators
app_consumer = DistributedApplication(socket_provider)
app_generator = DistributedApplication(socket_provider)
app_generator_update_model = DistributedApplication(socket_provider)
app_network = DistributedApplication(socket_provider)
app_network_opf = DistributedApplication(socket_provider)

class ScenarioState:
    """Stores the state of the queries"""
    consumer: str | None = None
    generator: str | None = None
    network: str | None = None
    network_opf: Dict[str, str] | None = None
    query_times: List[int] | None = None

scenario_state = ScenarioState()

class UpdateGeneratorModel:
    identifier: str | None = None
    encoded_model: str | None = None

update_generator_model = UpdateGeneratorModel()

@app_consumer.producer()
async def query_consumers(socket: SpaSocket, state):
    logging.debug("received query_consumers")
    consumers_response = await socket.request(
        SpaMessage(
            payload = "",
            topic = "consumer/all",
        )
    )
    logging.debug("received consumers=%s", consumers_response)
    scenario_state.consumer = json.loads(consumers_response.payload)
    logging.debug("state.consumer=%s", scenario_state.consumer)

@app_generator.producer()
async def query_generators(socket: SpaSocket, state):
    logging.debug("received query_generators")
    generators_response = await socket.request(
        SpaMessage(
            payload = "",
            topic = "generator/all",
        )
    )
    logging.debug("received generators=%s", generators_response)
    scenario_state.generator = json.loads(generators_response.payload)
    logging.debug("scenario_state.generators=%s", scenario_state.generator)

@app_network.producer()
async def query_network(socket: SpaSocket, state):
    logging.debug("received query_network")
    network_response = await socket.request(
        SpaMessage(
            payload = "",
            topic = "network/all",
        )
    )
    logging.debug("received networks=%s", network_response)
    scenario_state.network = json.loads(network_response.payload)
    logging.debug("scenario_state.network=%s", scenario_state.network)

@app_network_opf.producer()
async def query_range(socket: SpaSocket, state):
    opf = {}
    logging.debug("query_range %s", scenario_state.query_times)
    if scenario_state.query_times:
        for ts in scenario_state.query_times:
            logging.debug("query opf for %s", ts)
            network_opf_response = await socket.request(
                SpaMessage(
                    payload = str(ts),
                    topic = "network/opf",
                )
            )
            opf[ts] = json.loads(network_opf_response.payload)

    scenario_state.network_opf = opf

@app_generator_update_model.producer()
async def generator_update_model(socket: SpaSocket, state):
    await socket.publish(
        SpaMessage(
            content_type = 'application/json',
            payload = json.dumps({ 'file': update_generator_model.encoded_model }),
            topic = f"generator/{update_generator_model.identifier}/model"
        )
    )


def get_consumer_lat_lon(identifier, consumers):
    return [{ 'latitude': x['latitude'], 'longitude': x['longitude']}  for x in consumers if x['identifier'] == identifier][0]

def get_network_entity_lat_lon(identifier, entities):
    return [{ 'latitude': x['latitude'], 'longitude': x['longitude']} for x in entities if x['identifier'] == identifier][0]

def get_nodes(consumers, generators, network) -> pd.DataFrame:
    data = {}
    data['name'] = [x['name'] for x in consumers]
    data['identifier'] = [x['identifier'] for x in consumers]
    data['latitude'] = [x['latitude'] for x in consumers]
    data['longitude'] = [x['longitude'] for x in consumers]
    data['category'] = [x['category'] for x in consumers]
    data['type'] = [x['type'] for x in consumers]

    data['name'] += [x['name'] for x in generators]
    data['identifier'] += [x['identifier'] for x in generators]
    data['latitude'] += [x['latitude'] for x in generators]
    data['longitude'] += [x['longitude'] for x in generators]
    data['category'] += [x['category'] for x in generators]
    data['type'] += [x['type'] for x in generators]

    data['name'] += ([x['name'] for x in network['entities']])
    data['identifier'] += ([x['identifier'] for x in network['entities']])
    data['latitude'] += ([x['latitude'] for x in network['entities']])
    data['longitude'] += ([x['longitude'] for x in network['entities']])
    data['category'] += [x['category'] for x in network['entities']]
    data['type'] += [x['type'] for x in network['entities']]

    return pd.DataFrame(data=data)

def get_line_connections(consumers, generators, network) -> pd.DataFrame:
    latitudes = []
    longitudes = []
    identifiers = []

    consumer_ids = [c['identifier'] for c in consumers]
    generator_ids = [g['identifier'] for g in generators]
    network_entity_ids = [n['identifier'] for n in network['entities']]

    for line in network['lines']:
        fb = line['from_bus']
        tb = line['to_bus']        
        if fb in consumer_ids:
            lt = get_consumer_lat_lon(fb, consumers)
            longitudes.append(lt['longitude'])
            latitudes.append(lt['latitude'])
            identifiers.append(fb)
        elif fb in network_entity_ids:
            lt = get_network_entity_lat_lon(fb, network['entities'])
            longitudes.append(lt['longitude'])
            latitudes.append(lt['latitude'])
            identifiers.append(fb)
        elif fb in generator_ids:
            lt = get_consumer_lat_lon(fb, generators)
            longitudes.append(lt['longitude'])
            latitudes.append(lt['latitude'])
            identifiers.append(fb)
        else:
            print(f"identifier {fb} not found")
        if tb in consumer_ids:
            lt = get_consumer_lat_lon(tb, consumers)
            longitudes.append(lt['longitude'])
            latitudes.append(lt['latitude'])
            identifiers.append(tb)            
        elif tb in network_entity_ids:
            lt = get_network_entity_lat_lon(tb, network['entities'])
            longitudes.append(lt['longitude'])
            latitudes.append(lt['latitude'])
            identifiers.append(tb)  
        elif tb in generator_ids:
            lt = get_consumer_lat_lon(tb, generators)
            longitudes.append(lt['longitude'])
            latitudes.append(lt['latitude'])
            identifiers.append(tb)          
        else:
            print(f"identifier {tb} not found")        
    data = { 'identifier': identifiers, 'longitude': longitudes, 'latitude': latitudes }
    return pd.DataFrame(data=data)

def create_node_identifier_mapping(nodes_dataframe):
    t = nodes_dataframe.reset_index()
    return dict(zip(t.index, t.identifier))

def create_identifier_name_mapping(nodes_dataframe):
    t = nodes_dataframe.reset_index()
    return dict(zip(t.identifier, t.name))
 
# create load dataset
def create_load_dataframe(consumers, network, opf):
    load = opf['load']
    data = {}
    identifiers = [v for k, v in load['name'].items()]
    #print(identifiers)
    reverse_map ={ v: k for k, v in load['name'].items() }
    loads = [load['p_mw'][reverse_map[k]] for k in identifiers]
    #print(loads)
    data['identifier'] = identifiers
    data['load'] = loads
    return pd.DataFrame(data=data)

# create consumer load timeseries
def load_ts(nodes_df, opfs):
    node_identifier_map = create_node_identifier_mapping(nodes_df)
    opf_keys = [k for k in sorted(opfs.keys())]
    dataframes = []
    for ok in opf_keys:
        o = opfs[ok]
        df1 = pd.DataFrame(o['res_load'])
        df1 = df1.reset_index()
        df1['node_id'] = df1['index'].astype('int64')
        #df2 = nodes_df.reset_index()
        #df2['idx'] =df2['index'].astype('int64')
        #dataframe = df1.join(df2, on='idx')
        dataframe = df1
        dataframe['time'] = datetime.datetime.fromtimestamp(ok)
        dataframes.append(dataframe)
    res_load_ts = pd.concat(dataframes).reset_index()[['node_id', 'p_mw', 'q_mvar', 'time']]
    res_load_ts['identifier'] = res_load_ts['node_id'].map(node_identifier_map)
    res_load_ts = res_load_ts[['p_mw', 'q_mvar', 'time', 'identifier']]
    return res_load_ts
   
def bus_ts(nodes_df, opfs):
    node_identifier_map = create_node_identifier_mapping(nodes_df)
    opf_keys = [k for k in sorted(opfs.keys())]
    dataframes = []
    for ok in opf_keys:
        o = opfs[ok]
        df1 = pd.DataFrame(o['res_bus'])
        df1 = df1.reset_index()
        df1['node_id'] = df1['index'].astype('int64')
        #df2 = nodes_df.reset_index()
        #df2['idx'] =df2['index'].astype('int64')
        #dataframe = df1.join(df2, on='idx')
        dataframe = df1
        dataframe['time'] = datetime.datetime.fromtimestamp(ok)
        dataframes.append(dataframe)
    res_bus_ts = pd.concat(dataframes).reset_index()[['node_id', 'p_mw', 'q_mvar', 'time']]
    res_bus_ts['identifier'] = res_bus_ts['node_id'].map(node_identifier_map)
    res_bus_ts = res_bus_ts[['p_mw', 'q_mvar', 'time', 'identifier']]
    res_bus_ts['abs_p_mw'] = abs(res_bus_ts['p_mw'])
    return res_bus_ts

def ext_grid_ts(nodes_df, opfs):
    node_identifier_map = create_node_identifier_mapping(nodes_df)
    opf_keys = [k for k in sorted(opfs.keys())]
    dataframes = []
    for ok in opf_keys:
        o = opfs[ok]
        node_identifier_map = o['sgen']
        df1 = pd.DataFrame(o['res_ext_grid'])
        df1['time'] = datetime.datetime.fromtimestamp(ok)
        dataframes.append(df1)
    ext_grid_ts = pd.concat(dataframes)
    return ext_grid_ts

def gen_ts(nodes_df, opfs):
    opf_keys = [k for k in sorted(opfs.keys())]
    node_identifier_map = opfs[opf_keys[0]]['sgen']['name']
    dataframes = []
    for ok in opf_keys:
        o = opfs[ok]
        df1 = pd.DataFrame(o['res_sgen'])
        df1['time'] = datetime.datetime.fromtimestamp(ok)
        df1 = df1.reset_index()
        df1['index'].astype(int)
        df1['identifier'] = df1.reset_index()['index'].map(node_identifier_map)
        df1[['p_mw', 'q_mvar', 'time', 'identifier']]
        dataframes.append(df1)
    gen_ts = pd.concat(dataframes)
    return gen_ts

def get_scenario_dataframes(nodes_df, scenario, scenario_name):
    res_load_ts = load_ts(nodes_df, scenario)
    res_load_ts['scenario'] = scenario_name
    res_sum_load_ts = res_load_ts[['time', 'p_mw', 'q_mvar']].groupby(by=['time']).sum().reset_index().sort_values(by=['time'])
    res_sum_load_ts['scenario'] = scenario_name
    res_ext_grid_ts = ext_grid_ts(nodes_df, scenario)
    res_ext_grid_ts['scenario'] = scenario_name
    res_gen_ts = gen_ts(nodes_df, scenario)
    res_gen_ts['scenario'] = scenario_name

    sum_grid = res_ext_grid_ts['p_mw'].sum()
    sum_load = res_sum_load_ts['p_mw'].sum()
    sum_generation = res_gen_ts['p_mw'].sum()
    return res_sum_load_ts, res_ext_grid_ts, res_gen_ts