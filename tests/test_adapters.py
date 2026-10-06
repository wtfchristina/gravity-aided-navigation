import pytest

from gravity_nav.adapters import (
    AdapterError, AdapterRegistry, ExampleTacticalIMUAdapter,
    MappingAdapter, PacketJSONAdapter, default_registry,
)
from gravity_nav.packets import SensorPacket


def test_mapping_adapter_maps_fields():
    adapter = MappingAdapter(
        sensor="gravity",
        value_map={"measurement": "g_obs", "noise_std": "sigma"},
    )
    packet = adapter.adapt({"timestamp_s": 1.25, "sequence": 7, "g_obs": 12.0, "sigma": 0.5})
    assert packet.sensor == "gravity"
    assert packet.values["measurement"] == 12.0
    assert packet.sequence == 7


def test_mapping_adapter_rejects_missing_field():
    adapter = MappingAdapter(sensor="gravity", value_map={"measurement": "g_obs"})
    with pytest.raises(AdapterError):
        adapter.adapt({"timestamp_s": 0.0, "sequence": 0})


def test_packet_json_roundtrip():
    packet = SensorPacket("magnetic", 2.0, 3, {"measurement": 4.0, "noise_std": 1.0})
    recovered = PacketJSONAdapter().adapt(packet.to_json())
    assert recovered == packet


def test_example_tactical_imu_adapter_converts_g_to_si():
    packet = ExampleTacticalIMUAdapter().adapt({
        "time_us": 1_000_000,
        "seq": 4,
        "accel_x_g": 1.0,
        "accel_y_g": -0.5,
        "sample_period_us": 10_000,
    })
    assert packet.sensor == "imu"
    assert packet.timestamp_s == pytest.approx(1.0)
    assert packet.values["ax_mps2"] == pytest.approx(9.80665)
    assert packet.values["dt_s"] == pytest.approx(0.01)


def test_registry_create_and_duplicate_guard():
    reg = AdapterRegistry()
    reg.register("json", PacketJSONAdapter)
    assert isinstance(reg.create("json"), PacketJSONAdapter)
    with pytest.raises(AdapterError):
        reg.register("json", PacketJSONAdapter)


def test_default_registry_has_reference_adapters():
    assert {"packet_json", "example_tactical_imu"}.issubset(default_registry().names())
