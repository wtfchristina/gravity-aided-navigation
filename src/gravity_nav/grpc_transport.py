from __future__ import annotations

"""Optional authenticated, protobuf-compatible gRPC integration transport."""

from concurrent import futures
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Any

from .packets import SensorPacket
from .protobuf_contract import message_classes, packet_to_proto, packet_from_proto

SERVICE = "qpnt.v1.SensorGateway"
PUSH_PACKET = f"/{SERVICE}/PushPacket"
HEALTH = f"/{SERVICE}/Health"


class GRPCUnavailable(RuntimeError):
    pass


def _grpc():
    try:
        import grpc
    except ImportError as exc:
        raise GRPCUnavailable("gRPC support requires: pip install -e '.[integration]'") from exc
    return grpc


@dataclass(frozen=True)
class GRPCServerConfig:
    host: str = "127.0.0.1"
    port: int = 50051
    bearer_token: str | None = None
    max_workers: int = 4
    tls_cert: str | None = None
    tls_key: str | None = None


@dataclass(frozen=True)
class GRPCClientConfig:
    target: str = "127.0.0.1:50051"
    bearer_token: str | None = None
    tls_root_cert: str | None = None
    timeout_s: float = 5.0


def _authorized(context, token: str | None) -> bool:
    if not token:
        return True
    metadata = {k.lower(): v for k, v in context.invocation_metadata()}
    return metadata.get("authorization") == f"Bearer {token}"


def create_server(config: GRPCServerConfig, on_packet: Callable[[SensorPacket], dict[str, Any] | None]):
    grpc = _grpc()
    classes = message_classes()
    PacketPB = classes["SensorPacket"]; PushReply = classes["PushReply"]
    HealthRequest = classes["HealthRequest"]; HealthReply = classes["HealthReply"]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))

    def push_packet(request, context):
        if not _authorized(context, config.bearer_token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid bearer token")
        try:
            packet = packet_from_proto(request)
            result = on_packet(packet) or {}
            return PushReply(
                accepted=bool(result.get("accepted", True)),
                status=str(result.get("status", "accepted")),
                sequence=packet.sequence,
            )
        except Exception as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

    def health(_request, context):
        if not _authorized(context, config.bearer_token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid bearer token")
        return HealthReply(status="SERVING")

    handler = grpc.method_handlers_generic_handler(
        SERVICE,
        {
            "PushPacket": grpc.unary_unary_rpc_method_handler(
                push_packet, request_deserializer=PacketPB.FromString,
                response_serializer=lambda msg: msg.SerializeToString(),
            ),
            "Health": grpc.unary_unary_rpc_method_handler(
                health, request_deserializer=HealthRequest.FromString,
                response_serializer=lambda msg: msg.SerializeToString(),
            ),
        },
    )
    server.add_generic_rpc_handlers((handler,))

    address = f"{config.host}:{config.port}"
    if config.tls_cert and config.tls_key:
        cert = Path(config.tls_cert).read_bytes(); key = Path(config.tls_key).read_bytes()
        creds = grpc.ssl_server_credentials(((key, cert),))
        server.add_secure_port(address, creds)
    else:
        server.add_insecure_port(address)
    return server


class GRPCSensorClient:
    def __init__(self, config: GRPCClientConfig):
        self.config = config
        grpc = _grpc(); classes = message_classes()
        self.PushReply = classes["PushReply"]; self.HealthReply = classes["HealthReply"]; self.HealthRequest = classes["HealthRequest"]
        if config.tls_root_cert:
            roots = Path(config.tls_root_cert).read_bytes()
            self.channel = grpc.secure_channel(config.target, grpc.ssl_channel_credentials(root_certificates=roots))
        else:
            self.channel = grpc.insecure_channel(config.target)
        self._push = self.channel.unary_unary(
            PUSH_PACKET,
            request_serializer=lambda msg: msg.SerializeToString(),
            response_deserializer=self.PushReply.FromString,
        )
        self._health = self.channel.unary_unary(
            HEALTH,
            request_serializer=lambda msg: msg.SerializeToString(),
            response_deserializer=self.HealthReply.FromString,
        )

    @property
    def metadata(self):
        return (("authorization", f"Bearer {self.config.bearer_token}"),) if self.config.bearer_token else None

    def health(self) -> dict[str, Any]:
        reply = self._health(self.HealthRequest(), timeout=self.config.timeout_s, metadata=self.metadata)
        return {"status": reply.status, "service": SERVICE}

    def send(self, packet: SensorPacket) -> dict[str, Any]:
        reply = self._push(packet_to_proto(packet), timeout=self.config.timeout_s, metadata=self.metadata)
        return {"accepted": bool(reply.accepted), "status": reply.status, "sequence": int(reply.sequence), "sensor": packet.sensor}

    def send_many(self, packets: Iterable[SensorPacket]) -> list[dict[str, Any]]:
        return [self.send(p) for p in packets]

    def close(self): self.channel.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
