from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from .assured_pnt import AssuredPNTConfig

@dataclass(frozen=True)
class SensorProfile:
    name: str
    description: str
    accel_noise_std: float
    bias_rw_std: float
    initial_bias_std: float
    gravity_noise_std: float
    gravity_update_period_s: float
    magnetic_noise_std_nt: float
    magnetic_update_period_s: float

PROFILES={
    'commercial': SensorProfile('commercial','Illustrative low-cost IMU + environmental aiding profile',0.08,2.0e-3,0.04,5.0,5.0,30.0,2.0),
    'tactical': SensorProfile('tactical','Illustrative tactical-grade IMU + environmental aiding profile',0.03,8e-4,0.015,2.0,2.0,8.0,1.0),
    'navigation': SensorProfile('navigation','Illustrative higher-grade IMU + environmental aiding profile',0.01,2e-4,0.005,1.0,1.0,3.0,0.5),
    'quantum-research': SensorProfile('quantum-research','Illustrative research cold-atom/gravity profile; not a hardware specification',0.02,5e-4,0.01,0.5,1.0,5.0,1.0),
}

def apply_profile(cfg:AssuredPNTConfig,name:str)->AssuredPNTConfig:
    p=PROFILES[name]
    return replace(cfg,accel_noise_std=p.accel_noise_std,bias_rw_std=p.bias_rw_std,initial_bias_std=p.initial_bias_std,
                   gravity_noise_std=p.gravity_noise_std,gravity_update_period_s=p.gravity_update_period_s,
                   magnetic_noise_std_nt=p.magnetic_noise_std_nt,magnetic_update_period_s=p.magnetic_update_period_s)

def profiles_as_dict(): return {k:asdict(v) for k,v in PROFILES.items()}
