from __future__ import annotations
from dataclasses import dataclass, replace
import pandas as pd
from .assured_pnt import AssuredPNTConfig
from .requirements import MissionRequirement, solve_sensor_requirements


@dataclass(frozen=True)
class MissionEnvelope:
    outage_durations_s: tuple[float,...]=(300.0,600.0,900.0,1800.0)
    speeds_mps: tuple[float,...]=(50.0,83.0,150.0)


def mission_envelope_study(base: AssuredPNTConfig, requirement: MissionRequirement,
                           envelope: MissionEnvelope | None=None, runs: int=15) -> pd.DataFrame:
    """Find the least-demanding passing sensor combination across mission duration/speed points."""
    envelope=envelope or MissionEnvelope()
    rows=[]
    for duration in envelope.outage_durations_s:
        for speed in envelope.speeds_mps:
            cfg=replace(base,duration_s=float(duration),speed_mps=float(speed))
            trade=solve_sensor_requirements(cfg,requirement,
                gravity_noise=(1.0,2.0,4.0,8.0),magnetic_noise=(4.0,8.0,16.0,32.0),
                update_period=(0.5,1.0,2.0,5.0),runs=runs)
            passing=trade[trade.requirement_met]
            best=passing.iloc[0] if len(passing) else trade.iloc[0]
            rows.append({
                'duration_s':duration,'speed_mps':speed,
                'requirement_met':bool(best.requirement_met),
                'gravity_noise_std':float(best.gravity_noise_std),
                'magnetic_noise_std_nt':float(best.magnetic_noise_std_nt),
                'update_period_s':float(best.update_period_s),
                'success_probability':float(best.success_probability),
                'terminal_p95_m':float(best.terminal_p95_m),
                'rmse_p95_m':float(best.rmse_p95_m),
            })
    return pd.DataFrame(rows)
