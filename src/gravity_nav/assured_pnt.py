from __future__ import annotations

from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

from .dynamics import nominal_acceleration, propagate_truth
from .imu import IMUConfig, IMUSimulator
from .gravity_map import SyntheticGravityMap
from .magnetic_map import SyntheticMagneticMap
from .fusion import FusionEKF, FieldObservation
from .metrics import position_errors


@dataclass
class AssuredPNTConfig:
    duration_s: float = 600.0
    dt: float = 0.5
    speed_mps: float = 83.0
    seed: int = 21
    mode: str = "fused"  # ins, gravity, magnetic, fused
    accel_noise_std: float = 0.03
    bias_rw_std: float = 8e-4
    initial_bias_std: float = 0.015
    gravity_noise_std: float = 2.0
    gravity_update_period_s: float = 2.0
    magnetic_noise_std_nt: float = 8.0
    magnetic_update_period_s: float = 1.0
    innovation_gate_sigma: float = 5.0


def run_assured_pnt(cfg: AssuredPNTConfig | None = None, gravity_map=None, magnetic_map=None):
    cfg = cfg or AssuredPNTConfig()
    if cfg.mode not in {"ins", "gravity", "magnetic", "fused"}:
        raise ValueError("mode must be ins, gravity, magnetic, or fused")
    # Independent deterministic random streams keep the IMU realization identical
    # across aiding modes, which makes trade-study comparisons fair.
    ss = np.random.SeedSequence(cfg.seed)
    imu_ss, gravity_ss, magnetic_ss = ss.spawn(3)
    imu_rng = np.random.default_rng(imu_ss)
    gravity_rng = np.random.default_rng(gravity_ss)
    magnetic_rng = np.random.default_rng(magnetic_ss)
    gmap = gravity_map or SyntheticGravityMap()
    mmap = magnetic_map or SyntheticMagneticMap()
    imu = IMUSimulator(IMUConfig(cfg.accel_noise_std, cfg.bias_rw_std, cfg.initial_bias_std), imu_rng)

    n = int(cfg.duration_s/cfg.dt)+1
    times = np.linspace(0,cfg.duration_s,n)
    truth = np.zeros((n,4)); truth[0]=[0,0,cfg.speed_mps,0]
    ins = np.zeros((n,4)); ins[0]=truth[0]
    x0 = np.array([*truth[0],0.0,0.0])
    P0 = np.diag([40**2,40**2,2**2,2**2,0.03**2,0.03**2])
    ekf = FusionEKF(x0,P0,cfg.accel_noise_std,cfg.bias_rw_std)
    aided=np.zeros((n,6)); aided[0]=ekf.x
    g_meas=np.full(n,np.nan); m_meas=np.full(n,np.nan)
    g_used=np.zeros(n,dtype=bool); m_used=np.zeros(n,dtype=bool)
    next_g=0.0; next_m=0.0

    for k in range(1,n):
        a_true = nominal_acceleration(times[k-1])
        truth[k]=propagate_truth(truth[k-1],a_true,cfg.dt)
        a_meas,_ = imu.sample(a_true,cfg.dt)
        ins[k]=propagate_truth(ins[k-1],a_meas,cfg.dt)
        ekf.predict(a_meas,cfg.dt)

        if cfg.mode in {"gravity","fused"} and times[k]+1e-12 >= next_g:
            z=float(gmap.value(truth[k,0],truth[k,1])+gravity_rng.normal(0,cfg.gravity_noise_std))
            g_meas[k]=z
            g_used[k]=ekf.update(FieldObservation("gravity",gmap,z,cfg.gravity_noise_std),cfg.innovation_gate_sigma)
            next_g += cfg.gravity_update_period_s
        if cfg.mode in {"magnetic","fused"} and times[k]+1e-12 >= next_m:
            z=float(mmap.value(truth[k,0],truth[k,1])+magnetic_rng.normal(0,cfg.magnetic_noise_std_nt))
            m_meas[k]=z
            m_used[k]=ekf.update(FieldObservation("magnetic",mmap,z,cfg.magnetic_noise_std_nt),cfg.innovation_gate_sigma)
            next_m += cfg.magnetic_update_period_s
        aided[k]=ekf.x

    est = ins[:,:2] if cfg.mode=="ins" else aided[:,:2]
    e_ins=position_errors(truth[:,:2],ins[:,:2])
    e_est=position_errors(truth[:,:2],est)
    metrics={
        "mode": cfg.mode,
        "distance_km": float(np.sum(np.linalg.norm(np.diff(truth[:,:2],axis=0),axis=1))/1000),
        "ins_terminal_m": float(e_ins[-1]),
        "aided_terminal_m": float(e_est[-1]),
        "ins_rmse_m": float(np.sqrt(np.mean(e_ins**2))),
        "aided_rmse_m": float(np.sqrt(np.mean(e_est**2))),
        "terminal_improvement_pct": float(100*(1-e_est[-1]/max(e_ins[-1],1e-12))),
        "rmse_improvement_pct": float(100*(1-np.sqrt(np.mean(e_est**2))/max(np.sqrt(np.mean(e_ins**2)),1e-12))),
        "gravity_updates_accepted": int(g_used.sum()),
        "magnetic_updates_accepted": int(m_used.sum()),
        "config": asdict(cfg),
    }
    df=pd.DataFrame({
        "time_s":times,
        "truth_x_m":truth[:,0],"truth_y_m":truth[:,1],
        "ins_x_m":ins[:,0],"ins_y_m":ins[:,1],
        "aided_x_m":est[:,0],"aided_y_m":est[:,1],
        "gravity_measurement":g_meas,"magnetic_measurement_nt":m_meas,
        "gravity_update_accepted":g_used,"magnetic_update_accepted":m_used,
    })
    return df, metrics, gmap, mmap
