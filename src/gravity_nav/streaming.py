from __future__ import annotations

from dataclasses import dataclass
import heapq
import numpy as np

from .assured_pnt import AssuredPNTConfig
from .dynamics import nominal_acceleration, propagate_truth
from .gravity_map import SyntheticGravityMap
from .magnetic_map import SyntheticMagneticMap
from .imu import IMUConfig, IMUSimulator
from .packets import SensorPacket


@dataclass(frozen=True)
class LinkImpairmentConfig:
    """Synthetic transport impairment model for software/hardware-in-the-loop tests."""

    latency_ms: float = 20.0
    jitter_ms: float = 5.0
    dropout_probability: float = 0.0
    seed: int = 101


def generate_sensor_packets(
    cfg: AssuredPNTConfig,
    gravity_map=None,
    magnetic_map=None,
    include_truth_reference: bool = True,
) -> list[SensorPacket]:
    """Generate a timestamped sensor stream from the package's synthetic scenario.

    IMU packets occur at the propagation rate. Environmental packets use their
    configured update periods.  Optional truth packets exist only for SIL/HIL
    scoring and are explicitly labelled as references, not navigation inputs.
    """

    gmap = gravity_map or SyntheticGravityMap()
    mmap = magnetic_map or SyntheticMagneticMap()
    ss = np.random.SeedSequence(cfg.seed)
    imu_ss, gravity_ss, magnetic_ss = ss.spawn(3)
    imu_rng = np.random.default_rng(imu_ss)
    gravity_rng = np.random.default_rng(gravity_ss)
    magnetic_rng = np.random.default_rng(magnetic_ss)
    imu = IMUSimulator(IMUConfig(cfg.accel_noise_std, cfg.bias_rw_std, cfg.initial_bias_std), imu_rng)

    n = int(cfg.duration_s / cfg.dt) + 1
    truth = np.array([0.0, 0.0, cfg.speed_mps, 0.0], dtype=float)
    packets: list[SensorPacket] = []
    seq = 0
    next_g = 0.0
    next_m = 0.0

    if include_truth_reference:
        packets.append(SensorPacket("truth_reference", 0.0, seq, {
            "x_m": truth[0], "y_m": truth[1], "vx_mps": truth[2], "vy_mps": truth[3]
        }, metadata={"navigation_input": False}))
        seq += 1

    for k in range(1, n):
        t_prev = (k - 1) * cfg.dt
        t = k * cfg.dt
        a_true = nominal_acceleration(t_prev)
        truth = propagate_truth(truth, a_true, cfg.dt)
        a_meas, _ = imu.sample(a_true, cfg.dt)
        packets.append(SensorPacket("imu", t, seq, {
            "ax_mps2": float(a_meas[0]), "ay_mps2": float(a_meas[1]), "dt_s": float(cfg.dt)
        }))
        seq += 1

        if cfg.mode in {"gravity", "fused"} and t + 1e-12 >= next_g:
            z = float(gmap.value(truth[0], truth[1]) + gravity_rng.normal(0, cfg.gravity_noise_std))
            packets.append(SensorPacket("gravity", t, seq, {
                "measurement": z, "noise_std": float(cfg.gravity_noise_std)
            }))
            seq += 1
            next_g += cfg.gravity_update_period_s

        if cfg.mode in {"magnetic", "fused"} and t + 1e-12 >= next_m:
            z = float(mmap.value(truth[0], truth[1]) + magnetic_rng.normal(0, cfg.magnetic_noise_std_nt))
            packets.append(SensorPacket("magnetic", t, seq, {
                "measurement": z, "noise_std": float(cfg.magnetic_noise_std_nt)
            }))
            seq += 1
            next_m += cfg.magnetic_update_period_s

        if include_truth_reference:
            packets.append(SensorPacket("truth_reference", t, seq, {
                "x_m": float(truth[0]), "y_m": float(truth[1]),
                "vx_mps": float(truth[2]), "vy_mps": float(truth[3])
            }, metadata={"navigation_input": False}))
            seq += 1

    return sorted(packets, key=lambda p: (p.timestamp_s, p.sequence))


def impair_packets(packets: list[SensorPacket], cfg: LinkImpairmentConfig) -> list[tuple[float, SensorPacket]]:
    """Apply latency, jitter and probabilistic dropout.

    Returns `(delivery_time_s, packet)` pairs sorted by delivery time. This can
    intentionally produce out-of-order sensor arrivals when jitter is large.
    Truth reference packets are left unimpaired because they represent the lab
    scoring channel rather than a navigation link.
    """

    rng = np.random.default_rng(cfg.seed)
    heap: list[tuple[float, int, SensorPacket]] = []
    for packet in packets:
        if packet.sensor == "truth_reference":
            heapq.heappush(heap, (packet.timestamp_s, packet.sequence, packet))
            continue
        if rng.random() < cfg.dropout_probability:
            continue
        jitter = rng.normal(0.0, cfg.jitter_ms) / 1000.0
        delivery = packet.timestamp_s + max(0.0, cfg.latency_ms / 1000.0 + jitter)
        heapq.heappush(heap, (delivery, packet.sequence, packet))
    out: list[tuple[float, SensorPacket]] = []
    while heap:
        delivery, _, packet = heapq.heappop(heap)
        out.append((float(delivery), packet))
    return out
