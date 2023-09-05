from pydantic import BaseModel
from typing import List

class OptimalPowerFlowBus(BaseModel):
    in_service: dict
    name: dict
    type: dict
    vn_kv: dict

class OptimalPowerFlowLine(BaseModel):
    c_nf_per_km: dict
    c0_nf_per_km: dict
    df: dict
    from_bus: dict
    g_us_per_km: dict
    g0_us_per_km: dict
    in_service: dict
    length_km: dict
    max_i_ka: dict
    name: dict
    parallel: dict
    r_ohm_per_km: dict
    r0_ohm_per_km: dict
    std_type: dict
    to_bus: dict
    type: dict
    x_ohm_per_km: dict
    x0_ohm_per_km: dict

class OptimalPowerFlowLoad(BaseModel):
    bus: dict
    const_i_percent: dict
    const_z_percent: dict
    in_service: dict
    name: dict
    p_mw: dict
    q_mvar: dict
    scaling: dict
    sn_mva: dict
    type: dict

class OptimalPowerFlowResBus(BaseModel):
    p_mw: dict
    q_mvar: dict
    va_degree: dict
    vm_pu: dict

class OptimalPowerFlowResExtGrid(BaseModel):
    p_mw: dict
    q_mvar: dict

class OptimalPowerFlowResLine(BaseModel):
    i_from_ka: dict
    i_ka: dict
    i_to_ka: dict
    loading_percent: dict
    p_from_mw: dict
    p_to_mw: dict
    pl_mw: dict
    q_from_mvar: dict
    q_to_mvar: dict
    ql_mvar: dict
    va_from_degree: dict
    va_to_degree: dict
    vm_from_pu: dict
    vm_to_pu: dict

class OptimalPowerFlowResLoad(BaseModel):
    p_mw: dict
    q_mvar: dict

class OptimalPowerFlowResSgen(BaseModel):
    p_mw: dict
    q_mvar: dict

class OptimalPowerFlowSgen(BaseModel):
    bus: dict
    current_source: dict
    in_service: dict
    name: dict
    p_mw: dict
    q_mvar: dict
    scaling: dict
    sn_mva: dict
    type: dict

class OptimalPowerFlowSolution(BaseModel):
    bus: OptimalPowerFlowBus
    line: OptimalPowerFlowLine
    load: OptimalPowerFlowLoad
    sgen: OptimalPowerFlowSgen
    res_bus: OptimalPowerFlowResBus
    res_line: OptimalPowerFlowResLine
    res_load: OptimalPowerFlowResLoad
    res_ext_grid: OptimalPowerFlowResExtGrid
    res_sgen: OptimalPowerFlowResSgen

class OptimalPowerFlowSolutionCollection(BaseModel):
    opf_collection: List[OptimalPowerFlowSolution]