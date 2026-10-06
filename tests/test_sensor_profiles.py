from gravity_nav.sensor_profiles import PROFILES, apply_profile
from gravity_nav.assured_pnt import AssuredPNTConfig

def test_profiles_apply():
    c=apply_profile(AssuredPNTConfig(),'tactical')
    assert c.accel_noise_std==PROFILES['tactical'].accel_noise_std
    assert len(PROFILES)>=4
