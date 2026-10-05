# Commercial Overview

## Positioning

**RelativisticQ-PNT Assured PNT Trade Study Suite** is an engineering analysis framework for evaluating passive and alternative navigation architectures when GNSS is degraded or unavailable.

The current public demonstrator focuses on gravity and magnetic map aiding, Monte Carlo robustness, observability, sensor trade studies, and reproducible reporting.

## Candidate product tiers

### Core
- scenario execution
- dynamics and INS propagation
- environmental field abstractions
- map matching and fusion
- configuration-driven CLI

### Analyst
- Monte Carlo campaigns
- sensor requirements sweeps
- observability maps
- comparative architecture scoring
- automated engineering reports
- scenario library

### Integrator
- customer map adapters
- proprietary sensor plugins
- streaming APIs
- HIL/SIL adapters
- ROS 2 / gRPC / UDP interfaces
- embedded target profiling
- customer-specific models and support

## Commercial differentiation to build next

1. Full 6-DOF Earth-referenced navigation and error-state filtering.
2. Real geodetic/gravity/magnetic map adapters with provenance and metadata.
3. Time synchronization, sensor latency, dropouts, integrity monitoring, and fault injection.
4. Mission requirement solver: determine sensor performance required to satisfy an error bound.
5. HIL/SIL streaming adapter layer.
6. Repeatable embedded benchmark harness.
7. Signed scenario/report artifacts and requirements traceability.

## Validation principle

Commercial claims should remain tied to reproducible configurations and clearly separate:

- synthetic simulation performance
- software-in-the-loop results
- hardware-in-the-loop results
- field/flight-test results

The current repository contains only synthetic simulation results.
