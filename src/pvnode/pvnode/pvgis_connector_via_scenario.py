import requests
import pandas as pd
import configuration_model
import dill as pickle
import json

from generator_model import PVGisGenerator

"""
PVGIS Data Query and Processing Script

This script retrieves hourly PV (Photovoltaic) data based on a given scenario file from the PVGIS API
(Photovoltaic Geographical Information System, https://re.jrc.ec.europa.eu/pvg_tools/en/),
processes the data, and creates a dictionary of time stamps and its production value in kWh.
It saves the dictionary as a binary model.

Please enter your configurations in the main method on the bottom of this file.

"""

hourly_uri = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"


def query_pvgis(config_entry: configuration_model.ConfigurationEntry) -> dict:
    """
    Query PVGIS API for hourly data based on the configurations set in the scenario file.

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
    # Add column kwh
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


def create_model(pv_configuration_list: list) -> list:
    """
    Create model dictionaries based on PV configurations.

    Args:
        pv_configuration_list (list): List of Configuration objects containing PV system configurations.

    Returns:
        list: List of model dictionaries containing modeled PV data.
    """
    data = []
    for configuration in pv_configuration_list:
        dfs = []
        for config_entry in configuration.configuration:
            query = query_pvgis(config_entry)
            df = process_data(query)
            dfs.append(df)
        # Concatenate dfs and do data preprocessing
        print('create model_dict...')
        all_df = pd.concat(dfs)
        all_df = all_df.groupby(['month', 'day', 'hour', 'minute']).sum()
        all_df = all_df.reset_index()
        data_kwh = {}
        for index, row in all_df.iterrows():
            data_kwh[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['kwh']
        data.append(data_kwh)
    return data


def get_configurations(filename: str) -> tuple:
    """
    Load PV system configurations from a JSON scenario file.

    Args:
        filename (str): Path to the JSON file containing PV system configurations.

    Returns:
        tuple: A tuple containing a list of model filenames and a list of Configuration objects.
    """
    with open(filename, "r") as f:
        input = f.read()
    scenario = json.loads(input)
    producer = scenario["Scenario"]["Producer"]
    configurations = []
    model_filenames = []
    cnt = 1
    # Loop through all configs
    for p in producer:
        config_list = []
        model_filenames.append(p["ModelIdentifier"])
        for config_entry in p["ConfigurationEntries"]:
            e = configuration_model.ConfigurationEntry(
                lat=config_entry["latitude"],
                lon=config_entry["longitude"],
                peakpower=config_entry["peakpower"],
                angle=config_entry["angle"],
                aspect=config_entry["aspect"],
                loss=config_entry["loss"],
            )
            config_list.append(e)
        configurations.append(configuration_model.Configuration(configuration=config_list))
        cnt += 1
    return (model_filenames, configurations)
    

if __name__ == '__main__':    
    scenario_file = "scenarios/1_consumer/config.json"
    (model_filenames, configurations) = get_configurations(scenario_file)
    data = create_model(configurations)
    
    # Save dictionaries as binary models
    for i in range(len(data)):
        with open(f"models/{model_filenames[i]}", "wb") as f:
            pickle.dump(data[i], f)