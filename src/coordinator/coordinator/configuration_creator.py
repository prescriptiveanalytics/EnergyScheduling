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
    """
    Class to create a configuration for an energy network scenario.
    """
    
    def __init__(
        self,
        metadata: dict,
        df_grid_connection: pd.DataFrame,
        df_household: pd.DataFrame,
        df_generation: pd.DataFrame,
        df_producer: pd.DataFrame,
        df_storage: pd.DataFrame,
        profile_id_consumer: str,
        profile_id_generator: str
        ):
        self.metadata = metadata
        self.df_grid = df_grid_connection
        self.df_hh = df_household
        self.df_gen = df_generation
        self.df_prod = df_producer
        self.df_stor = df_storage
        self.profile_id_con = profile_id_consumer
        self.profile_id_gen = profile_id_generator


    # Methods to generate JSON configuration
    
    def __get_json(self) -> dict:
        # Set architecture of json
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

    def __set_attr_bus_hh(self) -> dict:
        return {
            "Voltage": 0.4,
            "Category": "consumer",
            "Type": "load"
        }
        
    def __set_attr_bus_gen(self) -> dict:
        return {
            "Voltage": 0.4,
            "Category": "generator",
            "Type": "generation"
        }
        
    def __set_attr_bus_stor(self) -> dict:
        return {
            "Voltage": 0.4,
            "Category": "storage",
            "Type": "storage"
        }
        
    def __set_attr_bus_grid(self) -> dict:
        return {
            "Voltage": 0.4,
            "Category": "grid_connection",
            "Type": "grid_connection"
        }
        
    def __set_attr_lines(self) -> dict:
        return {
            "StdType": "NAYY 4x50 SE",
            "LengthKm": 0.1
        }
    

    def generate_config(self) -> dict:
        json_dict = self.__get_json()
        
        # Households:
        hh_dict = pd.DataFrame.to_dict(self.df_hh, orient='records')
        json_dict["Scenario"]["Consumers"] = hh_dict
        
        # Generator:
        gen_dict = pd.DataFrame.to_dict(self.df_gen, orient='records')
        json_dict["Scenario"]["Generators"] = gen_dict
        
        # Producer:
        prod_dict = pd.DataFrame.to_dict(self.df_prod, orient='records')
        json_dict["Scenario"]["Producer"] = prod_dict
        
        # Storages:
        stor_dict = pd.DataFrame.to_dict(self.df_stor, orient='records')
        json_dict["Scenario"]["Storages"] = stor_dict
        
        # Grid connections:
        ent_dict = pd.DataFrame.to_dict(self.df_grid, orient='records')
        json_dict["Scenario"]["Network"]["Entities"] = ent_dict
        
        # Get ids
        id_hh = self.df_hh.Identifier.tolist()
        id_grid = self.df_grid.Identifier.tolist()
        id_gen = self.df_gen.Identifier.tolist()
        id_stor = self.df_stor.Identifier.tolist()
        # Add buses
        buses = self.__get_buses(id_hh, id_grid, id_gen, id_stor)
        # Append to json string
        json_dict["Scenario"]["Network"]["Buses"] = buses
            
        # Add lines
        lines = self.__get_lines(id_grid + id_hh + id_gen + id_stor)
        # Append list to json string
        json_dict["Scenario"]["Network"]["Lines"] = lines
        
        return json_dict
        
        
    def __get_buses(self, id_hh: list, id_grid: list, id_gen: list, id_stor: list) -> list:
        buses = []
        # Household bus
        for value in id_hh:
            bus_dict = { "Identifier": value }
            bus_dict.update(self.__set_attr_bus_hh())
            buses.append(bus_dict)
        # Grid connection bus
        for value in id_grid:
            grid_dict = { "Identifier": value }
            grid_dict.update(self.__set_attr_bus_grid())
            buses.append(grid_dict)
        # Generator bus
        for value in id_gen:
            gen_dict = { "Identifier": value }
            gen_dict.update(self.__set_attr_bus_gen())
            buses.append(gen_dict)
        # Storage bus
        for value in id_stor:
            stor_dict = { "Identifier": value}
            stor_dict.update(self.__set_attr_bus_stor())
            buses.append(stor_dict)
        return buses

    def __get_lines(self, all_ids: list) -> list:
        lines = []
        # Create dicts with "from_bus", "to_bus" and its attributes
        for i in range(len(all_ids)-1):
            line_dict = { "FromBus": all_ids[i], "ToBus": all_ids[i+1] }
            # Merge dict with set attributes
            line_dict.update(self.__set_attr_lines())
            # Append dict to list
            lines.append(line_dict)
        return lines
    

class DataFrameCreator:
    """
    Class to create DataFrames for various components of the scenario.
    """
    
    def __init__(
        self,
        num_consumer: int,
        num_generators: int,
        num_storages: int,
        num_grid_connections: int,
        generator_model: str,
        consumer_model: str,
        producer_model: str,
        configs: dict,
        lat: float = 48.3787,
        lon: float = 14.5173
        ):
        self.num_consumer = num_consumer
        self.num_generators = num_generators
        self.num_storages = num_storages
        self.num_grid_connections = num_grid_connections
        self.generator_model = generator_model
        self.consumer_model = consumer_model
        self.producer_model = producer_model
        self.address_number = 0
        self.configs = configs
        self.lat = lat
        self.lon = lon        
        self.df_generator = None
        
        
    def create_df_grid_connection(self) -> pd.DataFrame:
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
            # Increment location and address 
            self.lat += 0.0002
            self.lon += 0.0002
            self.address_number += 1
            
        # Create dataframe
        df_grid_connection["Address"] = address
        df_grid_connection["Category"] = category
        df_grid_connection["Identifier"] = identifier
        df_grid_connection["Latitude"] = latitude
        df_grid_connection["Longitude"] = longitude
        df_grid_connection["Name"] = name
        df_grid_connection["NetworkEntity"] = network_entity
        df_grid_connection["Type"] = types
        
        return df_grid_connection
    
    
    def create_df_household(self) -> pd.DataFrame:
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
        
        # Save original latitude
        orig_lat = self.lat
        # Set divisor to get settlement of houses if amount of households is bigger than 3
        divisor = None
        if self.num_consumer > 3:
            # Set highest possible divisor to get amount of house rows
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
            # Increment lat but not lon to create settlement
            if divisor is not None:
                self.lat += 0.0002
                if c % divisor == 0:
                    # Increment longitude and reset latitude
                    self.lon += 0.0002
                    self.lat = orig_lat
            else:
                self.lat += 0.0002
                self.lon += 0.0002
            self.address_number += 1
            
        # Create dataframe
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
    

    def create_df_generator(self) -> pd.DataFrame:
        self.df_generator = pd.DataFrame()
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

        for c in range(1, self.num_generators+1):
            name.append("photovoltaic " + str(c))
            identifier.append(str(uuid.uuid4()))
            latitude.append(round(self.lat, 4))
            longitude.append(round(self.lon, 4))
            address.append("Risc Strasse " + str(self.address_number))
            level.append(7)
            types.append("generator")
            category.append("household")
            profile_identifier.append(self.generator_model)
            in_service.append(True)
            # Increment lat and lon
            self.lat += 0.0002
            self.lon += 0.0002
            self.address_number += 1
            
        # Create dataframe
        self.df_generator["Name"] = name
        self.df_generator["Identifier"] = identifier
        self.df_generator["Latitude"] = latitude
        self.df_generator["Longitude"] = longitude
        self.df_generator["Address"] = address
        self.df_generator["Level"] = level
        self.df_generator["Type"] = types
        self.df_generator["Category"] = category
        self.df_generator["ProfileIdentifier"] = profile_identifier
        self.df_generator["InService"] = in_service
        
        return self.df_generator


    def create_df_producer(self) -> pd.DataFrame:
        df_producer = pd.DataFrame()
        identifier = []
        name = []
        model_identifier = []
        configuration_entries = []
        
        for c in range(self.num_generators):
            name.append("producer " + str(c+1))
            identifier.append(str(uuid.uuid4()))
            model_identifier.append(self.producer_model)
            configuration_entries.append(self.get_configuration_entry(self.df_generator.iloc[[c]]))
            # Increment lat and lon
            self.lat += 0.0002
            self.lon += 0.0002
        
        # Create dataframe
        df_producer["Identifier"] = identifier
        df_producer["Name"] = name
        df_producer["ModelIdentifier"] = model_identifier
        df_producer["ConfigurationEntries"] = configuration_entries
        # Set identifier in generator
        self.df_generator["ProducerIdentifier"] = identifier
        
        return df_producer


    def create_df_storage(self) -> pd.DataFrame:
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
            # Increment lat and lon
            self.lat += 0.0002
            self.lon += 0.0002   
        
        # Create dataframe
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

   
    def get_configuration_entry(self, df_generator: pd.DataFrame) -> dict:
        config_entries = []
        # Loop through configurations
        for params in self.configs.values():
            config = {
                # Set lat and lon from generators
                "latitude": df_generator.iloc[0]["Latitude"],
                "longitude": df_generator.iloc[0]["Longitude"],
                "peakpower": params["kwp"],
                "angle": params["angle"],
                "aspect": params["aspect"],
                "loss": 14
            }
            config_entries.append(config)
        return config_entries
    
    
    def save_config_file(self, json_dict: dict) -> None:
        json_obj = json.dumps(json_dict, indent=4)
        if not os.path.exists(f"scenarios/{self.num_consumer}_consumer"):
            os.makedirs(f"scenarios/{self.num_consumer}_consumer")
        with open(f"scenarios/{self.num_consumer}_consumer/config.json", "w") as of:
            of.write(json_obj)
    

if __name__ == "__main__":    
    # Set models and parameters
    generator_model = "hgb_south_10kwp"
    consumer_model = "two_person_all_working_no_heat"
    consumer = 1
    generators = 2
    storages = 1
    grid_conns = 1
    city = "hagenberg"
    
    # Set metadata for scenario
    metadata = {
        "name": f"{consumer} Consumer, {generators} Generator, rural",
        "description": "simple test network",
        "version": f"{date.today()}-V1"
    }
    
    # Set configurations - what if multiple generators with different configurations?
    configurations = {
        "south": {"aspect": 0, "kwp": 10, "angle": 22},
        "east": {"aspect": -90, "kwp": 2.5, "angle": 22},
        "west": {"aspect": 90, "kwp": 2.5, "angle": 22}
    }
    producer_model_identifier = f"{city}_" + "_".join([k + "-" + str(v["kwp"]) for k,v in configurations.items()])
    
    # Create DataFrames
    # If you want to choose another city, add parameters "latitude" and "longitude", default is Hagenberg
    dfc = DataFrameCreator(
        num_consumer=consumer,
        num_generators=generators,
        num_storages=storages,
        num_grid_connections=grid_conns,
        generator_model=generator_model,
        consumer_model=consumer_model,
        producer_model=producer_model_identifier,
        configs=configurations
    )
    df_grid = dfc.create_df_grid_connection()
    df_hh = dfc.create_df_household()
    df_gen = dfc.create_df_generator()
    df_prod = dfc.create_df_producer()
    df_stor = dfc.create_df_storage()
        
    # Create configuration file
    cc = ConfigurationCreator(
        metadata=metadata,
        df_grid_connection=df_grid,
        df_household=df_hh,
        df_generation=df_gen,
        df_producer=df_prod,
        df_storage=df_stor,
        profile_id_consumer=consumer_model,
        profile_id_generator=generator_model
    )
    json_dict = cc.generate_config()
    
    # Save json config
    dfc.save_config_file(json_dict)