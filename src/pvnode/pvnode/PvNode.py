from typing import Union, List, Optional
from domain_models.Pv import PvModel, PvCollection

class PvNode:
    """Pv node, handles: collection of pvs, models for each pv, model query
    """

    def __init__(self, scenario_identifier: str = None):
        self._pvs: Optional[PvCollection] = None
        self._model_map: Optional[dict] = dict()
        self._scenario_identifier: Optional[str] = scenario_identifier

    @property
    def consumers(self) -> PvCollection:
        return self._pvs

    @consumers.setter
    def pvs(self, pvs: PvCollection) -> None:
        self._pvs = pvs

    @property
    def pv_models(self) -> dict:
        return self._model_map

    @pv_models.setter
    def pv_models(self, model_map: dict) -> None:
        self._model_map = model_map
    
    def get_pv(self, identifier: str, unixtimestamp_seconds: int) -> float:
        return self._model_map[identifier].get_pv(unixtimestamp_seconds)
    
    def __str__(self) -> str:
        return f"PvNode(pvs={[x for x in self._pvs]})"
