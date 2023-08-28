import json
import dill as pickle
from pathlib import Path
from generator_model import PVGisGenerator
import pandas as pd
from pandas import json_normalize
import logging

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

model_output_path = Path("generator_models")

data_input_file = Path("data/lat-48.37_lon-14.513_peakpower-1_loss-14_angle-30_aspect-0_outputformat-json_mountingplace-building_startyear-2005_endyear-2020_usehorizon-1_pvcalculation-1.json")

orientations_amount = [
    [ 'hgb_south_10kwp', (-90, 0), (0, 10), (90, 0) ],
    [ 'hgb_east_10kwp', (-90, 10), (0, 0), (90, 0) ],
    [ 'hgb_west_10kwp', (-90, 0), (0, 0), (90, 10) ],
    [ 'hgb_south_5kwp_east_5kwp', (-90, 5), (0, 5), (90, 0) ],
    [ 'hgb_south_5kwp_west_5kwp', (-90, 0), (0, 5), (90, 5) ],
    [ 'hgb_south_7kwp_east_1.5kwp_west1.5kwp', (-90, 1.5), (0, 7), (90, 1.5) ]
]

def generate_model(configuration):
    name = configuration[0]
    dataframes = []
    for aspect, kwp in configuration[1:]:
        if kwp == 0: continue
        input_path = Path(f"data/lat-48.37_lon-14.513_peakpower-1_loss-14_angle-30_aspect-{aspect}_outputformat-json_mountingplace-building_startyear-2005_endyear-2020_usehorizon-1_pvcalculation-1.json")
        logging.debug(f"aspect={aspect}, kwp={kwp}, path={input_path}")
        with open(input_path, 'r') as inf:
            data_json = json.load(inf)
        
        df = json_normalize(data_json['outputs']['hourly'])
        df['time'] = pd.to_datetime(df['time'], format="%Y%m%d:%H%M")
        power = data_json['inputs']['pv_module']['peak_power']

        dfi = df.set_index('time')
        dfr = dfi.resample("15min").bfill()
        dfr = dfr.resample("15min").ffill()
        dfr = dfr.reset_index()
        dfr['P_eff'] = dfr['P'] * ((kwp / float(power)) / 4)
        dfr['aspect'] = aspect
        dataframes.append(dfr)

    all_df = pd.concat(dataframes)
    all_df = all_df.reset_index()
    all_df['hour'] = all_df['time'].dt.hour
    all_df['minute'] = all_df['time'].dt.minute
    all_df['day'] = all_df['time'].dt.day
    all_df['month'] = all_df['time'].dt.month
    #print(all_df.head())
    all_df = all_df[['P', 'G(i)', 'H_sun', 'T2m', 'WS10m', 'Int', 'hour', 'minute', 'day', 'month', 'aspect', 'P_eff']]
    all_df = all_df.groupby(by=['hour', 'minute', 'day', 'month', 'aspect']).max()
    #print(all_df.head())
    all_df = all_df.groupby(by=['hour', 'minute', 'day', 'month']).sum()
    all_df = all_df.reset_index()
    data_p_eff = {}
    data = {}
    for index, row in all_df.iterrows():
        data_p_eff[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['P_eff']
        data[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['P']

    generator = PVGisGenerator(name, data_p_eff)
    
    with open(model_output_path / name, "wb") as of:
        pickle.dump(generator, of)
    

kwp: float = 1

if __name__ == '__main__':

    for c in orientations_amount:
        generate_model(c)

    exit(0)

    name = "ex1_pvgis_10kwp_south_hgb"

    with open(data_input_file, "r") as inf:
        data_json = json.load(inf)

    df = json_normalize(data_json['outputs']['hourly'])
    df['time'] = pd.to_datetime(df['time'], format="%Y%m%d:%H%M")
    power = data_json['inputs']['pv_module']['peak_power']

    dfi = df.set_index('time')
    dfr = dfi.resample("15min").bfill()
    dfr = dfr.resample("15min").ffill()
    dfr = dfr.reset_index()
    dfr['hour'] = dfr['time'].dt.hour
    dfr['minute'] = dfr['time'].dt.minute
    dfr['day'] = dfr['time'].dt.day
    dfr['month'] = dfr['time'].dt.month
    dfr = dfr[['P', 'G(i)', 'H_sun', 'T2m', 'WS10m', 'Int', 'hour', 'minute', 'day', 'month']]
    dfr = dfr.groupby(by=['hour', 'minute', 'day', 'month']).mean()
    dfr = dfr.reset_index()
    dfr['P_eff'] = dfr['P'] * ((kwp / float(power)) / 4)

    data_p_eff = {}
    data = {}
    for index, row in dfr.iterrows():
        data_p_eff[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['P_eff']
        data[(int(row['month']), int(row['day']), int(row['hour']), int(row['minute']))] = row['P']

    generator = PVGisGenerator(name, data_p_eff)
    
    with open(model_output_path / name, "wb") as of:
        pickle.dump(generator, of)
    
    with open(model_output_path / name, "rb") as inf:
        test = pickle.load(inf)
        print(test.get_generation(1))