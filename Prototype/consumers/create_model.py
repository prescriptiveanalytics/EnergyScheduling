import dill as pickle
from pathlib import Path
from consumption_model import RandomConsumption, DataframeConsumption

model_output_path = Path("consumption_models")

if __name__ == '__main__':
    name = "ex1_random_100Wh_to_3000Wh"
    consumption = RandomConsumption(name)

    print(consumption.get_consumption(1))
    
    with open(model_output_path / name, "wb") as of:
        pickle.dump(consumption, of)

    with open(model_output_path / name, "rb") as inf:
        test = pickle.load(inf)
        print(test.get_consumption(1))
    
    name = "ex1_london2011-2014_cluster0"
    input_file_name = "data/cluster_0_per_hour_n=5.pkl"
    with open(input_file_name, "rb") as inf:
        df = pickle.load(inf)

    consumption = DataframeConsumption(name, df)
    print(consumption.get_consumption(1))    
    
    with open(model_output_path / name, "wb") as of:
        pickle.dump(consumption, of)
    
    with open(model_output_path / name, "rb") as inf:
        test = pickle.load(inf)
        print(test.get_consumption(1))