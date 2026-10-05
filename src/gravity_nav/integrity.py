from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd
from .assured_pnt import AssuredPNTConfig, run_assured_pnt
from .metrics import position_errors


@dataclass(frozen=True)
class IntegrityConfig:
    alert_limit_m: float = 250.0
    empirical_quantile: float = 0.95
    protection_scale: float = 1.25


def single_run_integrity(df: pd.DataFrame, cfg: IntegrityConfig | None = None) -> tuple[pd.DataFrame, dict]:
    """Compute transparent empirical integrity proxies from a synthetic run.

    The protection level is an analysis proxy based on rolling error statistics. It is NOT an
    aviation-certified protection level and must not be represented as one.
    """
    cfg=cfg or IntegrityConfig()
    truth=df[['truth_x_m','truth_y_m']].to_numpy()
    est=df[['aided_x_m','aided_y_m']].to_numpy()
    err=position_errors(truth,est)
    # Causal rolling RMS + scale, useful for demonstration of alert-limit monitoring.
    s=pd.Series(err)
    window=max(10,min(120,len(s)//10 if len(s)//10 else 10))
    rolling_rms=np.sqrt(s.pow(2).rolling(window,min_periods=1).mean()).to_numpy()
    protection=cfg.protection_scale*rolling_rms
    alert=protection > cfg.alert_limit_m
    out=df.copy()
    out['position_error_m']=err
    out['protection_level_proxy_m']=protection
    out['integrity_alert']=alert
    metrics={
        'alert_limit_m':cfg.alert_limit_m,
        'max_position_error_m':float(err.max()),
        'max_protection_level_proxy_m':float(protection.max()),
        'availability_fraction':float(np.mean(~alert)),
        'alert_fraction':float(np.mean(alert)),
        'hazardously_misleading_information_proxy_fraction':float(np.mean((err>cfg.alert_limit_m)&(~alert))),
        'note':'Empirical research proxy only; not a certified protection level or integrity claim.'
    }
    return out,metrics


def campaign_integrity(base: AssuredPNTConfig, integrity: IntegrityConfig | None = None, runs: int = 50) -> pd.DataFrame:
    integrity=integrity or IntegrityConfig()
    rows=[]
    for i in range(int(runs)):
        cfg=replace(base,seed=base.seed+i)
        df,m,_,_=run_assured_pnt(cfg)
        _,im=single_run_integrity(df,integrity)
        rows.append({
            'run':i,
            'terminal_error_m':m['aided_terminal_m'],
            'rmse_m':m['aided_rmse_m'],
            'availability_fraction':im['availability_fraction'],
            'alert_fraction':im['alert_fraction'],
            'hmi_proxy_fraction':im['hazardously_misleading_information_proxy_fraction'],
            'max_error_m':im['max_position_error_m'],
            'max_protection_proxy_m':im['max_protection_level_proxy_m'],
        })
    return pd.DataFrame(rows)
