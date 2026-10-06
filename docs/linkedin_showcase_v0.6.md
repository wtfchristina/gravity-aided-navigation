# LinkedIn showcase draft — v0.6

I just pushed another step forward on my Gravity-Aided Navigation / Assured PNT research platform.

Version 0.6 focuses on the part that often separates a simulation from an integration product: **connecting real external systems without rewriting the estimator.**

The release adds:

- a pluggable Sensor Adapter SDK
- third-party adapter discovery through Python entry points
- authenticated gRPC sensor streaming
- optional TLS transport
- a protobuf service contract for external clients
- ROS 2 sensor/gateway bridging
- the same transport-neutral SensorPacket contract across replay, UDP, gRPC, and ROS 2

The architectural goal is simple: a sensor vendor, simulator, lab instrument, or robotics stack should be able to plug into the navigation pipeline while the estimation core remains unchanged.

That makes the software more useful for SIL/HIL integration, sensor trade studies, and future customer-specific hardware work.

As with the previous releases, the included navigation results remain synthetic simulation results — not flight-test or certified performance claims.

#AssuredPNT #GNC #SensorFusion #ROS2 #gRPC #AerospaceSoftware #Navigation #SystemsEngineering
