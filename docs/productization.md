# Productization Roadmap

Version 0.3 introduces a trade-study layer around the original gravity-aided navigation demonstrator. The package is still research software, but the architecture is deliberately moving toward a commercial evaluation product.

## Current product-facing capabilities

- configuration-driven scenarios
- INS-only, gravity-only, magnetic-only, and fused modes
- pluggable scalar environmental field updates
- innovation gating
- CSV/NPZ regular-grid map ingestion
- Monte Carlo campaigns
- sensor trade-space sweeps
- local observability scoring
- reproducible CSV/JSON outputs
- generated Markdown/HTML engineering reports
- CLI workflows suitable for CI and batch analysis

## Commercial path

### Core
Dynamics, sensor models, map matching, state estimation, scenario execution.

### Analyst
Monte Carlo campaigns, observability maps, sensor requirements sweeps, report generation, scenario libraries.

### Integrator
Customer sensor adapters, real map products, streaming interfaces, hardware-in-the-loop, ROS 2/gRPC/UDP adapters, embedded performance profiling.

## Important gaps before operational use

- full 6-DOF Earth-referenced navigation
- attitude/gyro error-state estimation
- validated geophysical data products
- integrity monitoring and fault detection
- sensor time synchronization and transport delays
- formal V&V, requirements traceability, and safety assurance
- HIL/SIL qualification and embedded target benchmarking
- licensing, support, security update, and data-handling policies
