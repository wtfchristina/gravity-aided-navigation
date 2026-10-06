#!/usr/bin/env python3
import argparse
from pathlib import Path
from gravity_nav.public_data import fetch_noaa_wmm_grid
p=argparse.ArgumentParser(); p.add_argument('--lat-min',type=float,required=True); p.add_argument('--lat-max',type=float,required=True); p.add_argument('--lon-min',type=float,required=True); p.add_argument('--lon-max',type=float,required=True); p.add_argument('--step',type=float,default=.05); p.add_argument('--component',default='f'); p.add_argument('--year',type=int,default=2026); p.add_argument('--month',type=int,default=10); p.add_argument('--day',type=int,default=5); p.add_argument('--out',default='benchmark/data/wmm2025.csv'); a=p.parse_args()
df=fetch_noaa_wmm_grid(lat_min=a.lat_min,lat_max=a.lat_max,lon_min=a.lon_min,lon_max=a.lon_max,step_deg=a.step,component=a.component,year=a.year,month=a.month,day=a.day)
Path(a.out).parent.mkdir(parents=True,exist_ok=True); df.to_csv(a.out,index=False); print(f'wrote {len(df)} rows to {a.out}')
