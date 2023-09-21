from typing import Union, List, Optional
from domain_models.Generator import GeneratorModel, GeneratorCollection

class GeneratorNode:
    """Generator node, handles: collection of generators, models for each generator, model query
    """

    def __init__(self, scenario_identifier: str) -> None:
        self._generators: Optional[GeneratorCollection] = None
        self._model_map: Optional[dict] = None
        self._scenario_identifier: Optional[str] = scenario_identifier

    @property
    def generators(self) -> GeneratorCollection:
        return self._generators
    
    @generators.setter
    def generators(self, generators: GeneratorCollection) -> None:
        self._generators = generators
    
    @property
    def generation_models(self) -> dict:
        return self._model_map

    @generation_models.setter
    def generation_models(self, model_map: dict) -> None:
        self._model_map = model_map
    
    def get_generation(self, identifier: str, unixtimestamp_seconds) -> float:
        return self._model_map[identifier].get_generation(unixtimestamp_seconds)
