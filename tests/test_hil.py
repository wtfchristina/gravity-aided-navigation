from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.hil import HILConfig, run_hil_demo


def test_hil_demo_returns_metrics_and_trace():
    scenario=AssuredPNTConfig(duration_s=20,dt=.5,mode='fused')
    trace,metrics=run_hil_demo(scenario,HILConfig(latency_ms=15,jitter_ms=3,dropout_probability=.02,seed=9))
    assert len(trace) > 0
    assert metrics['navigation_packets_generated'] >= metrics['navigation_packets_delivered']
    assert metrics['transport_delivery_pct'] <= 100
    assert metrics['terminal_error_m'] >= 0
