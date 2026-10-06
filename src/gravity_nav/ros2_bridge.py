from __future__ import annotations

"""Optional ROS 2 bridge using std_msgs/String as a portable demo envelope.

The bridge intentionally reuses SensorPacket JSON rather than introducing a
second semantic schema. A production deployment can replace std_msgs/String with
custom IDL while keeping the adapter/gateway layers unchanged.
"""

import json
from typing import Callable

from .packets import SensorPacket


class ROS2Unavailable(RuntimeError):
    pass


def packet_to_ros_json(packet: SensorPacket) -> str:
    return packet.to_json()


def packet_from_ros_json(data: str) -> SensorPacket:
    return SensorPacket.from_json(data)


def navigation_state_json(gateway) -> str:
    state = gateway.ekf.x
    return json.dumps({
        "filter_time_s": float(gateway.filter_time_s),
        "x_m": float(state[0]), "y_m": float(state[1]),
        "vx_mps": float(state[2]), "vy_mps": float(state[3]),
        "bias_ax_mps2": float(state[4]), "bias_ay_mps2": float(state[5]),
    }, separators=(",", ":"), sort_keys=True)


def run_gateway_node(gateway, *, input_topic: str = "/qpnt/sensor_packets", output_topic: str = "/qpnt/navigation_state") -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise ROS2Unavailable("ROS 2 bridge requires a ROS 2 Python environment with rclpy and std_msgs") from exc

    class GatewayNode(Node):
        def __init__(self):
            super().__init__("qpnt_navigation_gateway")
            self.publisher = self.create_publisher(String, output_topic, 10)
            self.subscription = self.create_subscription(String, input_topic, self.on_packet, 50)

        def on_packet(self, msg):
            try:
                packet = packet_from_ros_json(msg.data)
                gateway.process(packet)
                out = String(); out.data = navigation_state_json(gateway)
                self.publisher.publish(out)
            except Exception as exc:
                self.get_logger().error(f"packet rejected: {exc}")

    rclpy.init()
    node = GatewayNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()


def run_publisher_node(packets, *, topic: str = "/qpnt/sensor_packets", rate_scale: float = 1.0) -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise ROS2Unavailable("ROS 2 bridge requires a ROS 2 Python environment with rclpy and std_msgs") from exc
    import time

    class PublisherNode(Node):
        def __init__(self):
            super().__init__("qpnt_sensor_publisher")
            self.publisher = self.create_publisher(String, topic, 50)

    rclpy.init(); node = PublisherNode()
    previous = None
    try:
        for packet in packets:
            if previous is not None and rate_scale > 0:
                time.sleep(max(0.0, packet.timestamp_s - previous) / rate_scale)
            msg = String(); msg.data = packet_to_ros_json(packet)
            node.publisher.publish(msg)
            rclpy.spin_once(node, timeout_sec=0.0)
            previous = packet.timestamp_s
    finally:
        node.destroy_node(); rclpy.shutdown()
