from __future__ import annotations

"""Sensor Adapter SDK.

Adapters translate vendor- or simulator-specific payloads into the transport-neutral
:class:`SensorPacket` contract used by the navigation gateway.

The SDK deliberately keeps the interface small so customer integrations can live
outside the core package while still being testable against the same contract.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping

from .packets import SensorPacket


class AdapterError(ValueError):
    """Raised when an external payload cannot be converted safely."""


class SensorAdapter(ABC):
    """Base class for customer/simulator sensor adapters."""

    name: str = "base"

    @abstractmethod
    def adapt(self, payload: Any) -> SensorPacket:
        """Convert one external payload to a validated SensorPacket."""

    def adapt_many(self, payloads: Iterable[Any]) -> list[SensorPacket]:
        return [self.adapt(p) for p in payloads]


@dataclass
class AdapterRegistry:
    """Runtime registry used by integration hosts and customer plug-ins."""

    _factories: dict[str, Callable[..., SensorAdapter]] = field(default_factory=dict)

    def register(self, name: str, factory: Callable[..., SensorAdapter], *, replace: bool = False) -> None:
        key = name.strip().lower()
        if not key:
            raise AdapterError("adapter name must not be empty")
        if key in self._factories and not replace:
            raise AdapterError(f"adapter already registered: {key}")
        self._factories[key] = factory

    def create(self, name: str, **kwargs: Any) -> SensorAdapter:
        key = name.strip().lower()
        try:
            factory = self._factories[key]
        except KeyError as exc:
            raise AdapterError(f"unknown adapter: {name}; available={self.names()}") from exc
        adapter = factory(**kwargs)
        if not isinstance(adapter, SensorAdapter):
            raise TypeError("registered factory must return SensorAdapter")
        return adapter

    def names(self) -> list[str]:
        return sorted(self._factories)


@dataclass
class MappingAdapter(SensorAdapter):
    """Map a generic dict payload into SensorPacket fields.

    This is useful for quickly integrating CSV rows, JSON telemetry, or simple lab
    instruments whose field names are known but do not yet justify a dedicated
    adapter class.
    """

    sensor: str
    value_map: Mapping[str, str]
    timestamp_key: str = "timestamp_s"
    sequence_key: str = "sequence"
    frame: str = "local_xy"
    metadata_keys: tuple[str, ...] = ()
    defaults: Mapping[str, float] = field(default_factory=dict)
    name: str = "mapping"

    def adapt(self, payload: Any) -> SensorPacket:
        if not isinstance(payload, Mapping):
            raise AdapterError("MappingAdapter requires a mapping payload")
        if self.timestamp_key not in payload:
            raise AdapterError(f"missing timestamp field: {self.timestamp_key}")
        if self.sequence_key not in payload:
            raise AdapterError(f"missing sequence field: {self.sequence_key}")

        values: dict[str, float] = {}
        for output_name, input_name in self.value_map.items():
            if input_name in payload:
                values[output_name] = float(payload[input_name])
            elif output_name in self.defaults:
                values[output_name] = float(self.defaults[output_name])
            else:
                raise AdapterError(f"missing required field: {input_name}")

        metadata = {k: payload[k] for k in self.metadata_keys if k in payload}
        return SensorPacket(
            sensor=self.sensor,
            timestamp_s=float(payload[self.timestamp_key]),
            sequence=int(payload[self.sequence_key]),
            values=values,
            frame=self.frame,
            metadata=metadata,
        )


class PacketJSONAdapter(SensorAdapter):
    """Adapter for the package's canonical JSON packet schema."""

    name = "packet_json"

    def adapt(self, payload: Any) -> SensorPacket:
        if isinstance(payload, SensorPacket):
            return payload
        if isinstance(payload, (str, bytes)):
            return SensorPacket.from_json(payload)
        if isinstance(payload, Mapping):
            return SensorPacket.from_dict(dict(payload))
        raise AdapterError(f"unsupported packet payload type: {type(payload).__name__}")


class ExampleTacticalIMUAdapter(SensorAdapter):
    """Reference adapter showing how a vendor-specific IMU could be integrated.

    Expected payload fields are illustrative only and are not tied to a real
    hardware vendor or data sheet.
    """

    name = "example_tactical_imu"

    def adapt(self, payload: Any) -> SensorPacket:
        if not isinstance(payload, Mapping):
            raise AdapterError("IMU payload must be a mapping")
        required = ("time_us", "seq", "accel_x_g", "accel_y_g", "sample_period_us")
        missing = [k for k in required if k not in payload]
        if missing:
            raise AdapterError(f"missing IMU fields: {missing}")
        g0 = 9.80665
        return SensorPacket(
            sensor="imu",
            timestamp_s=float(payload["time_us"]) * 1e-6,
            sequence=int(payload["seq"]),
            values={
                "ax_mps2": float(payload["accel_x_g"]) * g0,
                "ay_mps2": float(payload["accel_y_g"]) * g0,
                "dt_s": float(payload["sample_period_us"]) * 1e-6,
            },
            frame=str(payload.get("frame", "local_xy")),
            metadata={"adapter": self.name},
        )


def default_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register("packet_json", PacketJSONAdapter)
    registry.register("example_tactical_imu", ExampleTacticalIMUAdapter)
    return registry


def discover_entrypoint_adapters(registry: AdapterRegistry | None = None, *, group: str = "gravity_nav.sensor_adapters") -> AdapterRegistry:
    """Discover third-party adapter factories installed via Python entry points.

    A private integration wheel can expose, for example::

        [project.entry-points."gravity_nav.sensor_adapters"]
        vendor_imu = "my_company_qpnt.adapters:VendorIMUAdapter"

    The core package never needs to contain customer-specific hardware code.
    """
    from importlib.metadata import entry_points

    registry = registry or default_registry()
    eps = entry_points()
    selected = eps.select(group=group) if hasattr(eps, "select") else eps.get(group, [])
    for ep in selected:
        registry.register(ep.name, ep.load(), replace=True)
    return registry
