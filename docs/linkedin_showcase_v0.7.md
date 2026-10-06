# LinkedIn showcase draft — v0.7

I just extended my gravity-aided navigation project with a v0.7 geodetic-data and validation layer.

The original demonstrator focused on whether passive environmental fields could constrain INS drift during GNSS outages. The new version is built around a more practical engineering question:

**Can the same estimator and trade-study stack ingest externally sourced geophysical maps and produce reproducible validation statistics?**

v0.7 adds:

- WGS-84 geodetic / ECEF / local-ENU transformations
- latitude/longitude grid ingestion
- CSV / NPZ support, with optional NetCDF and GeoTIFF adapters
- customer/public map wrappers for the existing EKF
- sensor-grade profile studies
- multi-run INS / gravity / magnetic / fused validation
- median and 95th-percentile navigation-error reporting
- map-error perturbation tools

The bundled geodetic files use synthetic values and are clearly labeled as such; the point is to provide a reproducible pipeline into which externally licensed or proprietary gravity and magnetic products can be inserted.

For me, this is an important transition from "a navigation simulation" toward a platform for mission-specific Assured PNT evaluation.

#AssuredPNT #GPSDenied #GNC #Navigation #SensorFusion #Aerospace #ScientificComputing
