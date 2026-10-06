from __future__ import annotations

from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

from .assured_pnt import AssuredPNTConfig
from .gateway import GatewayConfig, NavigationGateway
from .streaming import LinkImpairmentConfig, generate_sensor_packets, impair_packets


@dataclass(frozen=True)
class HILConfig:
    latency_ms: float = 20.0
    jitter_ms: float = 5.0
    dropout_probability: float = 0.0
    max_measurement_staleness_s: float = 0.75
    seed: int = 101


def run_hil_demo(scenario: AssuredPNTConfig, hil: HILConfig | None = None):
    """Run an offline SIL/HIL integration exercise with transport impairments.

    Truth-reference packets are held on a separate scoring channel and never
    delivered to the estimator. Navigation packets receive latency, jitter, and
    dropout before being processed in arrival order.
    """
    hil = hil or HILConfig()
    all_packets = generate_sensor_packets(scenario, include_truth_reference=True)
    truth_packets = [p for p in all_packets if p.sensor == "truth_reference"]
    nav_packets = [p for p in all_packets if p.sensor != "truth_reference"]
    delivered = impair_packets(nav_packets, LinkImpairmentConfig(
        latency_ms=hil.latency_ms, jitter_ms=hil.jitter_ms,
        dropout_probability=hil.dropout_probability, seed=hil.seed))
    gateway = NavigationGateway(scenario, GatewayConfig(
        max_measurement_staleness_s=hil.max_measurement_staleness_s,
        innovation_gate_sigma=scenario.innovation_gate_sigma))
    for delivery_time, packet in delivered:
        gateway.process(packet, delivery_time)
    trace = gateway.dataframe()

    truth_df = pd.DataFrame([{
        "sensor_time_s": p.timestamp_s,
        "truth_x_m": p.values["x_m"], "truth_y_m": p.values["y_m"]
    } for p in truth_packets]).sort_values("sensor_time_s")
    if not trace.empty:
        trace = pd.merge_asof(
            trace.sort_values("sensor_time_s"), truth_df,
            on="sensor_time_s", direction="nearest", tolerance=max(scenario.dt, 1e-9)
        ).sort_values(["delivery_time_s", "sequence"]).reset_index(drop=True)
        trace["position_error_m"] = np.hypot(trace.est_x_m-trace.truth_x_m, trace.est_y_m-trace.truth_y_m)

    final_truth = truth_packets[-1].values if truth_packets else {"x_m": np.nan, "y_m": np.nan}
    terminal_error = float(np.hypot(gateway.ekf.x[0]-final_truth["x_m"], gateway.ekf.x[1]-final_truth["y_m"]))
    scored = trace[trace["position_error_m"].notna()] if not trace.empty else pd.DataFrame()
    rmse = float(np.sqrt(np.mean(scored["position_error_m"].to_numpy()**2))) if not scored.empty else float("nan")
    lat = trace["latency_ms"] if not trace.empty else pd.Series(dtype=float)
    metrics = {
        "terminal_error_m": terminal_error,
        "rmse_m": rmse,
        "navigation_packets_generated": int(len(nav_packets)),
        "navigation_packets_delivered": int(len(delivered)),
        "transport_delivery_pct": float(100 * len(delivered) / max(len(nav_packets), 1)),
        "stale_packets_rejected": int(gateway.stale),
        "imu_packets_processed": int(gateway.imu_packets),
        "gravity_updates_accepted": int(gateway.accepted["gravity"]),
        "magnetic_updates_accepted": int(gateway.accepted["magnetic"]),
        "mean_latency_ms": float(lat.mean()) if len(lat) else float("nan"),
        "p95_latency_ms": float(lat.quantile(0.95)) if len(lat) else float("nan"),
        "scenario": asdict(scenario),
        "hil": asdict(hil),
    }
    return trace, metrics
