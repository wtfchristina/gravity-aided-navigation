from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .assured_pnt import AssuredPNTConfig
from .fusion import FusionEKF, FieldObservation
from .gravity_map import SyntheticGravityMap
from .magnetic_map import SyntheticMagneticMap
from .packets import SensorPacket


@dataclass(frozen=True)
class GatewayConfig:
    max_measurement_staleness_s: float = 0.75
    innovation_gate_sigma: float = 5.0


class NavigationGateway:
    """Small transport-facing estimator adapter for SIL/HIL demonstrations.

    It accepts transport-neutral SensorPacket objects.  Truth-reference packets
    are used only to score the demonstration and are never fed to the filter.
    """

    def __init__(self, scenario: AssuredPNTConfig, gateway: GatewayConfig | None = None,
                 gravity_map=None, magnetic_map=None):
        self.scenario = scenario
        self.gateway = gateway or GatewayConfig(innovation_gate_sigma=scenario.innovation_gate_sigma)
        x0 = np.array([0.0, 0.0, scenario.speed_mps, 0.0, 0.0, 0.0])
        P0 = np.diag([40**2, 40**2, 2**2, 2**2, 0.03**2, 0.03**2])
        self.ekf = FusionEKF(x0, P0, scenario.accel_noise_std, scenario.bias_rw_std)
        self.gravity_map = gravity_map or SyntheticGravityMap()
        self.magnetic_map = magnetic_map or SyntheticMagneticMap()
        self.filter_time_s = 0.0
        self.last_truth: dict[str, float] | None = None
        self.accepted = {"gravity": 0, "magnetic": 0}
        self.rejected = {"gravity": 0, "magnetic": 0}
        self.stale = 0
        self.imu_packets = 0
        self.trace: list[dict[str, float | str | bool]] = []

    def process(self, packet: SensorPacket, delivery_time_s: float | None = None) -> None:
        arrival = packet.timestamp_s if delivery_time_s is None else float(delivery_time_s)
        if packet.sensor == "truth_reference":
            self.last_truth = dict(packet.values)
            self._record(packet, arrival, accepted=True)
            return

        staleness = max(0.0, self.filter_time_s - packet.timestamp_s)
        if staleness > self.gateway.max_measurement_staleness_s:
            self.stale += 1
            self._record(packet, arrival, accepted=False, status="stale")
            return

        if packet.sensor == "imu":
            self.ekf.predict(np.array([packet.values["ax_mps2"], packet.values["ay_mps2"]]), packet.values["dt_s"])
            self.filter_time_s = max(self.filter_time_s, packet.timestamp_s)
            self.imu_packets += 1
            self._record(packet, arrival, accepted=True)
            return

        if packet.sensor in {"gravity", "magnetic"}:
            field = self.gravity_map if packet.sensor == "gravity" else self.magnetic_map
            obs = FieldObservation(packet.sensor, field, packet.values["measurement"], packet.values["noise_std"])
            accepted = self.ekf.update(obs, self.gateway.innovation_gate_sigma)
            self.accepted[packet.sensor] += int(accepted)
            self.rejected[packet.sensor] += int(not accepted)
            self._record(packet, arrival, accepted=accepted, status="accepted" if accepted else "innovation_rejected")
            return

        self._record(packet, arrival, accepted=False, status="unknown_sensor")

    def _record(self, packet: SensorPacket, arrival: float, accepted: bool, status: str = "ok"):
        row: dict[str, float | str | bool] = {
            "sensor_time_s": float(packet.timestamp_s), "delivery_time_s": float(arrival),
            "latency_ms": float(max(0.0, arrival - packet.timestamp_s) * 1000.0),
            "sensor": packet.sensor, "sequence": float(packet.sequence),
            "accepted": bool(accepted), "status": status,
            "est_x_m": float(self.ekf.x[0]), "est_y_m": float(self.ekf.x[1]),
        }
        if self.last_truth is not None:
            tx = self.last_truth.get("x_m", np.nan); ty = self.last_truth.get("y_m", np.nan)
            row["truth_x_m"] = float(tx); row["truth_y_m"] = float(ty)
            row["position_error_m"] = float(np.hypot(self.ekf.x[0]-tx, self.ekf.x[1]-ty))
        self.trace.append(row)

    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.trace)
