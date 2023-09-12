import uuid
import pandas as pd

class CsvDataCreator:
    def __init__(self, num_consumer, num_generators, num_grid_connections, lat=48.3787, lon=14.5173):
        self.num_consumer = num_consumer
        self.num_generators = num_generators
        self.num_grid_connections = num_grid_connections
        self.address_number = 0
        self.lat = lat
        self.lon = lon
        
    def to_csv(self, filename, data):
        with open(file=filename, mode="w") as outfile:
            outfile.write(data)
        
    def create_df_grid_connection(self, filename):
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
            # increment
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
        
        # save to csv
        df_grid_connection.to_csv(filename, sep=";", index=False)
    
    
    def create_df_household(self, filename):
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
            profile_identifier.append("london2011-2014_cluster0")
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
        
        # save to csv
        df_consumer.to_csv(filename, sep=";", index=False)
    

    def create_df_generator(self, filename):
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
            profile_identifier.append("pvgis_hgp_south_10kwp")
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
        
        # save to csv
        df_generator.to_csv(filename, sep=";", index=False)


    
if __name__ == "__main__":
    c = CsvDataCreator(num_consumer=15, num_generators=1, num_grid_connections=1)
    c.create_df_grid_connection("./grid_connections.csv")
    c.create_df_household("./households.csv")
    c.create_df_generator("./generators.csv")
    