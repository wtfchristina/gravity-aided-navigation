import socket
import time
import pytest

pytest.importorskip("grpc")

from gravity_nav.grpc_transport import GRPCClientConfig, GRPCSensorClient, GRPCServerConfig, create_server
from gravity_nav.packets import SensorPacket


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_grpc_health_auth_and_packet_delivery():
    received = []
    port = free_port()
    server = create_server(
        GRPCServerConfig(host="127.0.0.1", port=port, bearer_token="secret"),
        lambda packet: received.append(packet) or {"accepted": True},
    )
    server.start()
    try:
        with GRPCSensorClient(GRPCClientConfig(f"127.0.0.1:{port}", bearer_token="secret")) as client:
            assert client.health()["status"] == "SERVING"
            reply = client.send(SensorPacket("imu", 0.0, 1, {"ax_mps2": 0.0, "ay_mps2": 0.0, "dt_s": 0.1}))
            assert reply["accepted"] is True
        assert len(received) == 1
        assert received[0].sensor == "imu"
    finally:
        server.stop(grace=0)
