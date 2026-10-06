# v0.7 Real-Data Ingestion and Validation

Version 0.7 adds the infrastructure needed to move environmental navigation studies from synthetic Cartesian fields toward externally sourced geodetic products.

## What is new

- WGS-84 geodetic/ECEF/local-ENU coordinate transforms.
- Regular latitude/longitude field maps with interpolation.
- CSV and NPZ geodetic map ingestion in the base install.
- Optional NetCDF and GeoTIFF ingestion through the `geospatial` extra.
- Local-ENU wrappers so existing estimators can use geodetic maps without changing the fusion API.
- Illustrative sensor-grade profiles.
- Reproducible INS / gravity / magnetic / fused validation campaigns.
- Median, mean, standard deviation, and 95th-percentile error summaries.
- Map-error injection utilities for bias, scale error, and smooth spatial mismatch.

## Geodetic CSV format

A complete rectangular grid is represented as:

```text
lat_deg,lon_deg,value
33.0,-112.5,...
...
```

Load it with:

```python
from gravity_nav.geogrid import GeoGridMap, LocalENUFieldMap

grid = GeoGridMap.from_csv("gravity.csv", name="gravity", units="E")
field = LocalENUFieldMap(grid, ref_lat_deg=33.4484, ref_lon_deg=-112.0740)
```

The estimator still sees the same interface:

```python
field.value(x_m, y_m)
field.gradient(x_m, y_m)
```

## Optional formats

Install:

```bash
pip install -e ".[geospatial]"
```

Then use `GeoGridMap.from_netcdf(...)` or `GeoGridMap.from_geotiff(...)`.

## Validation workflow

For synthetic baseline maps:

```bash
qpnt validate configs/real_data_validation.yaml --runs 30 --profile tactical
```

For user-supplied geodetic maps:

```bash
qpnt validate-geodetic configs/real_data_validation.yaml \
  --gravity-map path/to/gravity.csv \
  --magnetic-map path/to/magnetic.csv \
  --ref-lat 33.4484 \
  --ref-lon -112.0740 \
  --runs 30 \
  --profile tactical
```

## Important scope statement

The two `phoenix_geodetic_*_demo.csv` files shipped with this repository contain **synthetic values on a real latitude/longitude coordinate grid**. They test the geodetic ingestion and validation pipeline; they are not measured gravity or magnetic survey products.

Users are responsible for licensing, datum interpretation, units, resolution, uncertainty, and provenance of any external geophysical data supplied to the suite.
