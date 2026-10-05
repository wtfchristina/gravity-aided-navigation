import numpy as np
from gravity_nav.gravity_map import SyntheticGravityMap
from gravity_nav.observability import scalar_information

def test_observability_nonnegative():
    g=SyntheticGravityMap(); x=np.array([1000.,2000.]); y=np.array([0.,100.])
    info=scalar_information(g,2.0,x,y)
    assert np.all(info>=0)
