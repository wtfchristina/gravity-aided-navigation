from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from .geodesy import enu_to_geodetic

@dataclass
class GeoGridMap:
    lat_deg: np.ndarray
    lon_deg: np.ndarray
    values: np.ndarray
    name: str = 'field'
    units: str = 'arb'

    def __post_init__(self):
        self.lat_deg=np.asarray(self.lat_deg,float); self.lon_deg=np.asarray(self.lon_deg,float); self.values=np.asarray(self.values,float)
        if self.values.shape != (len(self.lat_deg),len(self.lon_deg)):
            raise ValueError('values must have shape (len(lat_deg), len(lon_deg))')
        self._interp=RegularGridInterpolator((self.lat_deg,self.lon_deg),self.values,bounds_error=False,fill_value=np.nan)

    @classmethod
    def from_csv(cls,path,name='field',units='arb'):
        df=pd.read_csv(path); required={'lat_deg','lon_deg','value'}
        if not required.issubset(df.columns): raise ValueError(f'CSV must contain {sorted(required)}')
        lats=np.sort(df.lat_deg.unique()); lons=np.sort(df.lon_deg.unique())
        piv=df.pivot(index='lat_deg',columns='lon_deg',values='value').reindex(index=lats,columns=lons)
        if piv.isna().any().any(): raise ValueError('CSV must define a complete rectangular geodetic grid')
        return cls(lats,lons,piv.to_numpy(),name,units)

    @classmethod
    def from_npz(cls,path,name='field',units='arb'):
        d=np.load(path); return cls(d['lat_deg'],d['lon_deg'],d['value'],name,units)

    @classmethod
    def from_netcdf(cls,path,value_var,lat_var='lat',lon_var='lon',name='field',units='arb'):
        try: import xarray as xr
        except ImportError as e: raise ImportError('Install the geospatial extra: pip install .[geospatial]') from e
        ds=xr.open_dataset(path); da=ds[value_var]
        vals=np.asarray(da.transpose(lat_var,lon_var).values,float)
        return cls(np.asarray(ds[lat_var].values,float),np.asarray(ds[lon_var].values,float),vals,name,units)

    @classmethod
    def from_geotiff(cls,path,name='field',units='arb',band=1):
        try:
            import rasterio
            from rasterio.warp import transform_bounds
        except ImportError as e: raise ImportError('Install the geospatial extra: pip install .[geospatial]') from e
        with rasterio.open(path) as src:
            arr=src.read(band).astype(float)
            if src.nodata is not None: arr[arr==src.nodata]=np.nan
            b=transform_bounds(src.crs,'EPSG:4326',*src.bounds,densify_pts=21)
            lons=np.linspace(b[0],b[2],src.width); lats=np.linspace(b[3],b[1],src.height)
            if lats[0]>lats[-1]: lats=lats[::-1]; arr=arr[::-1,:]
        return cls(lats,lons,arr,name,units)

    def value_geodetic(self,lat_deg,lon_deg):
        la=np.asarray(lat_deg,float); lo=np.asarray(lon_deg,float); shape=np.broadcast(la,lo).shape
        pts=np.column_stack([np.broadcast_to(la,shape).ravel(),np.broadcast_to(lo,shape).ravel()])
        out=self._interp(pts).reshape(shape); return float(out) if shape==() else out

    def to_csv(self,path):
        lo,la=np.meshgrid(self.lon_deg,self.lat_deg)
        pd.DataFrame({'lat_deg':la.ravel(),'lon_deg':lo.ravel(),'value':self.values.ravel()}).to_csv(path,index=False)

@dataclass
class LocalENUFieldMap:
    geogrid: GeoGridMap
    ref_lat_deg: float
    ref_lon_deg: float
    ref_alt_m: float = 0.0
    gradient_step_m: float = 25.0

    @property
    def name(self): return self.geogrid.name
    @property
    def units(self): return self.geogrid.units

    def value(self,x_m,y_m):
        xa=np.asarray(x_m,float); ya=np.asarray(y_m,float); shape=np.broadcast(xa,ya).shape
        out=np.empty(shape if shape else (),dtype=float)
        bx=np.broadcast_to(xa,shape).ravel(); by=np.broadcast_to(ya,shape).ravel(); vals=[]
        for x,y in zip(bx,by):
            lat,lon,_=enu_to_geodetic(float(x),float(y),0.0,self.ref_lat_deg,self.ref_lon_deg,self.ref_alt_m)
            vals.append(self.geogrid.value_geodetic(lat,lon))
        arr=np.asarray(vals).reshape(shape)
        return float(arr) if shape==() else arr

    def gradient(self,x:float,y:float,step_m:float|None=None):
        h=float(step_m or self.gradient_step_m)
        return np.array([(self.value(x+h,y)-self.value(x-h,y))/(2*h),(self.value(x,y+h)-self.value(x,y-h))/(2*h)],float)
