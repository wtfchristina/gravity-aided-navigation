from gravity_nav.validation import compare_modes, summarize_validation
from gravity_nav.assured_pnt import AssuredPNTConfig

def test_validation_modes():
    df=compare_modes(AssuredPNTConfig(duration_s=10,dt=1.0),runs=2)
    assert set(df['mode'])=={'ins','gravity','magnetic','fused'}
    s=summarize_validation(df)
    assert len(s)==4
