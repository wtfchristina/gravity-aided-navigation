from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.monte_carlo import run_campaign, summarize_campaign

def test_campaign_shape():
    df=run_campaign(AssuredPNTConfig(duration_s=20.0,dt=1.0),runs=2,modes=("ins","fused"))
    assert len(df)==4
    s=summarize_campaign(df)
    assert set(s["mode"])=={"ins","fused"}
