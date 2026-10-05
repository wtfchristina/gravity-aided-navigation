from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator


@dataclass
class GridFieldMap:
    """Regular-grid scalar field map with bilinear interpolation.

    CSV format: x_m,y_m,value with a complete rectangular grid.
    NPZ format: arrays named x, y, value where value.shape == (len(y), len(x)).
    """
    x: np.ndarray
    y: np.ndarray
    values: np.ndarray
    name: str = "field"
    units: str = "arb"

    def __post_init__(self):
        self.x = np.asarray(self.x, dtype=float)
        self.y = np.asarray(self.y, dtype=float)
        self.values = np.asarray(self.values, dtype=float)
        if self.values.shape != (len(self.y), len(self.x)):
            raise ValueError("values must have shape (len(y), len(x))")
        self._interp = RegularGridInterpolator((self.y, self.x), self.values, bounds_error=False, fill_value=None)

    @classmethod
    def from_csv(cls, path: str | Path, name: str = "field", units: str = "arb") -> "GridFieldMap":
        df = pd.read_csv(path)
        required = {"x_m", "y_m", "value"}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must contain {sorted(required)}")
        xs = np.sort(df.x_m.unique())
        ys = np.sort(df.y_m.unique())
        pivot = df.pivot(index="y_m", columns="x_m", values="value").reindex(index=ys, columns=xs)
        if pivot.isna().any().any():
            raise ValueError("CSV must define a complete rectangular grid")
        return cls(xs, ys, pivot.to_numpy(), name=name, units=units)

    @classmethod
    def from_npz(cls, path: str | Path, name: str = "field", units: str = "arb") -> "GridFieldMap":
        d = np.load(path)
        return cls(d["x"], d["y"], d["value"], name=name, units=units)

    def to_csv(self, path: str | Path):
        xx, yy = np.meshgrid(self.x, self.y)
        pd.DataFrame({"x_m": xx.ravel(), "y_m": yy.ravel(), "value": self.values.ravel()}).to_csv(path, index=False)

    def value(self, x, y):
        xa = np.asarray(x, dtype=float)
        ya = np.asarray(y, dtype=float)
        shape = np.broadcast(xa, ya).shape
        pts = np.column_stack([np.broadcast_to(ya, shape).ravel(), np.broadcast_to(xa, shape).ravel()])
        out = self._interp(pts).reshape(shape)
        return float(out) if shape == () else out

    def gradient(self, x: float, y: float, step_m: float = 25.0) -> np.ndarray:
        h = float(step_m)
        gx = (self.value(x+h, y) - self.value(x-h, y)) / (2*h)
        gy = (self.value(x, y+h) - self.value(x, y-h)) / (2*h)
        return np.array([gx, gy], dtype=float)

    def grid(self):
        xx, yy = np.meshgrid(self.x, self.y)
        return xx, yy, self.values.copy()
