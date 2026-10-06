import pandas as pd
from gravity_nav.public_data import normalize_geodetic_grid, DataProvenance

def test_normalize_csv(tmp_path):
    p=tmp_path/'x.csv'; pd.DataFrame({'lat':[1,1,2,2],'lon':[3,4,3,4],'v':[5,6,7,8]}).to_csv(p,index=False)
    d=normalize_geodetic_grid(p,lat_column='lat',lon_column='lon',value_column='v')
    assert list(d.columns)==['lat_deg','lon_deg','value'] and len(d)==4

def test_provenance_dict():
    x=DataProvenance('p','q','u',sha256='abc').to_dict(); assert x['product']=='q' and x['sha256']=='abc'
