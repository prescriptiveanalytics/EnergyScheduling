import pandas as pd
import json
import uuid
import os

"""
This script is designed to generate a configuration JSON file that defines a scenario for a consumer-generator network, 
including consumers, generators, network entities, buses and lines.

Usage (see main function at the bottom of this file):
1.  Provide a location specifying a latitude and longitude. The default values for the location are Hagenberg im Mühlkreis, Austria.
    Also choose a consumer- and generator model and create instances of DataFrameCreator to generate DataFrames for grid connections, 
    households and generators. You can specify the number of consumers, generators, grid connections and other parameters in the main 
    function as well.
2.  Create an instance of ConfigurationCreator by providing the DataFrames created in step 1.
3.  Call the generate_config method to generate the JSON configuration for the scenario.
4.  The JSON configuration is saved to a file named "config.json" in the "scenarios" folder.

"""

class ConfigurationCreator:
    def __init__(self, df_grid_connection, df_household, df_generation):
        self.df_grid = df_grid_connection
        self.df_hh = df_household
        self.df_gen = df_generation

    def __get_json(self):
        # set architecture of json
        return {
            "scenario": {
                "consumers": [],
                "generators": [],
                "networks": {
                    "entities": [],
                    "bus": [],
                    "lines": []
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
            "profile_identifier": "Hagenberg_peakpower10_angle22_aspect0"   # TODO: model in main setzen und übergeben!!!
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
        # convert each household entry to a dict
        hh_dict = pd.DataFrame.to_dict(self.df_hh, orient='records')
        # if attributes are not set
        if len(self.df_hh.columns) < 9:
            # merge each dict with set attributes
            for dict in hh_dict:
                dict.update(self.__set_attr_households())
        # fill json with values
        json_str["scenario"]["consumers"] = hh_dict
        
        # generator:
        # convert each entry to a dict
        gen_dict = pd.DataFrame.to_dict(self.df_gen, orient='records')
        # if attributes are not set
        if len(self.df_gen.columns) < 9:
            # merge each dict with set_attr
            for dict in gen_dict:
                dict.update(self.__set_attr_generator())
        # append values to json
        json_str["scenario"]["generators"] = gen_dict
        
        # grid connections - entities:
        # convert each entry to a dict
        ent_dict = pd.DataFrame.to_dict(self.df_grid, orient='records')
        if len(self.df_grid.columns) < 8:
            # merge dict with set_attr
            for dict in ent_dict:
                dict.update(self.__set_attr_entities())
        # append values to json
        json_str["scenario"]["networks"]["entities"] = ent_dict
        
        # get ids
        id_hh = self.df_hh.identifier.tolist()
        id_grid = self.df_grid.identifier.tolist()
        id_gen = self.df_gen.identifier.tolist()
        # add buses
        buses = self.__get_buses(id_hh, id_grid, id_gen)
        # append to json string
        json_str["scenario"]["networks"]["bus"] = buses
            
        # add lines
        lines = self.__get_lines(id_grid + id_hh + id_gen)
        # append list to json string
        json_str["scenario"]["networks"]["lines"] = lines
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
    
class DataFrameCreator:
    def __init__(self, num_consumer, num_generators, num_grid_connections, generator_model, consumer_model, lat=48.3787, lon=14.5173):
        self.num_consumer = num_consumer
        self.num_generators = num_generators
        self.num_grid_connections = num_grid_connections
        self.address_number = 0
        self.lat = lat
        self.lon = lon
        
    def to_csv(self, filename, data):
        with open(file=filename, mode="w") as outfile:
            outfile.write(data)
        
    def create_df_grid_connection(self):
        df_grid_connection = pd.DataFrame()
        name = []
        identifier = []
        latitude = []
        longitude = []
        address = []
        types = []
        category = []
        network_entity = []

        for c in range(1, self.num_grid_connections+1):
            name.append("grid connection " + str(c))
            identifier.append(str(uuid.uuid4()))
            latitude.append(round(self.lat, 4))
            longitude.append(round(self.lon, 4))
            address.append("Risc Strasse " + str(self.address_number))
            types.append("network")
            category.append("network")
            network_entity.append("network")
            # increment location and address 
            self.lat += 0.0002
            self.lon += 0.0002
            self.address_number += 1
            
        # create dataframe
        df_grid_connection["name"] = name
        df_grid_connection["identifier"] = identifier
        df_grid_connection["latitude"] = latitude
        df_grid_connection["longitude"] = longitude
        df_grid_connection["address"] = address
        df_grid_connection["type"] = types
        df_grid_connection["category"] = category
        df_grid_connection["network_entity"] = network_entity
        
        return df_grid_connection
    
    
    def create_df_household(self):
        df_consumer = pd.DataFrame()
        name = []
        identifier = []
        latitude = []
        longitude = []
        address = []
        level = []
        types = []
        category = []
        profile_identifier = []

        for c in range(1, self.num_consumer+1):
            name.append("Household " + str(c))
            identifier.append(str(uuid.uuid4()))
            latitude.append(round(self.lat, 4))
            longitude.append(round(self.lon, 4))
            address.append("Risc Strasse " + str(self.address_number))
            level.append(7)
            types.append("load")
            category.append("household")
            profile_identifier.append(consumer_model)
            # increment lat and lon
            self.lat += 0.0002
            self.lon += 0.0002
            self.address_number += 1
            
        # create dataframe
        df_consumer["name"] = name
        df_consumer["identifier"] = identifier
        df_consumer["latitude"] = latitude
        df_consumer["longitude"] = longitude
        df_consumer["address"] = address
        df_consumer["level"] = level
        df_consumer["type"] = types
        df_consumer["category"] = category
        df_consumer["profile_identifier"] = profile_identifier
        
        return df_consumer
    

    def create_df_generator(self):
        df_generator = pd.DataFrame()
        name = []
        identifier = []
        latitude = []
        longitude = []
        address = []
        level = []
        types = []
        category = []
        profile_identifier = []

        for c in range(1, self.num_generators+1):
            name.append("photovoltaic " + str(c))
            identifier.append(str(uuid.uuid4()))
            latitude.append(round(self.lat, 4))
            longitude.append(round(self.lon, 4))
            address.append("Risc Strasse " + str(self.address_number))
            level.append(7)
            types.append("generator")
            category.append("household")
            profile_identifier.append(generator_model)
            # increment lat and lon
            self.lat += 0.0002
            self.lon += 0.0002
            self.address_number += 1
            
        # create dataframe
        df_generator["name"] = name
        df_generator["identifier"] = identifier
        df_generator["latitude"] = latitude
        df_generator["longitude"] = longitude
        df_generator["address"] = address
        df_generator["level"] = level
        df_generator["type"] = types
        df_generator["category"] = category
        df_generator["profile_identifier"] = profile_identifier
        
        return df_generator


if __name__ == "__main__":
    # set models and variables
    generator_model = "hgb_south_10kwp"
    consumer_model = "london2011-2014_cluster0"
    consumer = 500
    generators = 1
    grid_conns = 1
    
    # create csv data and save to given paths
    # if you want to choose another city, add parameters latitude and longitude
    c = DataFrameCreator(consumer, generators, grid_conns, generator_model, consumer_model)    
    df_grid = c.create_df_grid_connection()
    df_hh = c.create_df_household()
    df_gen = c.create_df_generator()
    
    # create configuration file
    config_creator = ConfigurationCreator(df_grid_connection=df_grid, df_household=df_hh, df_generation=df_gen)
    json_str = config_creator.generate_config()
    # save json config
    json_obj = json.dumps(json_str, indent=4)
    if not os.path.exists(f"scenarios/{consumer}_consumer"):
        os.makedirs(f"scenarios/{consumer}_consumer")
    with open(f"scenarios/{consumer}_consumer/config.json", "w") as of:
        of.write(json_obj)