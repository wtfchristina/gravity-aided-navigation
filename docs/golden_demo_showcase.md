# Golden Demo Showcase Copy

## Website / GitHub short description

**Phoenix GNSS-Denied Golden Demo** is a reproducible trade-study scenario for the Gravity-Aided Navigation / Assured PNT platform. It compares INS-only, gravity-aided, magnetic-aided, and fused environmental navigation under the same modeled trajectory and sensor assumptions.

The demo packages the full chain from geodetic environmental-field maps through state estimation, Monte Carlo validation, reproducibility metadata, and presentation-ready results.

## LinkedIn draft

I packaged a fixed “golden demo” for my Assured PNT research platform so the same GNSS-denied scenario can be rerun, reviewed, and compared without changing the underlying assumptions.

The benchmark compares:

• INS only
• gravity-aided INS
• magnetic-aided INS
• fused gravity + magnetic aiding

The default scenario is a 600-second, roughly 50-km-class modeled mission using a tactical illustrative sensor profile and 30 Monte Carlo runs per mode.

The important part for me is reproducibility: the demo records configuration, raw runs, summary statistics, input-map hashes, a representative trajectory, and generated figures in one package.

The bundled field values are synthetic and are explicitly labeled that way. The same pipeline can ingest provenance-controlled public or customer geophysical maps for external validation.

This is research simulation — not flight-test or certified navigation performance — but it creates a stable baseline for engineering trade studies and future hardware/data integration.

#AssuredPNT #GPSDenied #Navigation #GNC #SensorFusion #Aerospace #ScientificComputing
