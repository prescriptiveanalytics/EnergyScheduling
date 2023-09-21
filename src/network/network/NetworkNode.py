from typing import Union, List, Optional
from domain_models.NetworkModel import NetworkBusModel, NetworkEntityModel, NetworkLineModel, NetworkModel, ScenarioNetworkModel
from domain_models.ConsumerModel import ConsumerModel, ConsumerCollection
from domain_models.GeneratorModel import GeneratorModel, GeneratorCollection

class NetworkNode:
    """Network node handles: communication with the consumer and producer nodes
    """

    def __init__(self, scenario_identifier: str) -> None:
        self._scenario_identifier = scenario_identifier
        self._initialized = False
        self._consumers = None
        self._generators = None
        self._networks = None

    @property
    def initialized(self) -> bool:
        return self._initialized

    @initialized.setter
    def initialized(self, value: bool):
        self._initialized = value

    @property
    def consumers(self) -> ConsumerCollection:
        return self._consumers

    @consumers.setter
    def consumers(self, value: ConsumerCollection):
        self._consumers = value

    @property
    def generators(self) -> GeneratorCollection:
        return self._generators

    @generators.setter
    def generators(self, value: GeneratorCollection):
        self._generators = value

    @property
    def networks(self) -> ScenarioNetworkModel:
        return self._networks

    @networks.setter
    def networks(self, value: ScenarioNetworkModel):
        self._networks = value

    def __str__(self) -> str:
        return f"NetworkNode(scenario_identifier={self._scenario_identifier},initialized={self._initialized},consumers={self._consumers},generators={self._generators},networks={self._networks})"