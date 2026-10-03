import numpy as np
from gravity_nav.dynamics import propagate_truth


def test_constant_velocity_propagation():
    s = np.array([0.0, 0.0, 10.0, -2.0])
    out = propagate_truth(s, np.zeros(2), 3.0)
    assert np.allclose(out, [30.0, -6.0, 10.0, -2.0])
