# ROS 2 Integration

The optional ROS 2 bridge lets a simulator or robotics stack exchange `SensorPacket` messages with the navigation gateway.

The reference bridge uses `std_msgs/String` carrying the canonical `SensorPacket` JSON schema. This minimizes dependencies and keeps the semantic contract identical across UDP, replay, gRPC, and ROS 2.

## Gateway node

In a ROS 2 Python environment with `rclpy` and `std_msgs` available:

```bash
qpnt ros2-gateway configs/fixed_wing_fused.yaml \
  --input-topic /qpnt/sensor_packets \
  --output-topic /qpnt/navigation_state
```

## Scenario publisher

```bash
qpnt ros2-publish configs/fixed_wing_fused.yaml \
  --topic /qpnt/sensor_packets \
  --speed 10
```

## Production extension

A customer deployment can replace the `std_msgs/String` envelope with custom ROS 2 IDL while keeping the adapter SDK and `NavigationGateway` unchanged.

This bridge is a research/integration reference, not a ROS 2 safety certification claim.
