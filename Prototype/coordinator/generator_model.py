from datetime import datetime

class PVGisGenerator:
    def __init__(self, identifier: str, generation: dict):
        self.identifier: str = identifier
        self.generation: dict = generation

    def get_generation(self, unix_timestamp_seconds) -> float:
        dt = datetime.fromtimestamp(unix_timestamp_seconds)
        query_minute = (dt.minute // 15) * 15
        return self.generation[(dt.month, dt.day, dt.hour, query_minute)]
