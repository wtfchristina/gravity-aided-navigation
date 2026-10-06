import json
from gravity_nav.packets import SensorPacket
from gravity_nav.ros2_bridge import packet_to_ros_json, packet_from_ros_json


def test_ros2_json_envelope_roundtrip_without_ros_install():
    packet = SensorPacket("gravity", 4.0, 9, {"measurement": 1.2, "noise_std": 0.2})
    assert packet_from_ros_json(packet_to_ros_json(packet)) == packet
