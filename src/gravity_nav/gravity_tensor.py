from __future__ import annotations

from dataclasses import dataclass
import numpy as np

EOTVOS = 1e-9  # s^-2


@dataclass(frozen=True)
class PotentialAnomaly:
    """Synthetic 2-D Gaussian perturbation to gravitational potential.

    amplitude has units m^2/s^2 and sigma_x/y are metres. The resulting
    second derivatives have units s^-2 and are reported in Eotvos (E).
    """

    x: float
    y: float
    amplitude: float
    sigma_x: float
    sigma_y: float


class SyntheticGravityTensorMap:
    """Differentiable synthetic gravity-gradient tensor map.

    Txx, Txy and Tyy are analytic second derivatives of a sum of Gaussian
    potential anomalies. Tzz is defined as -(Txx + Tyy), consistent with
    Laplace's equation in a local source-free approximation. This is a
    pedagogical field, not a geophysical product.
    """

    def __init__(self, anomalies: list[PotentialAnomaly] | None = None):
        if anomalies is None:
            anomalies = [
                PotentialAnomaly(7_000, 3_500, 2.4, 3_800, 3_200),
                PotentialAnomaly(17_000, -2_500, -2.0, 4_600, 3_500),
                PotentialAnomaly(28_000, 5_000, 3.0, 5_000, 4_100),
                PotentialAnomaly(39_000, -4_000, -2.5, 4_200, 3_200),
                PotentialAnomaly(49_000, 2_500, 2.1, 3_800, 3_600),
                PotentialAnomaly(31_000, 10_000, 1.5, 6_500, 4_500),
            ]
        self.anomalies = anomalies

    @staticmethod
    def _as_arrays(x, y):
        return np.asarray(x, dtype=float), np.asarray(y, dtype=float)

    def potential(self, x, y):
        x, y = self._as_arrays(x, y)
        out = np.zeros(np.broadcast(x, y).shape, dtype=float)
        for a in self.anomalies:
            dx = x - a.x
            dy = y - a.y
            e = np.exp(-0.5 * ((dx / a.sigma_x) ** 2 + (dy / a.sigma_y) ** 2))
            out += a.amplitude * e
        return out

    def components(self, x, y) -> dict[str, np.ndarray]:
        x, y = self._as_arrays(x, y)
        shape = np.broadcast(x, y).shape
        txx = np.zeros(shape, dtype=float)
        tyy = np.zeros(shape, dtype=float)
        txy = np.zeros(shape, dtype=float)
        for a in self.anomalies:
            dx = x - a.x
            dy = y - a.y
            sx2 = a.sigma_x**2
            sy2 = a.sigma_y**2
            e = np.exp(-0.5 * (dx**2 / sx2 + dy**2 / sy2))
            v = a.amplitude * e
            txx += v * (dx**2 / sx2**2 - 1.0 / sx2)
            tyy += v * (dy**2 / sy2**2 - 1.0 / sy2)
            txy += v * (dx * dy / (sx2 * sy2))
        tzz = -(txx + tyy)
        return {
            "Txx": txx / EOTVOS,
            "Txy": txy / EOTVOS,
            "Tyy": tyy / EOTVOS,
            "Tzz": tzz / EOTVOS,
        }

    def component(self, name: str, x, y):
        if name not in {"Txx", "Txy", "Tyy", "Tzz"}:
            raise ValueError(f"Unsupported tensor component: {name}")
        return self.components(x, y)[name]

    def jacobian_component(self, name: str, x: float, y: float, step_m: float = 5.0) -> np.ndarray:
        """Numerical spatial gradient [dT/dx, dT/dy] in E/m."""
        h = float(step_m)
        gx = (float(self.component(name, x + h, y)) - float(self.component(name, x - h, y))) / (2.0 * h)
        gy = (float(self.component(name, x, y + h)) - float(self.component(name, x, y - h))) / (2.0 * h)
        return np.array([gx, gy], dtype=float)

    def grid(self, component: str = "Tzz", xlim=(0.0, 55_000.0), ylim=(-15_000.0, 15_000.0), nx=240, ny=140):
        xs = np.linspace(*xlim, nx)
        ys = np.linspace(*ylim, ny)
        xx, yy = np.meshgrid(xs, ys)
        zz = self.component(component, xx, yy)
        return xx, yy, zz
