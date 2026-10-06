# Public Benchmark Methodology

The public benchmark uses identical trajectory, sensor profile, and random-seed policy across INS-only, gravity-aided, magnetic-aided, and fused modes. Each mode is evaluated across multiple Monte Carlo seeds. Primary outputs are median and 95th-percentile terminal error and RMS position error.

## Data provenance

The gravity reference is intended to come from NGA EGM2008 or a user-authorized derivative/crop. The magnetic reference is fetched from NOAA's WMM2025 calculator/API after user registration. Input files are hashed with SHA-256 and recorded in `provenance.json`.

## Interpretation limits

Reference-field products are not equivalent to local survey truth, and model-derived navigation results are not hardware or flight validation. WMM is a global main-field model; anomaly-navigation studies should consider appropriate high-resolution crustal/anomaly products where available.
