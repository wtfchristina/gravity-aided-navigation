import numpy as np
from gravity_nav.gravity_map import SyntheticGravityMap


def test_gradient_matches_finite_difference():
    m = SyntheticGravityMap()
    x, y = 12_345.0, 2_345.0
    h = 1.0
    gx_fd = (m.value(x+h, y) - m.value(x-h, y)) / (2*h)
    gy_fd = (m.value(x, y+h) - m.value(x, y-h)) / (2*h)
    g = m.gradient(x, y)
    assert np.allclose(g, [gx_fd, gy_fd], rtol=1e-4, atol=1e-6)
