# LinkedIn Showcase Draft — v0.3

I expanded my gravity-aided navigation project into a broader **Assured PNT Trade Study Suite**.

The original project asked whether a mapped gravity field could constrain inertial drift after GNSS loss. Version 0.3 turns that idea into a modular engineering analysis framework that can compare multiple passive navigation architectures under the same simulated mission conditions.

The new release includes:

- INS-only, gravity-only, magnetic-only, and fused environmental navigation
- pluggable map-based sensor observations
- CSV/NPZ map ingestion
- Monte Carlo robustness campaigns
- sensor noise and update-rate trade studies
- environmental observability heatmaps
- automated engineering reports
- YAML-driven scenarios and a command-line interface
- cold-atom gravity-gradient and symplectic dynamics research modules

In the default synthetic Monte Carlo campaign, fused gravity + magnetic aiding produced substantially lower terminal-error and RMSE distributions than unaided INS. These are simulation results only—not flight-test or operational performance claims.

The part I find most useful is the trade-study layer: instead of asking whether a sensor "works," the software lets you ask what measurement noise, map structure, update rate, and estimator configuration are required to meet a navigation objective.

The next commercial steps are full 6-DOF navigation, validated environmental map adapters, integrity/fault monitoring, and HIL/SIL interfaces.

GitHub: https://github.com/wtfchristina/gravity-aided-navigation
Website: https://www.qpnt.us

#AssuredPNT #GPSDenied #Navigation #GNC #SensorFusion #KalmanFilter #QuantumSensing #Aerospace #ScientificComputing
