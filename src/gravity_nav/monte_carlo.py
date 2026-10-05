from __future__ import annotations
from dataclasses import replace
import pandas as pd
import numpy as np
from .assured_pnt import AssuredPNTConfig, run_assured_pnt


def run_campaign(base: AssuredPNTConfig, runs: int = 50, modes=("ins","gravity","magnetic","fused")) -> pd.DataFrame:
    rows=[]
    for mode in modes:
        for i in range(int(runs)):
            cfg=replace(base,mode=mode,seed=base.seed+i)
            _,m,_,_=run_assured_pnt(cfg)
            rows.append({k:v for k,v in m.items() if k!="config"} | {"run":i})
    return pd.DataFrame(rows)


def summarize_campaign(df: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for mode,g in df.groupby("mode"):
        rows.append({
            "mode":mode,
            "runs":len(g),
            "terminal_median_m":float(g.aided_terminal_m.median()),
            "terminal_p95_m":float(np.percentile(g.aided_terminal_m,95)),
            "rmse_median_m":float(g.aided_rmse_m.median()),
            "rmse_p95_m":float(np.percentile(g.aided_rmse_m,95)),
            "divergence_rate_gt_2km":float(np.mean(g.aided_terminal_m>2000.0)),
        })
    return pd.DataFrame(rows).sort_values("terminal_median_m")
