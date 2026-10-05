from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from itertools import product
import numpy as np
import pandas as pd
from .assured_pnt import AssuredPNTConfig, run_assured_pnt


@dataclass(frozen=True)
class MissionRequirement:
    """Synthetic mission-level navigation requirement for trade studies.

    This is an engineering screening construct, not a certification or safety case.
    """
    terminal_error_limit_m: float = 100.0
    rmse_limit_m: float = 150.0
    success_probability: float = 0.95
    alert_limit_m: float = 250.0


def evaluate_configuration(cfg: AssuredPNTConfig, requirement: MissionRequirement, runs: int = 50) -> dict:
    terminal=[]; rmse=[]
    for i in range(int(runs)):
        c=replace(cfg, seed=cfg.seed+i)
        _,m,_,_=run_assured_pnt(c)
        terminal.append(float(m['aided_terminal_m']))
        rmse.append(float(m['aided_rmse_m']))
    terminal=np.asarray(terminal); rmse=np.asarray(rmse)
    success=(terminal <= requirement.terminal_error_limit_m) & (rmse <= requirement.rmse_limit_m)
    alert_exceed=terminal > requirement.alert_limit_m
    return {
        'runs': int(runs),
        'terminal_median_m': float(np.median(terminal)),
        'terminal_p95_m': float(np.percentile(terminal,95)),
        'terminal_max_m': float(np.max(terminal)),
        'rmse_median_m': float(np.median(rmse)),
        'rmse_p95_m': float(np.percentile(rmse,95)),
        'success_probability': float(np.mean(success)),
        'alert_limit_exceedance_probability': float(np.mean(alert_exceed)),
        'requirement_met': bool(np.mean(success) >= requirement.success_probability),
        'requirement': asdict(requirement),
    }


def solve_sensor_requirements(
    base: AssuredPNTConfig,
    requirement: MissionRequirement,
    gravity_noise=(0.5,1.0,2.0,4.0,8.0),
    magnetic_noise=(2.0,4.0,8.0,16.0,32.0),
    update_period=(0.5,1.0,2.0,5.0),
    runs: int = 25,
) -> pd.DataFrame:
    """Sweep sensor specifications and identify configurations meeting a mission requirement."""
    rows=[]
    for gn,mn,up in product(gravity_noise,magnetic_noise,update_period):
        cfg=replace(base,mode='fused',gravity_noise_std=float(gn),magnetic_noise_std_nt=float(mn),
                    gravity_update_period_s=float(up),magnetic_update_period_s=float(up))
        result=evaluate_configuration(cfg,requirement,runs)
        rows.append({
            'gravity_noise_std':float(gn),
            'magnetic_noise_std_nt':float(mn),
            'update_period_s':float(up),
            **{k:v for k,v in result.items() if k not in {'requirement'}},
        })
    df=pd.DataFrame(rows)
    # Prefer passing solutions with the least demanding sensor/update assumptions.
    # "burden_score" is a relative procurement/design proxy, not a cost model.
    df['burden_score']=(1/df.gravity_noise_std)+(1/df.magnetic_noise_std_nt)+(1/df.update_period_s)
    return df.sort_values(['requirement_met','burden_score','terminal_p95_m'],ascending=[False,True,True]).reset_index(drop=True)
