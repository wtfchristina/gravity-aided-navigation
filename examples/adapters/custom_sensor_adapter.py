"""Minimal customer-adapter example.

Copy this pattern into a private integration package rather than modifying the
core estimator. The external payload format below is intentionally fictional.
"""
from gravity_nav.adapters import SensorAdapter, AdapterError
from gravity_nav.packets import SensorPacket


class MyGravitySensorAdapter(SensorAdapter):
    name = "my_gravity_sensor"

    def adapt(self, payload):
        try:
            return SensorPacket(
                sensor="gravity",
                timestamp_s=float(payload["sensor_time_ns"]) * 1e-9,
                sequence=int(payload["counter"]),
                values={
                    "measurement": float(payload["anomaly_mgal"]),
                    "noise_std": float(payload.get("sigma_mgal", 1.0)),
                },
                frame="local_xy",
                metadata={"serial": payload.get("serial", "unknown")},
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise AdapterError(f"invalid gravity-sensor payload: {exc}") from exc
