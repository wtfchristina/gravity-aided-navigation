from __future__ import annotations
from dataclasses import replace
from itertools import product
import pandas as pd
from .assured_pnt import AssuredPNTConfig, run_assured_pnt


def sensor_trade_study(base: AssuredPNTConfig, gravity_noise=(1.0,2.0,4.0,8.0),
                       magnetic_noise=(4.0,8.0,16.0,32.0), update_period=(0.5,1.0,2.0,5.0),
                       seeds=(21,22,23)) -> pd.DataFrame:
    rows=[]
    for gn,mn,up in product(gravity_noise,magnetic_noise,update_period):
        vals=[]
        for seed in seeds:
            cfg=replace(base,mode="fused",gravity_noise_std=float(gn),magnetic_noise_std_nt=float(mn),
                        gravity_update_period_s=float(up),magnetic_update_period_s=float(up),seed=int(seed))
            _,m,_,_=run_assured_pnt(cfg)
            vals.append(m)
        rows.append({
            "gravity_noise_std":gn,"magnetic_noise_std_nt":mn,"update_period_s":up,
            "terminal_mean_m":sum(v["aided_terminal_m"] for v in vals)/len(vals),
            "rmse_mean_m":sum(v["aided_rmse_m"] for v in vals)/len(vals),
            "terminal_improvement_mean_pct":sum(v["terminal_improvement_pct"] for v in vals)/len(vals),
        })
    return pd.DataFrame(rows).sort_values("terminal_mean_m")
