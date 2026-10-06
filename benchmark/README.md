# Public-Data Benchmark Package

This package turns the v0.7 geodetic validation layer into a reproducible benchmark workflow using **authoritative public/reference geophysical products**.

## Reference products

- **Gravity:** NGA Earth Gravitational Model 2008 (EGM2008). The repository does not redistribute the full 128 MB interpolation product. Acquire it from NGA and export/crop the mission region to CSV or GeoTIFF, then normalize it with `scripts/prepare_public_gravity_map.py`.
- **Magnetic:** NOAA/NGA World Magnetic Model 2025 (WMM2025). NOAA requires registration for programmatic calculator access. Set `NOAA_GEOMAG_API_KEY` and use `scripts/fetch_wmm_grid.py`.

## Golden benchmark workflow

```bash
pip install -e .[geospatial]

# 1) Acquire/crop EGM2008 from NGA, then normalize
python scripts/prepare_public_gravity_map.py path/to/egm2008_region.csv \
  --lat-column lat_deg --lon-column lon_deg --value-column value \
  --out benchmark/data/egm2008_region.csv

# 2) Fetch WMM2025 field grid from NOAA after API registration
export NOAA_GEOMAG_API_KEY='YOUR_KEY'
python scripts/fetch_wmm_grid.py \
  --lat-min 33.0 --lat-max 33.9 --lon-min -112.7 --lon-max -111.6 \
  --step 0.05 --component f --out benchmark/data/wmm2025.csv

# 3) Run 30-run/mode benchmark
python scripts/run_public_benchmark.py \
  --gravity benchmark/data/egm2008_region.csv \
  --magnetic benchmark/data/wmm2025.csv \
  --runs 30 --profile tactical

# 4) Generate benchmark figures
python scripts/generate_public_benchmark_figures.py
```

## Reproducibility

Every golden run writes raw Monte Carlo results, a summary CSV, benchmark metadata, SHA-256 hashes of input maps, and a provenance manifest. The report explicitly separates simulation outputs from hardware/flight-test claims.

## Important scientific caveat

WMM2025 is primarily a global main-field model. For anomaly-aided magnetic navigation, high-resolution crustal/anomaly products may be more informative than WMM alone. The WMM benchmark here validates the **public-data ingestion and reproducibility pipeline**, not a claim that WMM total intensity is sufficient for every map-matching mission.
