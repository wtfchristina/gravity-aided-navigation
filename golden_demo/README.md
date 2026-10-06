# Phoenix GNSS-Denied Golden Demo

This is the repository's fixed, presentation-ready reference scenario.

It compares four modes over the same modeled mission:

1. INS only
2. Gravity-aided INS
3. Magnetic-aided INS
4. Fused gravity + magnetic aiding

## One-command run

```bash
PYTHONPATH=src python scripts/run_golden_demo.py
```

Outputs are written to:

- `golden_demo/results/`
- `golden_demo/figures/`
- `golden_demo/reports/GOLDEN_DEMO_REPORT.md`

## Default scenario

- 600 s GNSS-denied mission
- ~50 km class trajectory
- tactical illustrative sensor profile
- 30 Monte Carlo runs per mode
- fixed Phoenix-area geodetic reference origin
- reproducible seeds

## Data status

The bundled gravity and magnetic values are **synthetic fields encoded on a real geodetic grid**. They make the demo self-contained and redistributable.

For a public-data or customer-data benchmark, replace the two CSV inputs with provenance-controlled maps using the repository's existing `benchmark/` workflow.

## Why this demo exists

The goal is not to claim operational navigation performance. The goal is to provide a stable reference scenario that a reviewer, customer, or integration partner can run and use to inspect:

- estimator behavior,
- mode-to-mode performance,
- reproducibility,
- data contracts,
- integration surfaces, and
- the path from simulation to real-data validation.
