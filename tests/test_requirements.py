from dataclasses import replace
from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.requirements import MissionRequirement, evaluate_configuration, solve_sensor_requirements

def test_requirement_evaluation_has_probability():
    cfg=AssuredPNTConfig(duration_s=20,dt=1.0,mode='fused')
    req=MissionRequirement(terminal_error_limit_m=1000,rmse_limit_m=1000,success_probability=.5)
    r=evaluate_configuration(cfg,req,runs=3)
    assert 0 <= r['success_probability'] <= 1
    assert isinstance(r['requirement_met'],bool)

def test_requirement_solver_returns_ranked_rows():
    cfg=AssuredPNTConfig(duration_s=20,dt=1.0)
    req=MissionRequirement(terminal_error_limit_m=5000,rmse_limit_m=5000,success_probability=.5)
    df=solve_sensor_requirements(cfg,req,gravity_noise=(1,2),magnetic_noise=(4,),update_period=(1,),runs=2)
    assert len(df)==2
    assert 'burden_score' in df.columns
