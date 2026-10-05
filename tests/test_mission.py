from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.requirements import MissionRequirement
from gravity_nav.mission import MissionEnvelope, mission_envelope_study

def test_mission_envelope_runs():
    env=MissionEnvelope(outage_durations_s=(10,),speeds_mps=(50,))
    df=mission_envelope_study(AssuredPNTConfig(duration_s=10,dt=1.0),MissionRequirement(5000,5000,.5,6000),env,runs=1)
    assert len(df)==1
    assert 'requirement_met' in df.columns
