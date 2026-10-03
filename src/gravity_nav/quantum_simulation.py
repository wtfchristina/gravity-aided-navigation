from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .cold_atom import ColdAtomGradiometer, ColdAtomGradiometerConfig
from .dynamics import nominal_acceleration, propagate_truth
from .gravity_tensor import SyntheticGravityTensorMap
from .imu import IMUConfig, IMUSimulator
from .metrics import summarize
from .tensor_ekf import TensorGravityAidedEKF


@dataclass
class QuantumSimulationConfig:
    duration_s: float = 200.0
    dt: float = 0.5
    speed_mps: float = 272.0
    seed: int = 11
    accel_noise_std: float = 0.03
    bias_rw_std: float = 8e-4
    initial_bias_std: float = 0.015
    cai_update_period_s: float = 2.0
    cai_interrogation_time_s: float = 0.25
    cai_baseline_m: float = 0.5
    phase_noise_std_rad: float = 0.004
    vibration_phase_std_rad: float = 0.003
    component: str = "Tzz"


def run_quantum_simulation(cfg: QuantumSimulationConfig | None = None):
    cfg = cfg or QuantumSimulationConfig()
    rng = np.random.default_rng(cfg.seed)
    gmap = SyntheticGravityTensorMap()
    imu = IMUSimulator(IMUConfig(cfg.accel_noise_std, cfg.bias_rw_std, cfg.initial_bias_std), rng)
    cai_cfg = ColdAtomGradiometerConfig(
        interrogation_time_s=cfg.cai_interrogation_time_s,
        baseline_m=cfg.cai_baseline_m,
        phase_noise_std_rad=cfg.phase_noise_std_rad,
        vibration_phase_std_rad=cfg.vibration_phase_std_rad,
        update_period_s=cfg.cai_update_period_s,
        component=cfg.component,
    )
    cai = ColdAtomGradiometer(gmap, cai_cfg, rng)

    n = int(cfg.duration_s / cfg.dt) + 1
    times = np.linspace(0.0, cfg.duration_s, n)
    truth = np.zeros((n, 4)); truth[0] = [0.0, 0.0, cfg.speed_mps, 0.0]
    ins = np.zeros((n, 4)); ins[0] = truth[0]

    x0 = np.array([*truth[0], 0.0, 0.0], dtype=float)
    P0 = np.diag([60.0**2, 60.0**2, 2.0**2, 2.0**2, 0.03**2, 0.03**2])
    ekf = TensorGravityAidedEKF(x0, P0, gmap, cfg.accel_noise_std, cfg.bias_rw_std)
    aided = np.zeros((n, 6)); aided[0] = ekf.x

    phase_meas = np.full(n, np.nan)
    gradient_meas = np.full(n, np.nan)
    true_gradient = np.full(n, np.nan)
    next_update = 0.0

    for k in range(1, n):
        t = times[k-1]
        a_true = nominal_acceleration(t)
        truth[k] = propagate_truth(truth[k-1], a_true, cfg.dt)
        a_meas, _ = imu.sample(a_true, cfg.dt)
        ins[k] = propagate_truth(ins[k-1], a_meas, cfg.dt)
        ekf.predict(a_meas, cfg.dt)

        if times[k] + 1e-12 >= next_update:
            m = cai.measure(truth[k, 0], truth[k, 1])
            phase_meas[k] = m["measured_phase_rad"]
            gradient_meas[k] = m["inferred_gradient_e"]
            true_gradient[k] = m["true_gradient_e"]
            ekf.update_component(cfg.component, m["inferred_gradient_e"], cai.equivalent_gradient_noise_std_e)
            next_update += cfg.cai_update_period_s
        aided[k] = ekf.x

    df = pd.DataFrame({
        "time_s": times,
        "truth_x_m": truth[:,0], "truth_y_m": truth[:,1],
        "ins_x_m": ins[:,0], "ins_y_m": ins[:,1],
        "aided_x_m": aided[:,0], "aided_y_m": aided[:,1],
        "cai_phase_rad": phase_meas,
        f"{cfg.component}_measured_E": gradient_meas,
        f"{cfg.component}_true_E": true_gradient,
    })
    metrics = summarize(truth[:,:2], ins[:,:2], aided[:,:2])
    metrics.update({
        "distance_km": float(np.sum(np.linalg.norm(np.diff(truth[:,:2], axis=0), axis=1))/1000.0),
        "duration_s": cfg.duration_s,
        "cai_equivalent_gradient_noise_std_E": cai.equivalent_gradient_noise_std_e,
        "cai_scale_factor_rad_per_E": cai.cfg.scale_factor_rad_per_eotvos,
    })
    return df, metrics, gmap, cai
