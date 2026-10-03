import numpy as np
from gravity_nav.cold_atom import ColdAtomGradiometer, ColdAtomGradiometerConfig
from gravity_nav.gravity_tensor import SyntheticGravityTensorMap


def test_phase_gradient_round_trip():
    rng = np.random.default_rng(1)
    cfg = ColdAtomGradiometerConfig(phase_noise_std_rad=0.0, vibration_phase_std_rad=0.0)
    sensor = ColdAtomGradiometer(SyntheticGravityTensorMap(), cfg, rng)
    for gradient in [-80.0, -5.0, 0.0, 12.5, 100.0]:
        assert np.isclose(sensor.phase_to_gradient(sensor.gradient_to_phase(gradient)), gradient)
