import random
import pandas as pd
from datetime import datetime

""" 
The classes in this script are used for generating synthetic consumption data based on different templates: random consumption, 
daily consumption, and yearly consumption. The specific template and corresponding consumption value are determined based 
on the current time provided as a Unix timestamp.
"""

class RandomConsumption:
    def __init__(self, identifier: str):
        self.identifier: str = identifier
        self.load_min: int = 100
        self.load_max: int = 3000
        self.category_unit = "Wh"

    def get_consumption(self, unix_timestamp_seconds) -> float:
        return random.randint(self.load_min, self.load_max)

class DataframeTemplateDayConsumption:
    def __init__(self, identifier: str, consumption_data: pd.DataFrame):
        self.identifier: str = identifier
        grouped = consumption_data[['Hour', 'kwh']].groupby(by='Hour').median()
        values = grouped['kwh'].values
        self.consumption: dict = {}
        for k, v in enumerate(values):
            self.consumption[k] = {}
            for m in range(0, 60, 15):
                self.consumption[k][m] = v/4

    def get_consumption(self, unix_timestamp_seconds) -> float:
        dt = datetime.fromtimestamp(unix_timestamp_seconds)
        minute = dt.minute
        query_minute = (minute // 15) * 15
        return self.consumption[dt.hour][query_minute]

class DataframeTemplateYearConsumption:
    def __init__(self, identifier: str, consumption_data: pd.DataFrame):
        self.identifier: str = identifier
        self.consumption: dict = {}
        for k, v in enumerate(consumption_data.values):
            key = (v[2], v[3], v[4], v[5])
            self.consumption[key] = v[1]
    
    def get_consumption(self, unix_timestamp_seconds) -> float:
        dt = datetime.fromtimestamp(unix_timestamp_seconds)
        minute = dt.minute
        query_minute = (minute // 15) * 15
        return self.consumption[(dt.month, dt.day, dt.hour, query_minute)]