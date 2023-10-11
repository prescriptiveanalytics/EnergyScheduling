import requests
import pandas as pd
import configuration_model
import generator_model
import dill as pickle
import json
import os

'''
This is a script to access the pvgis webpage (https://re.jrc.ec.europa.eu/pvg_tools/en/)
which downloads pv data of a given position and given parameters.
It returns and saves the data in form of a serialized bytes model.
'''

def query_pvgis(config_entry):
    data = None
    print('access pvgis...')
    
    # if os.path.exists("temp/query_pvgis.txt"):
    #     # load query from file
    #     with open("temp/query_pvgis.txt", "r") as f:
    #         data = json.load(f)
    # else:
    response = requests.get(hourly_uri, params=config_entry.model_dump())
    if response.status_code == 200:
        print('access successful.')
        data = response.json()
    else:
        print('execution failed.')
    # save data to analyse
    # with open("temp/query_pvgis.txt", "w") as f:
    #     json.dump(data, f)
    return data


def create_model(pv_configuration):
    dfs = []
    data_kwh = {}
    # fetch data from pvgis
    for config_entry in pv_configuration:
        query = query_pvgis(config_entry[1][0])
        df = process_data(query)
        dfs.append(df)
    print('create dictionary...')
    # concat dfs
    all_df = pd.concat(dfs)
    all_df = all_df.groupby(['month', 'day', 'hour', 'minute']).sum()
    all_df = all_df.reset_index()
    # create dict
    for index, row in all_df.iterrows():
        data_kwh[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['kwh']
    # create model from dict    
    print('create model...')
    model = generator_model.PVGisGenerator('anlage1', data_kwh)
    # serialize and return model as binary
    model_binary = pickle.dumps(model)
    return model_binary


def process_data(query):
    print('process data...')
    df = pd.json_normalize(query['outputs']['hourly'])
    # convert time to datetime
    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
    # resample df
    dfi = df.set_index('time')
    dfr = dfi.resample('15min').bfill()
    dfr = dfr.resample('15min').ffill()
    dfr = dfr.reset_index()
    # add column kwh
    dfr['kwh'] = dfr['P'] / 4 / 1000
    # add columns month, day, hour, minute
    dfr['month'] = dfr['time'].dt.month
    dfr['day'] = dfr['time'].dt.day
    dfr['hour'] = dfr['time'].dt.hour
    dfr['minute'] = dfr['time'].dt.minute
    # drop column time
    dfr = dfr.drop('time', axis=1)
    # group df by month, day, hour, minute
    dfr_groupby = dfr.groupby(['month', 'day', 'hour', 'minute']).max()
    return dfr_groupby    


hourly_uri = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

required = [
    'lat',          # -90 <= lat <= 90
    'lon',          # -180 <= lat <= 180
    'peakpower',    # peakpower > 0
    'angle',        # 0 <= angle <= 90
    'aspect'        # -180 <= aspect <= 180 -- 0=south, 90=west, -90=east, north=+/-180
]

optional_default = {
    'loss': 14,                     # 0 <= loss <= 100
    'outputformat': 'json',         # ['json', 'csv']
    'mountingplace': 'building',    # ['free', 'building']
    'startyear': 2005,              # 2005 <= startyear <= 2020
    'endyear': 2020,                # 2005 <= endyear <= 2020   AND endyear should be >= to startyear
    'usehorizon': 1,                # 0 or 1 boolean
    'pvcalculation': 1              # 0 or 1 boolean -> only when mounting == Fixed
}


if __name__ == '__main__':
    e0 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=7, angle=22, aspect=0)
    e1 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1.5, angle=22, aspect=-90)
    e2 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1.5, angle=22, aspect=90)
    config = configuration_model.Configuration(configuration=[e0, e1, e2])
    # config = configuration_model.Configuration(configuration=[e0, e1])
    model = create_model(config)
    # save model
    with open("models/hgb_south_7kwp_east_1.5kwp_west_1.5kwp", "wb") as of:
        of.write(model)