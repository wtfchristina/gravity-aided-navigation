import numpy as np
from gravity_nav.geodesy import geodetic_to_enu, enu_to_geodetic

def test_geodetic_enu_roundtrip():
    ref=(33.4484,-112.0740,340.0)
    p=(33.51,-111.98,500.0)
    enu=geodetic_to_enu(*p,*ref)
    got=enu_to_geodetic(*enu,*ref)
    assert np.allclose(got,p,atol=2e-6)
