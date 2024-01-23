import dill as pickle
from pathlib import Path
import pandas as pd
import sys
import datetime
from consumption_model import RandomConsumption, DataframeTemplateDayConsumption, DataframeTemplateYearConsumption

""" 
This script creates consumer models on the basis of consumer data.
It expects an input file path of a pickled dataframe and the name for the new model.
It saves the generated model file according to the given input.

The input file must have the following format:

pandas.DataFrame:

        LCLid	    Hour	kwh
0	    MAC000002	0	    0.174222
1	    MAC000004	0	    0.020111
2	    MAC000006	0	    0.052778
3	    MAC000007	0	    0.199056
4	    MAC000009	0	    0.102556
...	    ...	        ...	    ...
70243	MAC005558	23	    0.011222
70244	MAC005561	23	    0.081333
70245	MAC005562	23	    0.261778
70246	MAC005566	23	    0.108000
70247	MAC005567	23	    0.092444

CLI:
The script call requests 3 arguments:
    1. the name of the script itself ("create_model.py")
    2. the path of the input pickle-file
    3. the name for the new model

Sample call CLI:
python create_model.py C:\Projects\SPA_Energie_UseCase\LondonHouseholds\Cluster_dataframes_hourly_only_holidays\n_5\cluster_0_per_hour_n=5_cluster_size=2274.pkl london2011-2014_only_holidays_cluster0
"""

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
        
    # model_name = "london2011-2014_only_holidays_cluster0"
    # input_file_name = "data/cluster_0_per_hour_n=5.pkl"
    
    # with cli
    input_file_name = sys.argv[1]
    model_name = sys.argv[2]
    with open(input_file_name, "rb") as inf:
        # load consumer data
        df = pickle.load(inf)

    # create consumption model
    consumption = DataframeTemplateDayConsumption(model_name, df)
    print(consumption.get_consumption(1))    
    
    with open(model_output_path / model_name, "wb") as of:
        # save model
        pickle.dump(consumption, of)
    
    with open(model_output_path / model_name, "rb") as inf:
        # test if succeeded
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
