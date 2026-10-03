from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .gravity_tensor import EOTVOS, SyntheticGravityTensorMap


@dataclass
class ColdAtomGradiometerConfig:
    """Simplified differential light-pulse atom-interferometer model.

    Differential phase model:
        Delta phi ~= k_eff * Gamma * baseline * T^2

    where Gamma is a gravity-gradient component in s^-2.
    """

    k_eff_rad_per_m: float = 1.61e7
    interrogation_time_s: float = 0.25
    baseline_m: float = 0.5
    phase_noise_std_rad: float = 0.015
    vibration_phase_std_rad: float = 0.010
    update_period_s: float = 2.0
    dead_time_s: float = 0.25
    component: str = "Tzz"

    @property
    def scale_factor_rad_per_eotvos(self) -> float:
        return (
            self.k_eff_rad_per_m
            * self.baseline_m
            * self.interrogation_time_s**2
            * EOTVOS
        )


class ColdAtomGradiometer:
    """Synthetic cold-atom gravity gradiometer.

    The class intentionally models only the measurement chain needed for the
    navigation demo: field -> differential phase -> noisy phase -> inferred
    gravity gradient. It does not claim flight-qualified CAI performance.
    """

    def __init__(self, gravity_map: SyntheticGravityTensorMap, cfg: ColdAtomGradiometerConfig, rng: np.random.Generator):
        self.gravity_map = gravity_map
        self.cfg = cfg
        self.rng = rng

    def gradient_to_phase(self, gradient_e: float) -> float:
        return float(gradient_e * self.cfg.scale_factor_rad_per_eotvos)

    def phase_to_gradient(self, phase_rad: float) -> float:
        scale = self.cfg.scale_factor_rad_per_eotvos
        if abs(scale) < 1e-30:
            raise ZeroDivisionError("Cold-atom scale factor is zero")
        return float(phase_rad / scale)

    @property
    def equivalent_gradient_noise_std_e(self) -> float:
        total_phase = np.hypot(self.cfg.phase_noise_std_rad, self.cfg.vibration_phase_std_rad)
        return float(total_phase / self.cfg.scale_factor_rad_per_eotvos)

    def measure(self, x: float, y: float) -> dict[str, float]:
        true_gradient_e = float(self.gravity_map.component(self.cfg.component, x, y))
        true_phase = self.gradient_to_phase(true_gradient_e)
        phase_noise = self.rng.normal(0.0, self.cfg.phase_noise_std_rad)
        vibration = self.rng.normal(0.0, self.cfg.vibration_phase_std_rad)
        measured_phase = true_phase + phase_noise + vibration
        inferred_gradient_e = self.phase_to_gradient(measured_phase)
        return {
            "true_gradient_e": true_gradient_e,
            "true_phase_rad": true_phase,
            "measured_phase_rad": measured_phase,
            "inferred_gradient_e": inferred_gradient_e,
        }
