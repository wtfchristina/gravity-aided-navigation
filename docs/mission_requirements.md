# Mission Requirements Solver

Version 0.4 adds a requirements-driven workflow around the existing environmental navigation simulator.

Instead of asking only *how did this sensor configuration perform?*, an analyst can ask:

> What gravity/magnetic sensor noise and update rate combinations satisfy a specified navigation error target for a GNSS outage?

The solver performs Monte Carlo sweeps and evaluates each candidate against:

- terminal position-error limit
- RMS position-error limit
- required empirical success probability
- alert-limit exceedance probability

Example:

```bash
qpnt requirements configs/mission_requirement.yaml --runs 25
```

The ranking includes a transparent `burden_score` used only to prefer less-demanding sensor/update assumptions among passing configurations. It is not a procurement-cost model.

All outputs are synthetic engineering-screening results, not certified requirements verification.
