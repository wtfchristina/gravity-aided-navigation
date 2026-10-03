from __future__ import annotations

import numpy as np


def position_errors(truth_xy: np.ndarray, estimate_xy: np.ndarray) -> np.ndarray:
    return np.linalg.norm(estimate_xy - truth_xy, axis=1)


def summarize(truth_xy: np.ndarray, ins_xy: np.ndarray, aided_xy: np.ndarray) -> dict[str, float]:
    e_ins = position_errors(truth_xy, ins_xy)
    e_aid = position_errors(truth_xy, aided_xy)
    return {
        "ins_terminal_m": float(e_ins[-1]),
        "aided_terminal_m": float(e_aid[-1]),
        "ins_rmse_m": float(np.sqrt(np.mean(e_ins**2))),
        "aided_rmse_m": float(np.sqrt(np.mean(e_aid**2))),
        "terminal_improvement_pct": float(100.0 * (1.0 - e_aid[-1] / max(e_ins[-1], 1e-12))),
        "rmse_improvement_pct": float(100.0 * (1.0 - np.sqrt(np.mean(e_aid**2)) / max(np.sqrt(np.mean(e_ins**2)), 1e-12))),
    }
