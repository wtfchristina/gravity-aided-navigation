from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gravity_nav.config import load_config
from gravity_nav.monte_carlo import run_campaign, summarize_campaign
cfg=load_config(ROOT/"configs/fixed_wing_fused.yaml")
df=run_campaign(cfg,runs=25); df.to_csv(ROOT/"results/monte_carlo.csv",index=False)
s=summarize_campaign(df); s.to_csv(ROOT/"results/monte_carlo_summary.csv",index=False); print(s.to_string(index=False))
