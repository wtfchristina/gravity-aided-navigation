# LinkedIn showcase draft — v0.5

I just pushed the next iteration of my gravity-aided Assured PNT research demonstrator.

Version 0.5 moves the project beyond offline simulation and into software/hardware-in-the-loop integration testing.

The new integration layer adds:

- timestamped, transport-neutral sensor packets
- JSONL record/replay for reproducible test cases
- UDP streaming for simulator or laboratory integration
- configurable latency, jitter, and packet-loss injection
- stale-measurement rejection
- packet-level estimator traces and link metrics

The design goal is separation of concerns: the navigation filter should not care whether a gravity, magnetic, or inertial observation came from a synthetic simulation, a replay log, a network socket, or a future hardware adapter.

That turns the project from a navigation algorithm demo into the beginnings of an integration and test environment for Assured PNT architectures.

All current performance results remain synthetic research simulations, not flight-test claims.

#AssuredPNT #GNC #SensorFusion #Navigation #Aerospace #Simulation #EmbeddedSystems #Python
