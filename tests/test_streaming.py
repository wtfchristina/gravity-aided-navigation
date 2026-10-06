from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.streaming import generate_sensor_packets, impair_packets, LinkImpairmentConfig


def test_generation_and_deterministic_impairment():
    cfg=AssuredPNTConfig(duration_s=5,dt=0.5,mode='fused')
    packets=generate_sensor_packets(cfg,include_truth_reference=False)
    assert any(p.sensor=='imu' for p in packets)
    assert any(p.sensor=='gravity' for p in packets)
    a=impair_packets(packets,LinkImpairmentConfig(latency_ms=10,jitter_ms=2,dropout_probability=.1,seed=4))
    b=impair_packets(packets,LinkImpairmentConfig(latency_ms=10,jitter_ms=2,dropout_probability=.1,seed=4))
    assert [(round(t,8),p.sequence) for t,p in a] == [(round(t,8),p.sequence) for t,p in b]
