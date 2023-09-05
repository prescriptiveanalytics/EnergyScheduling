import dill as pickle
from pathlib import Path
import pandas as pd
import datetime
from consumption_model import RandomConsumption, DataframeTemplateDayConsumption, DataframeTemplateYearConsumption

model_output_path = Path("consumption_models")

if __name__ == '__main__':
    # name = "ex1_random_100Wh_to_3000Wh"
    # consumption = RandomConsumption(name)

    # print(consumption.get_consumption(1))
    
    # with open(model_output_path / name, "wb") as of:
    #     pickle.dump(consumption, of)

    # with open(model_output_path / name, "rb") as inf:
    #     test = pickle.load(inf)
    #     print(test.get_consumption(1))
    
    name = "ex1_london2011-2014_cluster0"
    input_file_name = "data/cluster_0_per_hour_n=5.pkl"
    with open(input_file_name, "rb") as inf:
        df = pickle.load(inf)

    consumption = DataframeTemplateDayConsumption(name, df)
    print(consumption.get_consumption(1))    
    
    with open(model_output_path / name, "wb") as of:
        pickle.dump(consumption, of)
    
    with open(model_output_path / name, "rb") as inf:
        test = pickle.load(inf)
        print(test.get_consumption(1))
    
    # name = "ex0_two_person_all_working_no_heat"
    # input_file_name = "data/AT0031000000000000000000990062453_QH_20220101_20221231.csv"
    # df = pd.read_csv(input_file_name, sep=";", decimal=",")
    # df = df[['Datum von', 'Energiemenge in kWh']]

    # df = df.rename(columns={"Datum von": "date", "Energiemenge in kWh": "kwh"}, errors="raise")
    # df['date'] = pd.to_datetime(df['date'], format="%d.%m.%Y %H:%M")
    # df['month'] = df['date'].dt.month
    # df['day'] = df['date'].dt.day
    # df['hour'] = df['date'].dt.hour
    # df['minute'] = df['date'].dt.minute
    # print(df)
    # consumption = DataframeTemplateYearConsumption(name, df)

    # with open(model_output_path / name, "wb") as of:
    #     pickle.dump(consumption, of)
