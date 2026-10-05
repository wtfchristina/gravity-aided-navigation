import numpy as np
import pandas as pd
from gravity_nav.grid_map import GridFieldMap

def test_grid_csv_roundtrip(tmp_path):
    x=np.array([0.,10.,20.]); y=np.array([0.,5.]); values=np.add.outer(y,x)
    m=GridFieldMap(x,y,values)
    p=tmp_path/"map.csv"; m.to_csv(p)
    m2=GridFieldMap.from_csv(p)
    assert abs(m2.value(10,5)-15)<1e-9
