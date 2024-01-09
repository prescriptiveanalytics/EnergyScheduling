from pydantic import BaseModel
from typing import List, Optional


class OptimalPowerFlowBus(BaseModel):
    InService: dict
    Name: dict
    Type: dict
    VnKv: dict

class OptimalPowerFlowLine(BaseModel):
    CNfPerKm: dict
    C0NfPerKm: Optional[dict] = None
    Df: dict
    FromBus: dict
    GUsPerKm: dict
    G0UsPerKm: Optional[dict] = None
    InService: dict
    LengthKm: dict
    MaxIKa: dict
    Name: dict
    Parallel: dict
    ROhmPerKm: dict
    R0OhmPerKm: Optional[dict] = None
    StdType: dict
    ToBus: dict
    Type: dict
    XOhmPerKm: dict
    X0OhmPerKm: Optional[dict] = None

class OptimalPowerFlowLoad(BaseModel):
    Bus: dict
    ConstIPercent: dict
    ConstZPercent: dict
    InService: dict
    Name: dict
    PMw: dict
    QMvar: dict
    Scaling: dict
    SnMva: dict
    Type: dict

class OptimalPowerFlowResBus(BaseModel):
    PMw: dict
    QMvar: dict
    VaDegree: dict
    VmPu: dict

class OptimalPowerFlowResExtGrid(BaseModel):
    PMw: dict
    QMvar: dict

class OptimalPowerFlowResLine(BaseModel):
    IFromKa: dict
    IKa: dict
    IToKa: dict
    LoadingPercent: dict
    PFromMw: dict
    PToMw: dict
    PlMw: dict
    QFromMvar: dict
    QToMvar: dict
    QlMvar: dict
    VaFromDegree: dict
    VaToDegree: dict
    VmFromPu: dict
    VmToPu: dict

class OptimalPowerFlowResLoad(BaseModel):
    PMw: dict
    QMvar: dict

class OptimalPowerFlowResSgen(BaseModel):
    PMw: dict
    QMvar: dict

class OptimalPowerFlowSgen(BaseModel):
    Bus: dict
    CurrentSource: dict
    InService: dict
    Name: dict
    PMw: dict
    QMvar: dict
    Scaling: dict
    SnMva: dict
    Type: dict

class OptimalPowerFlowStorage(BaseModel):
    Name: dict
    Bus: dict
    PMw: dict
    QMvar: dict
    SnMva: dict
    SocPercent: dict
    MinEMwh: dict
    MaxEMwh: dict
    Scaling: dict
    InService: dict
    Type: dict

class OptimalPowerFlowResStorage(BaseModel):
    PMw: dict
    QMvar: dict

class OptimalPowerFlowSolution(BaseModel):
    Bus: OptimalPowerFlowBus
    Line: OptimalPowerFlowLine
    Load: OptimalPowerFlowLoad
    Sgen: OptimalPowerFlowSgen
    ResBus: OptimalPowerFlowResBus
    ResLine: OptimalPowerFlowResLine
    ResLoad: OptimalPowerFlowResLoad
    ResExtGrid: OptimalPowerFlowResExtGrid
    ResSgen: OptimalPowerFlowResSgen
    Storage: OptimalPowerFlowStorage
    ResStorage: OptimalPowerFlowResStorage


class OptimalPowerFlowSolutionCollection(BaseModel):
    OpfCollection: List[OptimalPowerFlowSolution]
