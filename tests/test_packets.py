from gravity_nav.packets import SensorPacket


def test_packet_json_roundtrip():
    p = SensorPacket('imu', 1.25, 7, {'ax_mps2': 0.1, 'ay_mps2': -0.2, 'dt_s': 0.5}, metadata={'source':'sim'})
    q = SensorPacket.from_json(p.to_json())
    assert q == p
