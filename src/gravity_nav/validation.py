from __future__ import annotations
from dataclasses import dataclass, asdict, replace
import numpy as np
import pandas as pd
from .assured_pnt import AssuredPNTConfig, run_assured_pnt

@dataclass
class ValidationConfig:
    runs: int = 30
    confidence: float = 0.95


def compare_modes(base_cfg:AssuredPNTConfig, runs:int=30, gravity_map=None, magnetic_map=None)->pd.DataFrame:
    rows=[]
    for mode in ['ins','gravity','magnetic','fused']:
        for i in range(runs):
            cfg=replace(base_cfg,mode=mode,seed=base_cfg.seed+i)
            _,m,_,_=run_assured_pnt(cfg,gravity_map=gravity_map,magnetic_map=magnetic_map)
            rows.append({'mode':mode,'run':i,'terminal_error_m':m['aided_terminal_m'],'rmse_m':m['aided_rmse_m']})
    return pd.DataFrame(rows)


def summarize_validation(df:pd.DataFrame)->pd.DataFrame:
    out=[]
    for mode,g in df.groupby('mode'):
        n=len(g); term=g.terminal_error_m.to_numpy(); rmse=g.rmse_m.to_numpy()
        out.append({'mode':mode,'runs':n,'terminal_median_m':float(np.median(term)),'terminal_p95_m':float(np.percentile(term,95)),
                    'terminal_mean_m':float(np.mean(term)),'terminal_std_m':float(np.std(term,ddof=1) if n>1 else 0),
                    'rmse_median_m':float(np.median(rmse)),'rmse_p95_m':float(np.percentile(rmse,95))})
    return pd.DataFrame(out).sort_values('terminal_median_m')
