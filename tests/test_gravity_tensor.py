import numpy as np
from gravity_nav.gravity_tensor import SyntheticGravityTensorMap


def test_tensor_trace_is_zero_by_construction():
    m = SyntheticGravityTensorMap()
    c = m.components(12345.0, 2345.0)
    assert abs(float(c["Txx"] + c["Tyy"] + c["Tzz"])) < 1e-10


def test_tzz_jacobian_matches_finite_difference():
    m = SyntheticGravityTensorMap()
    x, y, h = 18000.0, -1500.0, 5.0
    fd = np.array([
        (m.component("Tzz", x+h, y)-m.component("Tzz", x-h, y))/(2*h),
        (m.component("Tzz", x, y+h)-m.component("Tzz", x, y-h))/(2*h),
    ], dtype=float)
    assert np.allclose(m.jacobian_component("Tzz", x, y, h), fd, rtol=1e-6, atol=1e-10)
