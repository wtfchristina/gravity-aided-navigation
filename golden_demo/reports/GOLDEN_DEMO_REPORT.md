# Phoenix GNSS-Denied Golden Demo

> Reproducible research simulation. Bundled environmental-field values are synthetic on a real geodetic grid. These results are not flight-test, hardware-validation, or certified-navigation claims.

## Mission

- Duration: 600 s
- Representative distance: 51.2 km
- Sensor profile: tactical
- Monte Carlo runs per mode: 30
- Reference origin: 33.4484, -112.0740

## Headline result

Median terminal error fell from **4,053 m (INS-only)** to **258 m (fused)** in this modeled scenario — a **93.6% reduction**.

## Mode comparison

| mode     |   runs |   terminal_median_m |   terminal_p95_m |   terminal_mean_m |   terminal_std_m |   rmse_median_m |   rmse_p95_m |
|:---------|-------:|--------------------:|-----------------:|------------------:|-----------------:|----------------:|-------------:|
| magnetic |     30 |             240.659 |          673.951 |           297.147 |          200.394 |         368.002 |      508.645 |
| fused    |     30 |             257.626 |          519.306 |           268.756 |          185.619 |         335.365 |      445.914 |
| gravity  |     30 |            1344.96  |         3875.06  |          1674.3   |         1268.65  |         857.01  |     1940.05  |
| ins      |     30 |            4053.21  |         9068.47  |          4468.25  |         2263.29  |        1779     |     3924.3   |

## Representative fused run

- INS terminal error: 3,937.9 m
- Fused terminal error: 36.5 m
- Fused terminal improvement: 99.1%
- Gravity updates accepted: 301
- Magnetic updates accepted: 601

## Reproducibility

- Gravity-map SHA-256: `eb73b9ae89f3e8378a3d0846d1a2ae19605e05d894ac23b20c5f210419995c85`
- Magnetic-map SHA-256: `a5e535e69e2f5617b5eff7f10f576991ce0a8f6359e746aaa5badb63e47f8134`
- Fixed scenario configuration is stored in `golden_demo/golden_demo.yaml`.
- Raw Monte Carlo runs, summary CSV, representative trajectory, metadata, and figures are packaged with the demo.

## Interpretation

The demo is designed to answer a trade-study question: under the same trajectory and inertial realization policy, how do INS-only, gravity-aided, magnetic-aided, and fused solutions compare?

The bundled maps are deliberately synthetic so the demo is fully redistributable and runnable without third-party data licenses. For external validation, replace them with provenance-controlled EGM2008, WMM/anomaly products, or customer-supplied maps using the public-data workflow already included in the repository.

## Limitations

- Synthetic environmental-field values do not establish real-world map observability.
- Sensor profiles are illustrative modeling assumptions, not hardware specifications.
- No flight test, hardware-in-the-loop certification, or safety-of-life claim is made.
- WMM main-field data alone may not provide the spatial anomaly content needed for all magnetic map-matching missions.