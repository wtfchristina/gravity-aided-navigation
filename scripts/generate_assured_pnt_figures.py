from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gravity_nav.config import load_config
from gravity_nav.assured_pnt import run_assured_pnt
from gravity_nav.observability import combined_information, normalized_score
cfg=load_config(ROOT/"configs/fixed_wing_fused.yaml")
df,m,gmap,mmap=run_assured_pnt(cfg); (ROOT/"figures").mkdir(exist_ok=True)
fig=plt.figure(figsize=(10,5)); plt.plot(df.truth_x_m/1000,df.truth_y_m/1000,label="Truth",linewidth=2); plt.plot(df.ins_x_m/1000,df.ins_y_m/1000,label="INS only"); plt.plot(df.aided_x_m/1000,df.aided_y_m/1000,label="Gravity + magnetic EKF"); plt.xlabel("East (km)"); plt.ylabel("North (km)"); plt.title("Multi-modal passive navigation"); plt.legend(); plt.grid(alpha=.25); plt.tight_layout(); fig.savefig(ROOT/"figures/assured_pnt_trajectory.png",dpi=180); plt.close(fig)
xx,yy,_=gmap.grid(); info=combined_information([(gmap,cfg.gravity_noise_std),(mmap,cfg.magnetic_noise_std_nt)],xx,yy); score=normalized_score(info)
fig=plt.figure(figsize=(10,5)); plt.contourf(xx/1000,yy/1000,score,levels=20); plt.colorbar(label="Normalized local observability score"); plt.plot(df.truth_x_m/1000,df.truth_y_m/1000,linewidth=2); plt.xlabel("East (km)"); plt.ylabel("North (km)"); plt.title("Environmental navigation observability"); plt.tight_layout(); fig.savefig(ROOT/"figures/observability_heatmap.png",dpi=180); plt.close(fig)
print(m)
