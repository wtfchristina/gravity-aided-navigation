# v0.3 API Overview

## Scenario
`AssuredPNTConfig` configures a fixed-wing synthetic scenario and selects `ins`, `gravity`, `magnetic`, or `fused` aiding.

## Environmental fields
Any scalar field implementing:

```python
value(x, y)
gradient(x, y)
```

can be passed to the fusion estimator. `GridFieldMap` loads customer-style regular-grid CSV or NPZ maps.

## Fusion
`FusionEKF.update(FieldObservation(...))` accepts arbitrary scalar environmental observations and optional innovation gating.

## Analysis
- `run_campaign` / `summarize_campaign`: Monte Carlo evaluation
- `sensor_trade_study`: sensor noise and update-rate sweeps
- `scalar_information` / `combined_information`: local observability proxy
- `write_report`: Markdown and HTML report generation
