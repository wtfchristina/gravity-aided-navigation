# Changelog

## 0.6.0

- Added Sensor Adapter SDK with mapping, canonical JSON, and reference IMU adapters.
- Added third-party adapter discovery through Python entry points.
- Added optional authenticated gRPC SensorPacket gateway and client.
- Added optional TLS configuration for the gRPC reference transport.
- Added protobuf service contract under `proto/sensor_gateway.proto`.
- Added optional ROS 2 gateway and synthetic publisher bridge.
- Added Integration SDK tab to the Streamlit demonstrator.
- Expanded CI to Python 3.10-3.12 with integration dependencies.
- Added adapter, ROS 2 serialization, gRPC delivery, and auth tests.
- All integration features remain research/engineering references, not certified avionics interfaces.

## 0.5.0 - SIL/HIL Integration Layer

- Added transport-neutral timestamped `SensorPacket` messages.
- Added JSONL sensor-log generation, record, and replay.
- Added UDP publisher and recorder interfaces for lab/simulator integration.
- Added deterministic latency, jitter, and packet-dropout injection.
- Added estimator-gateway stale-data rejection and packet-level traces.
- Added offline SIL/HIL demonstration metrics including mean/p95 latency and delivery percentage.
- Added Streamlit SIL/HIL integration tab.
- Added packet-schema, integration, commercial-value, and LinkedIn showcase documentation.
- Added sample replay log and HIL demo outputs.
- Expanded test suite to 22 passing tests.

## 0.2.0

- Added a synthetic gravity-gradient tensor model (`Txx`, `Txy`, `Tyy`, `Tzz`).
- Added a simplified cold-atom gravity gradiometer phase model.
- Added a cold-atom/Tzz-aided EKF navigation simulation.
- Added a structure-preserving Kepler benchmark comparing RK4 and implicit midpoint integration.
- Expanded the Streamlit demonstrator, figures, tests, and technical documentation.
- Added GitHub Actions CI and project contribution files.

## 0.1.0

- Initial gravity-aided INS + scalar-map EKF demonstrator.

## 0.3.0 - Assured PNT Trade Study Suite

- Added multi-modal gravity + magnetic environmental navigation fusion.
- Added generic scalar-field observation interface and gated fusion EKF.
- Added CSV/NPZ regular-grid map ingestion.
- Added configuration-driven scenarios and `qpnt` CLI.
- Added Monte Carlo campaign analysis and 95th-percentile metrics.
- Added sensor noise/update-rate trade studies.
- Added local observability scoring and heatmap generation.
- Added Markdown/HTML engineering report generation.
- Added productization and API documentation.

## 0.4.0

- Added mission-level navigation requirements and Monte Carlo compliance evaluation.
- Added sensor requirement solver for gravity noise, magnetic noise, and update-rate trade spaces.
- Added mission-envelope studies across outage duration and vehicle speed.
- Added integrity-analysis research proxies including alert-limit monitoring, empirical availability, and HMI-like proxy rate.
- Added `qpnt requirements`, `qpnt integrity`, and `qpnt mission-envelope` commands.
- Added Streamlit mission-requirements and integrity tab.
- Added documentation for requirements engineering, integrity screening, and commercial decision-support positioning.
- Expanded test suite to 17 passing tests.
