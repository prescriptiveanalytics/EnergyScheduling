import requests
import pandas as pd
import configuration_model

'''
This is a script to access the pvgis webpage (https://re.jrc.ec.europa.eu/pvg_tools/en/)
which downloads pv data of given position and parameters
and groups the kwh data by month, day, hour and minutes.
It returns the data as a dictionary.
'''

def query_pvgis(config_entry):
    data = None
    print('access pvgis...')
    response = requests.get(hourly_uri, params=config_entry.model_dump())
    if response.status_code == 200:
        print('access successful.')
        data = response.json()
    else:
        print('execution failed.')
    return data


def create_model(pv_configuration):
    dfs = []
    data_kwh = {}
    for config_entry in pv_configuration:
        query = query_pvgis(config_entry[1][0])
        df = process_data(query)
        dfs.append(df)
    # concat dfs
    print('create model_dict...')
    all_df = pd.concat(dfs)
    all_df = all_df.groupby(['month', 'day', 'hour', 'minute']).sum()
    all_df = all_df.reset_index()
    for index, row in all_df.iterrows():
        data_kwh[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['kwh']
    return data_kwh


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
    dfr_groupby = dfr.groupby(['month', 'day', 'hour', 'minute']).max()
    return dfr_groupby    


hourly_uri = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

required = [
    'lat',          # -90 <= lat <= 90
    'lon',          # -180 <= lat <= 180
    'peakpower',    # peakpower > 0
    'angle',        # 0 <= angle <= 90
    'aspect'        # -180 <= aspect <= 180
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
    e0 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=0)
    e1 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=180)
    e2 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=-180)
    config = configuration_model.Configuration(configuration=[e0, e1, e2])
    data_kwh = create_model(config)