from gravity_nav.assured_pnt import AssuredPNTConfig, run_assured_pnt
from gravity_nav.integrity import IntegrityConfig, single_run_integrity, campaign_integrity

def test_integrity_trace_columns():
    df,_,_,_=run_assured_pnt(AssuredPNTConfig(duration_s=20,dt=1.0))
    trace,m=single_run_integrity(df,IntegrityConfig(alert_limit_m=500))
    assert 'protection_level_proxy_m' in trace.columns
    assert 0 <= m['availability_fraction'] <= 1

def test_integrity_campaign():
    df=campaign_integrity(AssuredPNTConfig(duration_s=10,dt=1.0),runs=2)
    assert len(df)==2
