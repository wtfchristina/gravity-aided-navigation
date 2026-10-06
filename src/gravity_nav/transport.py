from __future__ import annotations

from dataclasses import dataclass
import socket
from pathlib import Path

from .packets import SensorPacket
from .replay import write_jsonl


@dataclass(frozen=True)
class UDPConfig:
    host: str = "127.0.0.1"
    port: int = 5555
    recv_buffer_bytes: int = 65535
    timeout_s: float = 0.5


class UDPSender:
    def __init__(self, cfg: UDPConfig):
        self.cfg = cfg
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, packet: SensorPacket) -> None:
        self.sock.sendto(packet.to_json().encode("utf-8"), (self.cfg.host, self.cfg.port))

    def close(self) -> None:
        self.sock.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()


class UDPReceiver:
    def __init__(self, cfg: UDPConfig):
        self.cfg = cfg
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((cfg.host, cfg.port))
        self.sock.settimeout(cfg.timeout_s)

    def receive(self) -> SensorPacket | None:
        try:
            raw, _ = self.sock.recvfrom(self.cfg.recv_buffer_bytes)
        except socket.timeout:
            return None
        return SensorPacket.from_json(raw)

    def close(self) -> None:
        self.sock.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()


def record_udp(cfg: UDPConfig, duration_s: float, path: str | Path) -> int:
    import time
    received: list[SensorPacket] = []
    deadline = time.monotonic() + duration_s
    with UDPReceiver(cfg) as receiver:
        while time.monotonic() < deadline:
            packet = receiver.receive()
            if packet is not None:
                received.append(packet)
    write_jsonl(path, received)
    return len(received)
