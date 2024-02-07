import requests
import pandas as pd
import configuration_model

from generator_model import PVGisGenerator

"""
PVGIS Data Query and Processing Script

This script retrieves hourly PV (Photovoltaic) data from the PVGIS API
(Photovoltaic Geographical Information System, https://re.jrc.ec.europa.eu/pvg_tools/en/),
processes the data, and creates a dictionary of time stamps and its production value in kWh.

Please enter your configurations in the main method on the bottom of this file.

"""

def query_pvgis(config_entry: configuration_model.ConfigurationEntry) -> dict:
    """
    Query PVGIS API for hourly data based on configuration entry.

    Args:
        config_entry (configuration_model.ConfigurationEntry): Configuration entry for PV system.

    Returns:
        dict: JSON response containing hourly PV data.
    """
    data = None
    print('access pvgis...')
    response = requests.get(hourly_uri, params=config_entry.model_dump())
    if response.status_code == 200:
        print('access successful.')
        data = response.json()
    else:
        print('execution failed.')
    return data


def process_data(query: dict) -> pd.DataFrame:
    """
    Process PV data retrieved from PVGIS API.

    Args:
        query (dict): JSON response containing hourly PV data.

    Returns:
        pandas.DataFrame: Processed PV data.
    """
    print('process data...')
    df = pd.json_normalize(query['outputs']['hourly'])
    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
    # Resample df
    dfi = df.set_index('time')
    dfr = dfi.resample('15min').bfill()
    dfr = dfr.resample('15min').ffill()
    dfr = dfr.reset_index()
    # Add column kwh: divide PV Power by 4 to get values for 15 minutes and by 1000 to get kW
    dfr['kwh'] = dfr['P'] / 4 / 1000
    # Add columns month, day, hour, minute
    dfr['month'] = dfr['time'].dt.month
    dfr['day'] = dfr['time'].dt.day
    dfr['hour'] = dfr['time'].dt.hour
    dfr['minute'] = dfr['time'].dt.minute
    # Drop column time
    dfr = dfr.drop('time', axis=1)
    dfr_groupby = dfr.groupby(['month', 'day', 'hour', 'minute']).max()
    return dfr_groupby


def create_model(pv_configuration: configuration_model.Configuration) -> dict:
    """
    Create a dictionary model based on PV configurations.

    Args:
        pv_configuration (configuration_model.Configuration): Configuration object containing PV system configurations.

    Returns:
        dict: Dictionary containing modeled PV data.
    """
    dfs = []
    data_kwh = {}
    for config_entry in pv_configuration.configuration:
        query = query_pvgis(config_entry)
        df = process_data(query)
        dfs.append(df)
    # Concatenate dfs and do data preprocessing
    print('create model dictionary...')
    all_df = pd.concat(dfs)
    all_df = all_df.groupby(['month', 'day', 'hour', 'minute']).sum()
    all_df = all_df.reset_index()
    for index, row in all_df.iterrows():
        data_kwh[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['kwh']
    return data_kwh


hourly_uri = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"


if __name__ == '__main__':
    # Example PV system configurations
    e0 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=0)
    e1 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=90)
    e2 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=-90)
    config = configuration_model.Configuration(configuration=[e0, e1, e2])
    # Create model dictionary
    data_kwh = create_model(config)