import numpy as np
from gravity_nav.symplectic import benchmark


def test_symplectic_benchmark_returns_finite_energy_errors():
    _, _, _, rk_e, mp_e = benchmark(duration_s=400.0, dt=20.0)
    assert np.all(np.isfinite(rk_e))
    assert np.all(np.isfinite(mp_e))
