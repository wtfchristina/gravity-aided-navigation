from pathlib import Path
import sys, json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gravity_nav.config import load_config
from gravity_nav.assured_pnt import run_assured_pnt
from gravity_nav.reporting import write_report

cfg=load_config(ROOT/"configs/fixed_wing_fused.yaml")
df,m,_,_=run_assured_pnt(cfg)
(ROOT/"results").mkdir(exist_ok=True)
df.to_csv(ROOT/"results/assured_pnt_fused.csv",index=False)
(ROOT/"results/assured_pnt_fused.json").write_text(json.dumps(m,indent=2),encoding="utf-8")
write_report(ROOT/"results/assured_pnt_fused_report.md","Assured PNT Fused Scenario",m,["Synthetic gravity and magnetic maps","Planar kinematics","Research demonstration only"])
print(json.dumps({k:v for k,v in m.items() if k!="config"},indent=2))
