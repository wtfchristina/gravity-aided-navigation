from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .dynamics import nominal_acceleration, propagate_truth
from .gravity_map import SyntheticGravityMap
from .imu import IMUConfig, IMUSimulator
from .sensor import GravitySensorConfig, GravitySensor
from .ekf import GravityAidedEKF
from .metrics import summarize


@dataclass
class SimulationConfig:
    duration_s: float = 600.0
    dt: float = 0.5
    speed_mps: float = 83.0  # ~Mach 0.24; chosen to traverse ~50 km in 10 min
    seed: int = 7
    gravity_noise_std: float = 2.0
    gravity_update_period: float = 2.0
    accel_noise_std: float = 0.03
    bias_rw_std: float = 8e-4
    initial_bias_std: float = 0.015


def run_simulation(cfg: SimulationConfig | None = None):
    cfg = cfg or SimulationConfig()
    rng = np.random.default_rng(cfg.seed)
    gmap = SyntheticGravityMap()
    imu = IMUSimulator(IMUConfig(cfg.accel_noise_std, cfg.bias_rw_std, cfg.initial_bias_std), rng)
    gsensor = GravitySensor(gmap, GravitySensorConfig(cfg.gravity_noise_std, cfg.gravity_update_period), rng)

    n = int(cfg.duration_s / cfg.dt) + 1
    times = np.linspace(0.0, cfg.duration_s, n)

    truth = np.zeros((n, 4))
    truth[0] = np.array([0.0, 0.0, cfg.speed_mps, 0.0])

    # INS-only dead reckoning state [x,y,vx,vy]
    ins = np.zeros((n, 4))
    ins[0] = truth[0].copy()

    x0 = np.array([*truth[0], 0.0, 0.0])
    P0 = np.diag([40.0**2, 40.0**2, 2.0**2, 2.0**2, 0.03**2, 0.03**2])
    ekf = GravityAidedEKF(x0, P0, gmap, cfg.accel_noise_std, cfg.bias_rw_std)
    aided = np.zeros((n, 6))
    aided[0] = ekf.x

    imu_bias = np.zeros((n, 2))
    gravity_meas = np.full(n, np.nan)
    next_gravity_t = 0.0

    for k in range(1, n):
        t_prev = times[k-1]
        a_true = nominal_acceleration(t_prev)
        truth[k] = propagate_truth(truth[k-1], a_true, cfg.dt)

        a_meas, bias = imu.sample(a_true, cfg.dt)
        imu_bias[k] = bias

        ins[k] = propagate_truth(ins[k-1], a_meas, cfg.dt)
        ekf.predict(a_meas, cfg.dt)

        if times[k] + 1e-12 >= next_gravity_t:
            z = gsensor.measure(truth[k, 0], truth[k, 1])
            gravity_meas[k] = z
            ekf.update_gravity(z, cfg.gravity_noise_std)
            next_gravity_t += cfg.gravity_update_period

        aided[k] = ekf.x

    df = pd.DataFrame({
        "time_s": times,
        "truth_x_m": truth[:, 0], "truth_y_m": truth[:, 1],
        "ins_x_m": ins[:, 0], "ins_y_m": ins[:, 1],
        "aided_x_m": aided[:, 0], "aided_y_m": aided[:, 1],
        "truth_vx_mps": truth[:, 2], "truth_vy_mps": truth[:, 3],
        "aided_vx_mps": aided[:, 2], "aided_vy_mps": aided[:, 3],
        "imu_bias_x_mps2": imu_bias[:, 0], "imu_bias_y_mps2": imu_bias[:, 1],
        "gravity_measurement": gravity_meas,
    })

    metrics = summarize(truth[:, :2], ins[:, :2], aided[:, :2])
    metrics["distance_km"] = float(np.sum(np.linalg.norm(np.diff(truth[:, :2], axis=0), axis=1)) / 1000.0)
    metrics["duration_s"] = cfg.duration_s
    return df, metrics, gmap
