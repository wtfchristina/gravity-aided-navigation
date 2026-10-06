from __future__ import annotations
import numpy as np
from .geogrid import GeoGridMap, LocalENUFieldMap

# A deterministic geodetic-format DEMONSTRATION field. It is deliberately synthetic.
# It exists to exercise lat/lon ingestion and local-frame interpolation without redistributing third-party data.
def synthetic_geodetic_field(ref_lat=33.4484,ref_lon=-112.0740,span_deg=0.8,n=181,name='gravity_demo',units='arb'):
    lats=np.linspace(ref_lat-span_deg/2,ref_lat+span_deg/2,n)
    lons=np.linspace(ref_lon-span_deg/2,ref_lon+span_deg/2,n)
    lo,la=np.meshgrid(lons,lats)
    x=(lo-ref_lon)*np.cos(np.deg2rad(ref_lat))*111320.0
    y=(la-ref_lat)*110540.0
    vals=(22*np.exp(-((x-12000)**2+(y+5000)**2)/(2*9000**2))
          -18*np.exp(-((x+15000)**2+(y-9000)**2)/(2*12000**2))
          +8*np.sin(x/7000)*np.cos(y/9500))
    return GeoGridMap(lats,lons,vals,name=name,units=units)

def local_demo_map(ref_lat=33.4484,ref_lon=-112.0740):
    return LocalENUFieldMap(synthetic_geodetic_field(ref_lat,ref_lon),ref_lat,ref_lon)
