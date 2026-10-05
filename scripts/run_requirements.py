from pathlib import Path
from gravity_nav.requirements_config import load_mission_requirement
from gravity_nav.requirements import solve_sensor_requirements, evaluate_configuration
import json

cfg,req=load_mission_requirement('configs/mission_requirement.yaml')
out=Path('results'); out.mkdir(exist_ok=True)
df=solve_sensor_requirements(cfg,req,runs=20)
df.to_csv(out/'requirements.csv',index=False)
(out/'requirements_baseline.json').write_text(json.dumps(evaluate_configuration(cfg,req,20),indent=2))
print(df.head(15).to_string(index=False))
