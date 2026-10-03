# Architecture

```text
                       GNSS unavailable
                              |
                              v
                    +------------------+
                    |  IMU / inertial  |
                    +--------+---------+
                             |
                             v
                      State propagation
                             |
            +----------------+----------------+
            |                                 |
            v                                 v
  Synthetic gravity tensor map      Cold-atom gradiometer
       Txx/Txy/Tyy/Tzz              DeltaPhi ~ k_eff Gamma L T^2
            |                                 |
            +----------------+----------------+
                             |
                             v
                   Extended Kalman Filter
                             |
                             v
                   Gravity-aided estimate
```

The repository intentionally separates the physical field, sensor, estimator, and numerical-propagation layers so each can be replaced independently as fidelity increases.
