import socket
import pytest

grpc = pytest.importorskip("grpc")

from gravity_nav.grpc_transport import GRPCClientConfig, GRPCSensorClient, GRPCServerConfig, create_server


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_grpc_rejects_wrong_token():
    port = free_port()
    server = create_server(GRPCServerConfig("127.0.0.1", port, "right"), lambda packet: {"accepted": True})
    server.start()
    try:
        with GRPCSensorClient(GRPCClientConfig(f"127.0.0.1:{port}", "wrong")) as client:
            with pytest.raises(grpc.RpcError) as exc:
                client.health()
            assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        server.stop(grace=0)
