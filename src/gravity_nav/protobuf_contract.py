from __future__ import annotations

"""Runtime protobuf classes matching ``proto/sensor_gateway.proto``.

The repository keeps generated files out of source control while still exposing a
wire-compatible protobuf gRPC reference implementation. External languages can
generate normal stubs from the checked-in .proto file.
"""

import json
from functools import lru_cache
from typing import Any

from .packets import SensorPacket


class ProtobufUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=1)
def message_classes():
    try:
        from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
    except ImportError as exc:
        raise ProtobufUnavailable("protobuf support requires: pip install -e '.[integration]'") from exc

    fd = descriptor_pb2.FileDescriptorProto()
    fd.name = "sensor_gateway.proto"
    fd.package = "qpnt.v1"
    fd.syntax = "proto3"

    numeric = fd.message_type.add(); numeric.name = "NumericValue"
    f = numeric.field.add(); f.name = "key"; f.number = 1; f.label = 1; f.type = 9
    f = numeric.field.add(); f.name = "value"; f.number = 2; f.label = 1; f.type = 1

    packet = fd.message_type.add(); packet.name = "SensorPacket"
    specs = [
        ("sensor", 1, 9, 1, None),
        ("timestamp_s", 2, 1, 1, None),
        ("sequence", 3, 4, 1, None),
        ("values", 4, 11, 3, ".qpnt.v1.NumericValue"),
        ("frame", 5, 9, 1, None),
        ("metadata_json", 6, 9, 1, None),
    ]
    for name, number, typ, label, type_name in specs:
        f = packet.field.add(); f.name=name; f.number=number; f.type=typ; f.label=label
        if type_name: f.type_name = type_name

    reply = fd.message_type.add(); reply.name = "PushReply"
    for name, number, typ in [("accepted",1,8),("status",2,9),("sequence",3,4)]:
        f=reply.field.add(); f.name=name; f.number=number; f.type=typ; f.label=1

    health_req = fd.message_type.add(); health_req.name = "HealthRequest"
    health_reply = fd.message_type.add(); health_reply.name = "HealthReply"
    f=health_reply.field.add(); f.name="status"; f.number=1; f.type=9; f.label=1

    svc = fd.service.add(); svc.name = "SensorGateway"
    m=svc.method.add(); m.name="PushPacket"; m.input_type=".qpnt.v1.SensorPacket"; m.output_type=".qpnt.v1.PushReply"
    m=svc.method.add(); m.name="Health"; m.input_type=".qpnt.v1.HealthRequest"; m.output_type=".qpnt.v1.HealthReply"

    pool = descriptor_pool.DescriptorPool()
    pool.Add(fd)
    names = ["NumericValue","SensorPacket","PushReply","HealthRequest","HealthReply"]
    return {name: message_factory.GetMessageClass(pool.FindMessageTypeByName(f"qpnt.v1.{name}")) for name in names}


def packet_to_proto(packet: SensorPacket):
    cls = message_classes()["SensorPacket"]
    msg = cls(sensor=packet.sensor, timestamp_s=packet.timestamp_s, sequence=packet.sequence,
              frame=packet.frame, metadata_json=json.dumps(packet.metadata, separators=(",", ":"), sort_keys=True))
    for key, value in packet.values.items():
        item = msg.values.add(); item.key = str(key); item.value = float(value)
    return msg


def packet_from_proto(msg) -> SensorPacket:
    metadata: dict[str, Any] = json.loads(msg.metadata_json) if msg.metadata_json else {}
    return SensorPacket(
        sensor=msg.sensor,
        timestamp_s=float(msg.timestamp_s),
        sequence=int(msg.sequence),
        values={item.key: float(item.value) for item in msg.values},
        frame=msg.frame or "local_xy",
        metadata=metadata,
    )
