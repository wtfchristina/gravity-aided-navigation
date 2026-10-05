from pathlib import Path
import json
from gravity_nav.config import load_config
from gravity_nav.assured_pnt import run_assured_pnt
from gravity_nav.integrity import IntegrityConfig, single_run_integrity, campaign_integrity

cfg=load_config('configs/fixed_wing_fused.yaml')
ic=IntegrityConfig(alert_limit_m=300.0)
out=Path('results'); out.mkdir(exist_ok=True)
campaign_integrity(cfg,ic,25).to_csv(out/'integrity.csv',index=False)
df,_,_,_=run_assured_pnt(cfg)
trace,m=single_run_integrity(df,ic)
trace.to_csv(out/'integrity_trace.csv',index=False)
(out/'integrity_metrics.json').write_text(json.dumps(m,indent=2))
print(json.dumps(m,indent=2))
