from typing import Union, List, Optional
from domain_models.Consumer import ConsumerModel, ConsumerCollection

class ConsumerNode:
    """Consumer node, handles: collection of consumers, models for each consumer, model query
    """

    def __init__(self, scenario_identifier: str = None):
        self._consumers: Optional[ConsumerCollection] = None
        self._model_map: Optional[dict] = dict()
        self._scenario_identifier: Optional[str] = scenario_identifier

    @property
    def consumers(self) -> ConsumerCollection:
        return self._consumers

    @consumers.setter
    def consumers(self, consumers: ConsumerCollection) -> None:
        self._consumers = consumers

    @property
    def consumption_models(self) -> dict:
        return self._model_map

    @consumption_models.setter
    def consumption_models(self, model_map: dict) -> None:
        self._model_map = model_map
    
    def get_consumption(self, identifier: str, unixtimestamp_seconds: int) -> float:
        return self._model_map[identifier].get_consumption(unixtimestamp_seconds)
    
    def __str__(self) -> str:
        return f"ConsumerNode(consumers={[x for x in self._consumers]})"
