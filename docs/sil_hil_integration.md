# SIL/HIL Integration Guide

Version 0.5 adds an integration boundary between sensor data sources and the navigation estimator. The goal is to make the research stack useful in software-in-the-loop (SIL), processor-in-the-loop, and early hardware-in-the-loop (HIL) workflows without coupling the core filter to a specific transport.

## Integration architecture

```text
sensor simulator / hardware / recorded data
                |
                v
        transport adapter
       UDP | JSONL | custom
                |
                v
          SensorPacket
                |
                v
       NavigationGateway
                |
                v
          FusionEKF core
                |
                v
      navigation state + trace
```

`NavigationGateway` is deliberately transport-neutral. A future ROS 2, gRPC, serial, CAN, or vendor SDK adapter only needs to convert the incoming observation into the documented packet object.

## Demonstration packet types

- `imu`: `ax_mps2`, `ay_mps2`, `dt_s`
- `gravity`: `measurement`, `noise_std`
- `magnetic`: `measurement`, `noise_std`
- `truth_reference`: scoring-only x/y/vx/vy values; never used as a navigation measurement

## Timing

`timestamp_s` is sensor/scenario time. UDP arrival time is intentionally separate. This allows experiments with transport latency and out-of-order delivery while retaining the original observation time.

## Link impairments

`LinkImpairmentConfig` supports:

- constant latency
- Gaussian timing jitter
- packet dropout probability
- deterministic seeding for reproducibility

The estimator gateway can reject measurements older than a configured staleness threshold.

## Safety and scope

The current transport layer is designed for laboratory integration and engineering evaluation. It is not a certified avionics bus implementation, does not provide cryptographic transport security, and should not be represented as flight-qualified software.
