from gravity_nav.assured_pnt import AssuredPNTConfig, run_assured_pnt

def test_fused_mode_runs_and_improves_default():
    _,m,_,_=run_assured_pnt(AssuredPNTConfig(duration_s=120.0,mode="fused"))
    assert m["aided_rmse_m"] < m["ins_rmse_m"]
    assert m["gravity_updates_accepted"] > 0
    assert m["magnetic_updates_accepted"] > 0
