from domain_models.NetworkModel import ScenarioNetworkModel
from domain_models.ConsumerModel import ConsumerCollection
from domain_models.GeneratorModel import GeneratorCollection
from domain_models.StorageModel import StorageCollection


class NetworkNode:
    """Network node handles: communication with the consumer and producer nodes
    """

    def __init__(self, scenario_identifier: str) -> None:
        self._scenario_identifier = scenario_identifier
        self._initialized = False
        self._consumers = None
        self._consumption_models = None
        self._generators = None
        self._generation_models = None
        self._networks = None
        self._storages = None

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
    def consumption_models(self) -> object:
        return self._consumption_models

    @consumption_models.setter
    def consumption_models(self, value: object):
        self._consumption_models = value

    @property
    def generators(self) -> GeneratorCollection:
        return self._generators

    @generators.setter
    def generators(self, value: GeneratorCollection):
        self._generators = value

    @property
    def generation_models(self):
        return self._generation_models

    @generation_models.setter
    def generation_models(self, value: object):
        self._generation_models = value

    @property
    def networks(self) -> ScenarioNetworkModel:
        return self._networks

    @networks.setter
    def networks(self, value: ScenarioNetworkModel):
        self._networks = value

    @property
    def storages(self) -> StorageCollection:
        return self._storages

    @storages.setter
    def storages(self, value: StorageCollection):
        self._storages = value

    def __str__(self) -> str:
        return (f"NetworkNode(scenario_identifier={self._scenario_identifier},"
                f"initialized={self._initialized},"
                f"consumers={self._consumers},"
                f"generators={self._generators},"
                f"storages={self._storages},"
                f"networks={self._networks})")
