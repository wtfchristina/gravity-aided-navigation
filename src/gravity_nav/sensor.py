from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .gravity_map import SyntheticGravityMap


@dataclass
class GravitySensorConfig:
    noise_std: float = 2.0   # synthetic map units
    update_period: float = 2.0


class GravitySensor:
    def __init__(self, gravity_map: SyntheticGravityMap, cfg: GravitySensorConfig, rng: np.random.Generator):
        self.gravity_map = gravity_map
        self.cfg = cfg
        self.rng = rng

    def measure(self, x: float, y: float) -> float:
        return float(self.gravity_map.value(x, y) + self.rng.normal(0.0, self.cfg.noise_std))
