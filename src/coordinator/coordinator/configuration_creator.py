import pandas as pd
import json
import uuid
import os
from datetime import date

"""
This script is designed to generate a configuration JSON file that defines a scenario for a network including consumers, 
generators, storages, network entities, buses and lines.

Usage (see main function at the bottom of this file):
1.  Provide a location specifying a latitude and longitude. The default values for the location are Hagenberg im Mühlkreis, Austria.
    Also choose a consumer- and generator model and create an instance of the DataFrameCreator class to generate DataFrames for 
    grid connections, households, generators and storages. 
    You can specify the number of consumers, generators, storages, grid connections and other parameters in the main function as well.
2.  Create an instance of ConfigurationCreator by providing the DataFrames created in step 1.
3.  Call the generate_config method to generate the JSON configuration for the scenario.
4.  The JSON configuration is saved to a file named "config.json" in the "scenarios" folder.

"""

class ConfigurationCreator:
    def __init__(self, metadata, df_grid_connection, df_household, df_generation, df_producer, df_storage, profile_id_consumer, profile_id_generator):
        self.metadata = metadata
        self.df_grid = df_grid_connection
        self.df_hh = df_household
        self.df_gen = df_generation
        self.df_prod = df_producer
        self.df_stor = df_storage
        self.profile_id_con = profile_id_consumer
        self.profile_id_gen = profile_id_generator

    def __get_json(self):
        # set architecture of json
        return {
            "Scenario": {
                "Name": self.metadata["name"],
                "Description": self.metadata["description"],
                "Version": self.metadata["version"],
                "Consumers": [],
                "Generators": [],
                "Producer": [],
                "Storages": [],
                "Network": {
                    "Buses": [],
                    "Entities": [],
                    "Lines": []
                }
            }
        }

    def __set_attr_households(self):
        return {
            "Level": 7,
            "Type": "load",
            "Category": "household",
            "ProfileIdentifier": self.profile_id_con
        }
        
    def __set_attr_generator(self):
        return {
            "Level": 7,
            "Type": "generator",
            "Category": "household",
            "ProfileIdentifier": self.profile_id_gen
        }
        
    def __set_attr_entities(self):
        return {
            "Type": "network",
            "Category": "network",
            "NetworkEntity": "network"
        }
        
    def __set_attr_bus_hh(self):
        return {
            "Voltage": 0.4,
            "Category": "consumer",
            "Type": "load"
        }
        
    def __set_attr_bus_gen(self):
        return {
            "Voltage": 0.4,
            "Category": "generator",
            "Type": "generation"
        }
        
    def __set_attr_bus_stor(self):
        return {
            "Voltage": 0.4,
            "Category": "storage",
            "Type": "storage"
        }
        
    def __set_attr_bus_grid(self):
        return {
            "Voltage": 0.4,
            "Category": "grid_connection",
            "Type": "grid_connection"
        }
        
    def __set_attr_lines(self):
        return {
            "StdType": "NAYY 4x50 SE",
            "LengthKm": 0.1
        }
    

    def generate_config(self):
        json_str = self.__get_json()
        
        # households:
        # convert each household entry to a dict
        hh_dict = pd.DataFrame.to_dict(self.df_hh, orient='records')
        # fill json with values
        json_str["Scenario"]["Consumers"] = hh_dict
        
        # generator:
        gen_dict = pd.DataFrame.to_dict(self.df_gen, orient='records')
        json_str["Scenario"]["Generators"] = gen_dict
        
        # producer:
        prod_dict = pd.DataFrame.to_dict(self.df_prod, orient='records')
        json_str["Scenario"]["Producer"] = prod_dict
        
        # storages:
        stor_dict = pd.DataFrame.to_dict(self.df_stor, orient='records')
        json_str["Scenario"]["Storages"] = stor_dict
        
        # grid connections - entities:
        ent_dict = pd.DataFrame.to_dict(self.df_grid, orient='records')
        json_str["Scenario"]["Network"]["Entities"] = ent_dict
        
        # get ids
        id_hh = self.df_hh.Identifier.tolist()
        id_grid = self.df_grid.Identifier.tolist()
        id_gen = self.df_gen.Identifier.tolist()
        id_stor = self.df_stor.Identifier.tolist()
        # add buses
        buses = self.__get_buses(id_hh, id_grid, id_gen, id_stor)
        # append to json string
        json_str["Scenario"]["Network"]["Buses"] = buses
            
        # add lines
        lines = self.__get_lines(id_grid + id_hh + id_gen + id_stor)
        # append list to json string
        json_str["Scenario"]["Network"]["Lines"] = lines
        return json_str
        
    def __get_buses(self, id_hh, id_grid, id_gen, id_stor):
        buses = []
        # household bus
        for value in id_hh:
            bus_dict = { "Identifier": value }
            bus_dict.update(self.__set_attr_bus_hh())
            buses.append(bus_dict)
        # grid connection bus
        for value in id_grid:
            grid_dict = { "Identifier": value }
            grid_dict.update(self.__set_attr_bus_grid())
            buses.append(grid_dict)
        # generator bus
        for value in id_gen:
            gen_dict = { "Identifier": value }
            gen_dict.update(self.__set_attr_bus_gen())
            buses.append(gen_dict)
        # storage bus
        for value in id_stor:
            stor_dict = { "Identifier": value}
            stor_dict.update(self.__set_attr_bus_stor())
            buses.append(stor_dict)
        return buses

    def __get_lines(self, all_ids):
        lines = []
        # create dicts with "from_bus", "to_bus" and set_attr_lines
        for i in range(len(all_ids)-1):
            line_dict = { "FromBus": all_ids[i], "ToBus": all_ids[i+1] }
            # merge dict with set attributes
            line_dict.update(self.__set_attr_lines())
            # append dict to list
            lines.append(line_dict)
        return lines
    
class DataFrameCreator:
    def __init__(self, num_consumer, num_generators, num_storages, num_grid_connections, generator_model, consumer_model, regression_model, lat=48.3787, lon=14.5173):
        self.num_consumer = num_consumer
        self.num_generators = num_generators
        self.num_storages = num_storages
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
        df_grid_connection["Address"] = address
        df_grid_connection["Category"] = category
        df_grid_connection["Identifier"] = identifier
        df_grid_connection["Latitude"] = latitude
        df_grid_connection["Longitude"] = longitude
        df_grid_connection["Name"] = name
        df_grid_connection["NetworkEntity"] = network_entity
        df_grid_connection["Type"] = types
        
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
        in_service = []
        
        # save original latitude
        orig_lat = self.lat
        # set divisor to get settlement of houses if amount of households is bigger than 3
        divisor = None
        if self.num_consumer > 3:
            # set highest possible divisor to get amount of house rows
            for x in range(2, self.num_consumer):
                if self.num_consumer % x == 0:
                    divisor = x

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
            in_service.append(True)
            # increment lat but not lon to create settlement
            if divisor is not None:
                self.lat += 0.0002
                if c % divisor == 0:
                    # increment longitude and reset latitude
                    self.lon += 0.0002
                    self.lat = orig_lat
            else:
                self.lat += 0.0002
                self.lon += 0.0002
            self.address_number += 1
            
        # create dataframe
        df_consumer["Address"] = address
        df_consumer["Category"] = category
        df_consumer["Identifier"] = identifier
        df_consumer["Latitude"] = latitude
        df_consumer["Level"] = level
        df_consumer["Longitude"] = longitude
        df_consumer["Name"] = name
        df_consumer["ProfileIdentifier"] = profile_identifier
        df_consumer["Type"] = types
        df_consumer["InService"] = in_service
        
        return df_consumer
    

    def create_df_generator(self, producer_ids):
        df_generator = pd.DataFrame()
        name = []
        identifier = []
        producer_identifier = []
        latitude = []
        longitude = []
        address = []
        level = []
        types = []
        category = []
        profile_identifier = []
        in_service = []

        for c in range(1, self.num_generators+1):
            name.append("photovoltaic " + str(c))
            identifier.append(str(uuid.uuid4()))
            producer_identifier.append(producer_ids[c-1])
            latitude.append(round(self.lat, 4))
            longitude.append(round(self.lon, 4))
            address.append("Risc Strasse " + str(self.address_number))
            level.append(7)
            types.append("generator")
            category.append("household")
            profile_identifier.append(generator_model)
            in_service.append(True)
            # increment lat and lon
            self.lat += 0.0002
            self.lon += 0.0002
            self.address_number += 1
            
        # create dataframe
        df_generator["Name"] = name
        df_generator["Identifier"] = identifier
        df_generator["ProducerIdentifier"] = producer_identifier
        df_generator["Latitude"] = latitude
        df_generator["Longitude"] = longitude
        df_generator["Address"] = address
        df_generator["Level"] = level
        df_generator["Type"] = types
        df_generator["Category"] = category
        df_generator["ProfileIdentifier"] = profile_identifier
        df_generator["InService"] = in_service
        
        return df_generator


    def create_df_producer(self):
        df_producer = pd.DataFrame()
        identifier = []
        name = []
        model_identifier = []
        configuration_entries = []
        
        for c in range(self.num_generators):
            name.append("producer " + str(c+1))
            identifier.append(str(uuid.uuid4()))
            model_identifier.append(regression_model)
            configuration_entries.append(self.get_configuration_entry(self.lat, self.lon))
            
        df_producer["Identifier"] = identifier
        df_producer["Name"] = name
        df_producer["ModelIdentifier"] = model_identifier
        df_producer["ConfigurationEntries"] = configuration_entries
        
        return df_producer


    def create_df_storage(self):
        df_storage = pd.DataFrame()
        name = []
        identifier = []
        latitude = []
        longitude = []
        address = []
        level = []
        types = []
        category = []
        in_service = []
        minimum_capacity = []
        maximum_capacity = []
        capacity_unit = []
        minimum_active_power = []
        maximum_active_power = []
        minimum_reactive_power = []
        maximum_reactive_power = []
        current_active_power = []
        state_of_charge = []
        
        for c in range(1, self.num_storages+1):
            name.append("Storage " + str(c))
            identifier.append(str(uuid.uuid4()))
            latitude.append(round(self.lat, 4))
            longitude.append(round(self.lon, 4))
            address.append("none")
            level.append(7)
            types.append("storage")
            category.append("household")
            in_service.append(True)
            minimum_capacity.append(0)
            maximum_capacity.append(0.01)
            capacity_unit.append("MWh")
            minimum_active_power.append(0)
            maximum_active_power.append(1)
            minimum_reactive_power.append(0)
            maximum_reactive_power.append(1)
            current_active_power.append(0)
            state_of_charge.append(0)            
            # increment lat
            self.lat += 0.0002
            self.lon += 0.0002   
        
        # create dataframe
        df_storage["Name"] = name
        df_storage["Identifier"] = identifier
        df_storage["Latitude"] = latitude
        df_storage["Longitude"] = longitude
        df_storage["Address"] = address
        df_storage["Level"] = level
        df_storage["Type"] = types
        df_storage["Category"] = category
        df_storage["InService"] = in_service
        df_storage["MinimumCapacity"] = minimum_capacity
        df_storage["MaximumCapacity"] = maximum_capacity
        df_storage["CapacityUnit"] = capacity_unit
        df_storage["MinimumActivePower"] = minimum_active_power
        df_storage["MaximumActivePower"] = maximum_active_power
        df_storage["MinimumReactivePower"] = minimum_reactive_power
        df_storage["MaximumReactivePower"] = maximum_reactive_power
        df_storage["CurrentActivePower"] = current_active_power
        df_storage["StateOfCharge"] = state_of_charge
        
        return df_storage
                
    def get_configuration_entry(self, lat, lon):
        return {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "peakpower": 10,
            "angle": 22,
            "aspect": 0,
            "loss": 14
        }
    

if __name__ == "__main__":
    # set models and variables
    generator_model = "hgb_south_10kwp"
    consumer_model = "two_person_all_working_no_heat"
    regression_model = "bad_zell_all_aspects.onnx"
    consumer = 10
    generators = 1
    storages = 1
    grid_conns = 1
    
    # create DataFrames
    # if you want to choose another city, add parameters latitude and longitude, default is Hagenberg
    c = DataFrameCreator(consumer, generators, storages, grid_conns, generator_model, consumer_model, regression_model)    
    df_grid = c.create_df_grid_connection()
    df_hh = c.create_df_household()
    df_prod = c.create_df_producer()
    df_gen = c.create_df_generator(df_prod["Identifier"].tolist())
    df_stor = c.create_df_storage()
    
    # set metadata for scenario
    metadata = {
        "name": f"{consumer} Consumer, {generators} Generator, rural",
        "description": "simple test network",
        "version": f"{date.today()}-V1"
    }
    
    # create configuration file
    config_creator = ConfigurationCreator(metadata=metadata, df_grid_connection=df_grid, df_household=df_hh, df_generation=df_gen, df_producer=df_prod, df_storage=df_stor, profile_id_consumer=consumer_model, profile_id_generator=generator_model)
    json_str = config_creator.generate_config()
    # save json config
    json_obj = json.dumps(json_str, indent=4)
    if not os.path.exists(f"scenarios/{consumer}_consumer"):
        os.makedirs(f"scenarios/{consumer}")
    with open(f"scenarios/{consumer}_consumer/config.json", "w") as of:
        of.write(json_obj)