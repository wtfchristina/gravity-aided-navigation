from pathlib import Path
import json
import sys
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gravity_nav.config import load_config
from gravity_nav.hil import HILConfig, run_hil_demo

cfg=load_config(ROOT/'configs/hil_demo.yaml')
trace,metrics=run_hil_demo(cfg,HILConfig(latency_ms=30,jitter_ms=8,dropout_probability=.02,seed=101))
figdir=ROOT/'figures'; figdir.mkdir(exist_ok=True)

fig=plt.figure(figsize=(10,4.8))
for sensor,group in trace.groupby('sensor'):
    plt.scatter(group.delivery_time_s,group.latency_ms,s=9,label=sensor,alpha=.7)
plt.xlabel('Delivery time (s)'); plt.ylabel('Transport latency (ms)')
plt.title('SIL/HIL sensor-link timing under latency, jitter, and dropout')
plt.legend(); plt.grid(True,alpha=.25); plt.tight_layout()
fig.savefig(figdir/'hil_link_timing.png',dpi=180); plt.close(fig)

fig=plt.figure(figsize=(10,4.8))
scored=trace.dropna(subset=['position_error_m'])
plt.plot(scored.sensor_time_s,scored.position_error_m)
plt.xlabel('Sensor time (s)'); plt.ylabel('Position error (m)')
plt.title('Estimator error during impaired-link SIL/HIL demonstration')
plt.grid(True,alpha=.25); plt.tight_layout()
fig.savefig(figdir/'hil_position_error.png',dpi=180); plt.close(fig)

print(json.dumps(metrics,indent=2))
