from __future__ import annotations

from pathlib import Path
import json
import time
from collections.abc import Iterable, Callable

from .packets import SensorPacket


def write_jsonl(path: str | Path, packets: Iterable[SensorPacket]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for p in packets:
            f.write(p.to_json() + "\n")
    return path


def read_jsonl(path: str | Path) -> list[SensorPacket]:
    packets: list[SensorPacket] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                packets.append(SensorPacket.from_dict(json.loads(line)))
            except Exception as exc:
                raise ValueError(f"invalid sensor log line {line_no}: {exc}") from exc
    return packets


def replay_packets(
    packets: list[SensorPacket],
    callback: Callable[[SensorPacket], None],
    speed: float = 0.0,
) -> None:
    """Replay packets into a callback.

    `speed=0` disables wall-clock sleeping. `speed=1` is real time; `speed=10`
    is ten times faster than real time.
    """
    if speed < 0:
        raise ValueError("speed must be >= 0")
    if not packets:
        return
    previous = packets[0].timestamp_s
    for p in packets:
        if speed > 0:
            dt = max(0.0, p.timestamp_s - previous) / speed
            if dt:
                time.sleep(dt)
        callback(p)
        previous = p.timestamp_s
