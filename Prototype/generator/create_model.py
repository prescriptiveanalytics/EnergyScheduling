import json
import dill as pickle
from pathlib import Path
from generator_model import PVGisGenerator
import pandas as pd
from pandas import json_normalize

model_output_path = Path("generator_models")

data_input_file = Path("data/lat-48.37_lon-14.513_peakpower-1_loss-14_angle-0_aspect--30_outputformat-json_mountingplace-building_startyear-2005_endyear-2020_usehorizon-1_pvcalculation-1.json")

kwp: float = 1

if __name__ == '__main__':
    name = "ex1_pvgis_10kwp_hgb"

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
    dfr['P_eff'] = dfr['P'] * (kwp / float(power))

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