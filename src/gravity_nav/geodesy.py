from __future__ import annotations
import math
import numpy as np

WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)


def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float = 0.0) -> np.ndarray:
    lat = math.radians(lat_deg); lon = math.radians(lon_deg)
    s = math.sin(lat); c = math.cos(lat)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * s * s)
    return np.array([(n + alt_m) * c * math.cos(lon),
                     (n + alt_m) * c * math.sin(lon),
                     (n * (1.0 - WGS84_E2) + alt_m) * s], dtype=float)


def ecef_to_enu(xyz: np.ndarray, ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float = 0.0) -> np.ndarray:
    p = np.asarray(xyz, dtype=float)
    ref = geodetic_to_ecef(ref_lat_deg, ref_lon_deg, ref_alt_m)
    d = p - ref
    lat = math.radians(ref_lat_deg); lon = math.radians(ref_lon_deg)
    sl, cl = math.sin(lat), math.cos(lat)
    so, co = math.sin(lon), math.cos(lon)
    r = np.array([[-so, co, 0.0], [-sl*co, -sl*so, cl], [cl*co, cl*so, sl]])
    return r @ d


def geodetic_to_enu(lat_deg: float, lon_deg: float, alt_m: float,
                    ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float = 0.0) -> np.ndarray:
    return ecef_to_enu(geodetic_to_ecef(lat_deg, lon_deg, alt_m), ref_lat_deg, ref_lon_deg, ref_alt_m)


def enu_to_geodetic(e_m: float, n_m: float, u_m: float,
                    ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float = 0.0) -> tuple[float,float,float]:
    lat = math.radians(ref_lat_deg); lon = math.radians(ref_lon_deg)
    sl, cl = math.sin(lat), math.cos(lat)
    so, co = math.sin(lon), math.cos(lon)
    r = np.array([[-so, -sl*co, cl*co], [co, -sl*so, cl*so], [0.0, cl, sl]])
    xyz = geodetic_to_ecef(ref_lat_deg, ref_lon_deg, ref_alt_m) + r @ np.array([e_m,n_m,u_m],dtype=float)
    x,y,z = xyz
    lon2 = math.atan2(y,x)
    p = math.hypot(x,y)
    lat2 = math.atan2(z, p*(1-WGS84_E2))
    alt = 0.0
    for _ in range(8):
        s=math.sin(lat2); nrad=WGS84_A/math.sqrt(1-WGS84_E2*s*s)
        alt = p/max(math.cos(lat2),1e-15)-nrad
        lat2 = math.atan2(z, p*(1-WGS84_E2*nrad/(nrad+alt)))
    return math.degrees(lat2), math.degrees(lon2), float(alt)
