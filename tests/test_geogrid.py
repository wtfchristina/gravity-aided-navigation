import numpy as np
from gravity_nav.geogrid import GeoGridMap, LocalENUFieldMap
from gravity_nav.geodetic_demo import synthetic_geodetic_field

def test_geogrid_interpolation():
    g=GeoGridMap(np.array([0.,1.]),np.array([10.,11.]),np.array([[0.,1.],[2.,3.]]))
    assert abs(g.value_geodetic(.5,10.5)-1.5)<1e-12

def test_local_enu_wrapper_is_finite():
    g=synthetic_geodetic_field(n=31)
    m=LocalENUFieldMap(g,33.4484,-112.0740)
    assert np.isfinite(m.value(1000.,2000.))
    assert np.isfinite(m.gradient(1000.,2000.)).all()
