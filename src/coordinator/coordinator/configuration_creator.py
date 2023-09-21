import pandas as pd
import json
from csv_data_creator import CsvDataCreator

class ConfigurationCreator:
    def __init__(self, path_grid_connection, path_household, path_generation):
        self.path_grid_connection = path_grid_connection
        self.path_household = path_household
        self.path_generation = path_generation
        

    def __get_json(self):
        # set architecture of json
        return {
            "scenario": {
                "consumer": {
                    "consumers": []
                },
                "generator": {
                    "generators": []
                },
                "network": {
                    "network": {
                        "entities": [],
                        "bus": [],
                        "lines": []
                    }
                }
            }
        }

    def __set_attr_households(self):
        return {
            "level": 7,
            "type": "load",
            "category": "household",
            "profile_identifier": "london2011-2014_cluster0"
        }
        
    def __set_attr_generator(self):
        return {
            "level": 7,
            "type": "generator",
            "category": "household",
            "profile_identifier": "pvgis_hgp_south_10kwp"
        }
        
    def __set_attr_entities(self):
        return {
            "type": "network",
            "category": "network",
            "network_entity": "network"
        }
        
    def __set_attr_bus_hh(self):
        return {
            "voltage": 400,
            "category": "consumer",
            "type": "load"
        }
        
    def __set_attr_bus_gen(self):
        return {
            "voltage": 400,
            "category": "generator",
            "type": "generation"
        }
        
    def __set_attr_bus_grid(self):
        return {
            "voltage": 400,
            "category": "grid_connection",
            "type": "grid_connection"
        }
        
    def __set_attr_lines(self):
        return {
            "std_type": "NAYY 4x50 SE",
            "length_km": 0.1
        }


    def generate_config(self):
        json_str = self.__get_json()
        # households:
        df_hh = pd.read_csv(self.path_household, sep=";")
        # convert each household entry to a dict
        hh_dict = pd.DataFrame.to_dict(df_hh, orient='records')
        # if attributes are not set
        if len(df_hh.columns) < 9:
            # merge each dict with set attributes
            for dict in hh_dict:
                dict.update(self.__set_attr_households())
        # fill json with values
        json_str["scenario"]["consumer"]["consumers"] = hh_dict
        
        # generator:
        df_gen = pd.read_csv(self.path_generation, sep=";")
        # convert each entry to a dict
        gen_dict = pd.DataFrame.to_dict(df_gen, orient='records')
        # if attributes are not set
        if len(df_gen.columns) < 9:
            # merge each dict with set_attr
            for dict in gen_dict:
                dict.update(self.__set_attr_generator())
        # append values to json
        json_str["scenario"]["generator"]["generators"] = gen_dict
        
        # grid connections - entities:
        df_grid = pd.read_csv(self.path_grid_connection, sep=";")
        # convert each entry to a dict
        ent_dict = pd.DataFrame.to_dict(df_grid, orient='records')
        if len(df_grid.columns) < 8:
            # merge dict with set_attr
            for dict in ent_dict:
                dict.update(self.__set_attr_entities())
        # append values to json
        json_str["scenario"]["network"]["network"]["entities"] = ent_dict
        
        # get ids
        id_hh = df_hh.identifier.tolist()
        id_grid = df_grid.identifier.tolist()
        id_gen = df_gen.identifier.tolist()
        # add buses
        buses = self.__get_buses(id_hh, id_grid, id_gen)
        # append to json string
        json_str["scenario"]["network"]["network"]["bus"] = buses
            
        # add lines
        lines = self.__get_lines(id_grid + id_hh + id_gen)
        # append list to json string
        json_str["scenario"]["network"]["network"]["lines"] = lines
        return json_str
        
        
    def __get_buses(self, id_hh, id_grid, id_gen):
        buses = []
        # households
        for value in id_hh:
            bus_dict = { "identifier": value }
            bus_dict.update(self.__set_attr_bus_hh())
            buses.append(bus_dict)
        # grid connection bus
        for value in id_grid:
            grid_dict = { "identifier": value }
            grid_dict.update(self.__set_attr_bus_grid())
            buses.append(grid_dict)
        # generator bus
        for value in id_gen:
            gen_dict = { "identifier": value }
            gen_dict.update(self.__set_attr_bus_gen())
            buses.append(gen_dict)
        return buses


    def __get_lines(self, all_ids):
        lines = []
        # create dicts with "from_bus", "to_bus" and set_attr_lines
        for i in range(len(all_ids)-1):
            line_dict = { "from_bus": all_ids[i], "to_bus": all_ids[i+1] }
            # merge dict with set attributes
            line_dict.update(self.__set_attr_lines())
            # append dict to list
            lines.append(line_dict)
        return lines

 
if __name__ == "__main__":
    # set paths and variables
    # path_grid_conn = "./energy_data/grid_connections.csv"
    # path_household = "./energy_data/households.csv"
    # path_generation = "./energy_data/generators.csv"
    path_grid_conn = "./grid_connections.csv"
    path_household = "./households.csv"
    path_generation = "./generators.csv"
    consumer = 15
    generators = 1
    grid_conns = 1
    
    # create csv data and save to given paths
    c = CsvDataCreator(num_consumer=consumer, num_generators=generators, num_grid_connections=grid_conns)    
    c.create_df_grid_connection(path_grid_conn)
    c.create_df_household(path_household)
    c.create_df_generator(path_generation)
    
    # create configuration file
    config_creator = ConfigurationCreator(path_grid_connection=path_grid_conn, path_household=path_household, path_generation=path_generation)
    json_str = config_creator.generate_config()
    # save json config
    json_obj = json.dumps(json_str, indent=4)
    with open("./_config.json", "w") as of:
        of.write(json_obj)