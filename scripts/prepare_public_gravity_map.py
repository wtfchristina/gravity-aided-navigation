#!/usr/bin/env python3
import argparse
from pathlib import Path
from gravity_nav.public_data import normalize_geodetic_grid
p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('--lat-column',default='lat_deg'); p.add_argument('--lon-column',default='lon_deg'); p.add_argument('--value-column',default='value'); p.add_argument('--out',default='benchmark/data/egm2008_region.csv'); a=p.parse_args()
df=normalize_geodetic_grid(a.input,lat_column=a.lat_column,lon_column=a.lon_column,value_column=a.value_column)
Path(a.out).parent.mkdir(parents=True,exist_ok=True); df.to_csv(a.out,index=False); print(f'wrote {len(df)} normalized rows to {a.out}')
