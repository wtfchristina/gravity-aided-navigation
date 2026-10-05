from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gravity_nav.config import load_config
from gravity_nav.trade_study import sensor_trade_study
cfg=load_config(ROOT/"configs/fixed_wing_fused.yaml")
df=sensor_trade_study(cfg); df.to_csv(ROOT/"results/trade_study.csv",index=False); print(df.head(15).to_string(index=False))
