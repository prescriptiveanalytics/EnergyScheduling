import pandas as pd
import requests
import json
import datetime

# read consumer data: config['consumer_api']
def query_consumers(base_consumer_url):
    request_consumers = f"{base_consumer_url}/consumer/all"
    result = requests.get(request_consumers)
    consumers = json.loads(result.text)
    return consumers

# read all generators: config['generator_api']
def query_generators(base_generator_url):
    request_generators = f"{base_generator_url}/generator/all"
    result = requests.get(request_generators)
    generators = json.loads(result.text)
    return generators


# read network data, config['network_api']
def query_network(base_network_uri):
    initialize_network = f"{base_network_uri}/initialize"
    request_initialize = requests.get(initialize_network)

    request_network = f"{base_network_uri}/network"
    result = requests.get(request_network)
    network = json.loads(result.text)
    return network

def query_range(queries, base_network_uri):
    opfs = {}
    for ts in queries:
        request_opf = f"{base_network_uri}/opf/{ts}"
        result = requests.get(request_opf)
        opfs[ts] = json.loads(result.text)
    return opfs

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
    
# # create load dataset
# def create_load_dataframe(consumers, network, opf):
#     load = opf['load']
#     data = {}
#     identifiers = [v for k, v in load['name'].items()]
#     #print(identifiers)
#     reverse_map ={ v: k for k, v in load['name'].items() }
#     loads = [load['p_mw'][reverse_map[k]] for k in identifiers]
#     #print(loads)
#     data['identifier'] = identifiers
#     data['load'] = loads
#     return pd.DataFrame(data=data)

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