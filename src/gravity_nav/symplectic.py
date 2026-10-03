from __future__ import annotations

import numpy as np
from scipy.optimize import root

MU = 3.986004418e14  # m^3/s^2


def kepler_rhs(state: np.ndarray, mu: float = MU) -> np.ndarray:
    x, y, px, py = state
    r = np.hypot(x, y)
    return np.array([px, py, -mu*x/r**3, -mu*y/r**3], dtype=float)


def kepler_hamiltonian(state: np.ndarray, mu: float = MU) -> float:
    x, y, px, py = state
    r = np.hypot(x, y)
    return float(0.5*(px*px + py*py) - mu/r)


def rk4_step(state: np.ndarray, dt: float) -> np.ndarray:
    k1 = kepler_rhs(state)
    k2 = kepler_rhs(state + 0.5*dt*k1)
    k3 = kepler_rhs(state + 0.5*dt*k2)
    k4 = kepler_rhs(state + dt*k3)
    return state + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)


def implicit_midpoint_step(state: np.ndarray, dt: float) -> np.ndarray:
    def residual(next_state):
        midpoint = 0.5*(state + next_state)
        return next_state - state - dt*kepler_rhs(midpoint)
    guess = state + dt*kepler_rhs(state)
    sol = root(residual, guess, method="hybr", tol=1e-11)
    if not sol.success:
        raise RuntimeError(f"Implicit midpoint solve failed: {sol.message}")
    return np.asarray(sol.x, dtype=float)


def benchmark(duration_s: float = 600_000.0, dt: float = 120.0, altitude_m: float = 500_000.0):
    earth_radius = 6_378_137.0
    r0 = earth_radius + altitude_m
    v0 = np.sqrt(MU/r0)
    initial = np.array([r0, 0.0, 0.0, v0], dtype=float)
    n = int(duration_s/dt) + 1
    t = np.linspace(0.0, duration_s, n)
    rk = np.zeros((n,4)); mp = np.zeros((n,4))
    rk[0] = initial; mp[0] = initial
    for k in range(1,n):
        rk[k] = rk4_step(rk[k-1], dt)
        mp[k] = implicit_midpoint_step(mp[k-1], dt)
    h0 = kepler_hamiltonian(initial)
    rk_e = np.array([(kepler_hamiltonian(s)-h0)/abs(h0) for s in rk])
    mp_e = np.array([(kepler_hamiltonian(s)-h0)/abs(h0) for s in mp])
    return t, rk, mp, rk_e, mp_e
