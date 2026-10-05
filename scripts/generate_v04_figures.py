from pathlib import Path
import json
import matplotlib.pyplot as plt
from gravity_nav.assured_pnt import AssuredPNTConfig, run_assured_pnt
from gravity_nav.requirements import MissionRequirement, solve_sensor_requirements
from gravity_nav.integrity import IntegrityConfig, single_run_integrity, campaign_integrity

figdir=Path('figures'); figdir.mkdir(exist_ok=True)
out=Path('results'); out.mkdir(exist_ok=True)
base=AssuredPNTConfig(mode='fused')
req=MissionRequirement(terminal_error_limit_m=150,rmse_limit_m=250,success_probability=.8,alert_limit_m=300)
trade=solve_sensor_requirements(base,req,gravity_noise=(1,2,4),magnetic_noise=(4,8,16),update_period=(1,2),runs=8)
trade.to_csv(out/'requirements_v04_sample.csv',index=False)

# Show p95 terminal error for the 2-second update subset.
sub=trade[trade.update_period_s==2].pivot(index='gravity_noise_std',columns='magnetic_noise_std_nt',values='terminal_p95_m')
fig=plt.figure(figsize=(7,5))
plt.imshow(sub.values,aspect='auto',origin='lower')
plt.colorbar(label='Terminal error p95 (m)')
plt.xticks(range(len(sub.columns)),[str(x) for x in sub.columns])
plt.yticks(range(len(sub.index)),[str(x) for x in sub.index])
plt.xlabel('Magnetic noise std (nT)'); plt.ylabel('Gravity noise std')
plt.title('Mission requirement trade space (2 s updates)')
plt.tight_layout(); plt.savefig(figdir/'requirements_trade_space.png',dpi=180); plt.close(fig)

df,m,_,_=run_assured_pnt(base)
trace,im=single_run_integrity(df,IntegrityConfig(alert_limit_m=300))
trace.to_csv(out/'integrity_trace_v04.csv',index=False)
(out/'integrity_metrics_v04.json').write_text(json.dumps(im,indent=2))
campaign_integrity(base,IntegrityConfig(alert_limit_m=300),runs=12).to_csv(out/'integrity_campaign_v04.csv',index=False)
fig=plt.figure(figsize=(9,4.5))
plt.plot(trace.time_s,trace.position_error_m,label='Position error')
plt.plot(trace.time_s,trace.protection_level_proxy_m,label='Protection-level proxy')
plt.axhline(300,linestyle='--',label='Alert limit')
plt.xlabel('Time (s)'); plt.ylabel('Meters'); plt.title('Integrity screening proxy')
plt.legend(); plt.grid(True,alpha=.25); plt.tight_layout(); plt.savefig(figdir/'integrity_screening.png',dpi=180); plt.close(fig)
