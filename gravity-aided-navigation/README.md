# Gravity-Aided Navigation for GPS-Denied Systems

**A RelativisticQ-PNT Research Demonstrator**

This project demonstrates a simulated gravity-aided navigation architecture for an autonomous platform operating without GNSS.

A noisy inertial navigation solution is fused with synthetic gravity-gradient observations using an Extended Kalman Filter (EKF). The measurements are matched against a differentiable reference gravity field to constrain accumulated inertial drift.

> **Scope:** This repository is a research simulation. Results are synthetic and do not represent flight-test or operational hardware performance.

## Why this project?

GNSS-denied navigation needs external references that do not depend on satellite RF signals. Gravity-aided navigation is one candidate: spatial variations in Earth's gravity field can provide environmental observables that are independent of GNSS.

This repository focuses on the software side of that problem:

**Physics -> Sensing -> Estimation -> Navigation**

## Architecture

```text
                 GPS DENIED
                     |
                     v
               +-----------+
               |    IMU    |
               +-----+-----+
                     |
                     v
              INS PROPAGATION
                     |
                     v
               +-----------+        Reference
               |    EKF    | <----- Gravity Map
               +-----+-----+
                     ^
                     |
          Gravity-Gradient Sensor
                     |
                     v
              z = h(x, y) + noise
                     |
                     v
             CORRECTED NAVIGATION
```

## What the simulation includes

- Planar truth trajectory across ~50 km
- Accelerometer noise and time-varying bias
- INS-only dead reckoning
- Synthetic spatial gravity-gradient field
- Noisy gravity measurements at a lower update rate
- Nonlinear EKF map matching
- Reproducible metrics and plots
- Interactive Streamlit demo
- Unit tests

## Example results

Run:

```bash
python scripts/generate_figures.py
```

The script generates:

- `figures/trajectory_comparison.png`
- `figures/position_error.png`
- `figures/gravity_map.png`

Results are generated from the simulation rather than hard-coded.

## Quick start

```bash
git clone https://github.com/wtfchristina/gravity-aided-navigation.git
cd gravity-aided-navigation
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e .
python scripts/run_simulation.py
python scripts/generate_figures.py
```

Run the interactive demo:

```bash
pip install streamlit
streamlit run app.py
```

Run tests:

```bash
pip install pytest
pytest -q
```

## Core estimator state

```text
x = [position_x,
     position_y,
     velocity_x,
     velocity_y,
     accel_bias_x,
     accel_bias_y]
```

The gravity observation is modeled as:

```text
z_k = h(position_x, position_y) + measurement_noise
```

The EKF uses the map gradient to convert a field mismatch into a position correction.

## Research roadmap

### Phase 1 - Gravity-aided INS
Synthetic gravity field + INS + EKF. **This release.**

### Phase 2 - Gravity-gradient tensor
Extend the observation model to multiple tensor components such as `Txx`, `Txy`, and `Tzz`.

### Phase 3 - Cold-atom sensor model
Add matter-wave phase observations, interrogation time, sensor dead time, phase noise, and vibration sensitivity.

### Phase 4 - Structure-preserving dynamics
Add a separate Hamiltonian propagation benchmark comparing RK methods with implicit-midpoint symplectic integration.

### Phase 5 - High-fidelity Earth model
Replace the synthetic field with public gravity/geopotential data and move toward 3D Earth-referenced navigation.

## Limitations

The current implementation intentionally uses simplified planar dynamics and a synthetic field. It does **not** model full 6-DOF strapdown INS, a flight-qualified cold-atom sensor, validated operational gravity-map accuracy, or real-world environmental disturbances.

See [`docs/methodology.md`](docs/methodology.md) for details.

## Author

**Christina Holt**  
RelativisticQ-PNT  
GitHub: [@wtfchristina](https://github.com/wtfchristina)

## License

MIT
