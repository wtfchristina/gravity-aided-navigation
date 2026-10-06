from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import csv, io, json, os, hashlib
import pandas as pd

NOAA_WMM_GRID_API = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateIgrfgrid"
NGA_EGM2008_PAGE = "https://earth-info.nga.mil/index.php?dir=wgs84&action=wgs84"
NGA_EGM2008_DOWNLOAD = "https://earth-info.nga.mil/php/download.php?file=egm-08interpolation"
NOAA_WMM_PAGE = "https://www.ncei.noaa.gov/products/world-magnetic-model"

@dataclass(frozen=True)
class DataProvenance:
    provider: str
    product: str
    source_url: str
    accessed_utc: str | None = None
    license_note: str | None = None
    sha256: str | None = None

    def to_dict(self): return asdict(self)


def sha256_file(path:str|Path)->str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def fetch_noaa_wmm_grid(*,lat_min:float,lat_max:float,lon_min:float,lon_max:float,step_deg:float,
                        component:str='f',model:str='WMM',year:int=2026,month:int=10,day:int=5,
                        api_key:str|None=None,timeout_s:float=60.0)->pd.DataFrame:
    """Fetch a NOAA geomagnetic grid and normalize it to lat_deg/lon_deg/value.

    NOAA requires API registration. Pass api_key or set NOAA_GEOMAG_API_KEY.
    This function intentionally performs no request when a key is absent.
    """
    key=api_key or os.getenv('NOAA_GEOMAG_API_KEY')
    if not key:
        raise RuntimeError('NOAA API key required. Register with NOAA NCEI and set NOAA_GEOMAG_API_KEY.')
    params=dict(lat1=lat_min,lat2=lat_max,lon1=lon_min,lon2=lon_max,
                latStepSize=step_deg,lonStepSize=step_deg,magneticComponent=component,
                model=model,startYear=year,startMonth=month,startDay=day,
                endYear=year,endMonth=month,endDay=day,dateStepSize=1,
                key=key,resultFormat='csv')
    url=NOAA_WMM_GRID_API+'?'+urlencode(params)
    with urlopen(url,timeout=timeout_s) as r:
        text=r.read().decode('utf-8-sig')
    raw=pd.read_csv(io.StringIO(text))
    # NOAA column names have changed over time; resolve common variants robustly.
    lower={str(c).strip().lower():c for c in raw.columns}
    lat_col=next((lower[k] for k in lower if 'latitude' in k or k=='lat'),None)
    lon_col=next((lower[k] for k in lower if 'longitude' in k or k in {'lon','lng'}),None)
    candidates=[c for c in raw.columns if str(c).strip().lower() in {component.lower(),'total intensity','f','x','y','z','h','d','i'}]
    if lat_col is None or lon_col is None or not candidates:
        raise ValueError(f'Unexpected NOAA CSV columns: {list(raw.columns)}')
    value_col=candidates[0]
    out=raw[[lat_col,lon_col,value_col]].rename(columns={lat_col:'lat_deg',lon_col:'lon_deg',value_col:'value'})
    return out.astype({'lat_deg':float,'lon_deg':float,'value':float})


def normalize_geodetic_grid(path:str|Path, *, value_column:str='value', lat_column:str='lat_deg', lon_column:str='lon_deg')->pd.DataFrame:
    """Normalize a user-acquired public field grid to the project CSV contract."""
    p=Path(path)
    if p.suffix.lower()=='.csv':
        df=pd.read_csv(p)
    elif p.suffix.lower() in {'.tif','.tiff'}:
        try: import rasterio
        except ImportError as e: raise ImportError('Install geospatial extra for GeoTIFF support') from e
        with rasterio.open(p) as src:
            if src.crs is None: raise ValueError('GeoTIFF must define a CRS')
            from rasterio.warp import transform
            arr=src.read(1)
            rows,cols=(arr.shape[0],arr.shape[1])
            rr,cc=__import__('numpy').indices((rows,cols))
            xs,ys=rasterio.transform.xy(src.transform,rr,cc)
            np=__import__('numpy'); xs=np.asarray(xs).ravel(); ys=np.asarray(ys).ravel(); vals=arr.ravel()
            if str(src.crs).upper()!='EPSG:4326':
                lons,lats=transform(src.crs,'EPSG:4326',xs.tolist(),ys.tolist())
            else: lons,lats=xs,ys
            df=pd.DataFrame({'lat_deg':lats,'lon_deg':lons,'value':vals})
            return df.dropna().reset_index(drop=True)
    else:
        raise ValueError('Supported inputs: CSV, GeoTIFF')
    required={lat_column,lon_column,value_column}
    if not required.issubset(df.columns): raise ValueError(f'Missing required columns {sorted(required)}')
    return df[[lat_column,lon_column,value_column]].rename(columns={lat_column:'lat_deg',lon_column:'lon_deg',value_column:'value'}).dropna().astype(float)


def write_provenance(path:str|Path, *items:DataProvenance, extra:dict|None=None):
    payload={'datasets':[x.to_dict() for x in items]}
    if extra: payload['benchmark']=extra
    Path(path).write_text(json.dumps(payload,indent=2),encoding='utf-8')
