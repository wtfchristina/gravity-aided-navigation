from pathlib import Path
from gravity_nav.requirements_config import load_mission_requirement
from gravity_nav.mission import mission_envelope_study
cfg,req=load_mission_requirement('configs/mission_requirement.yaml')
out=Path('results'); out.mkdir(exist_ok=True)
df=mission_envelope_study(cfg,req,runs=8)
df.to_csv(out/'mission_envelope.csv',index=False)
print(df.to_string(index=False))
