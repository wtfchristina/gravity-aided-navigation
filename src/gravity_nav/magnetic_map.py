from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class MagneticAnomaly:
    x: float
    y: float
    amplitude_nt: float
    sigma_x: float
    sigma_y: float


class SyntheticMagneticMap:
    """Smooth synthetic magnetic anomaly map in nanotesla.

    This field is intentionally synthetic and is used only for estimator and
    trade-study demonstrations. It is not a World Magnetic Model product.
    """

    def __init__(self, anomalies: list[MagneticAnomaly] | None = None):
        self.anomalies = anomalies or [
            MagneticAnomaly(5_000, -4_000, 170.0, 3_800, 3_000),
            MagneticAnomaly(14_000, 5_000, -210.0, 5_200, 4_000),
            MagneticAnomaly(25_000, -1_000, 260.0, 4_800, 5_100),
            MagneticAnomaly(36_000, 7_000, -180.0, 5_500, 3_800),
            MagneticAnomaly(45_000, -5_500, 220.0, 4_200, 3_700),
            MagneticAnomaly(52_000, 3_000, -130.0, 3_800, 4_600),
        ]

    def value(self, x, y):
        x_arr = np.asarray(x, dtype=float)
        y_arr = np.asarray(y, dtype=float)
        out = np.zeros(np.broadcast(x_arr, y_arr).shape, dtype=float)
        for a in self.anomalies:
            dx = (x_arr - a.x) / a.sigma_x
            dy = (y_arr - a.y) / a.sigma_y
            out += a.amplitude_nt * np.exp(-0.5 * (dx*dx + dy*dy))
        return out

    def gradient(self, x: float, y: float) -> np.ndarray:
        gx = gy = 0.0
        for a in self.anomalies:
            dx = x - a.x
            dy = y - a.y
            e = np.exp(-0.5 * ((dx/a.sigma_x)**2 + (dy/a.sigma_y)**2))
            term = a.amplitude_nt * e
            gx += term * (-dx / a.sigma_x**2)
            gy += term * (-dy / a.sigma_y**2)
        return np.array([gx, gy], dtype=float)

    def grid(self, xlim=(0.0, 55_000.0), ylim=(-15_000.0, 15_000.0), nx=240, ny=140):
        xs = np.linspace(*xlim, nx)
        ys = np.linspace(*ylim, ny)
        xx, yy = np.meshgrid(xs, ys)
        return xx, yy, self.value(xx, yy)
