from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gravity_nav.validation import compare_modes, summarize_validation
from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.sensor_profiles import apply_profile

out=ROOT/'figures'; out.mkdir(exist_ok=True)
cfg=apply_profile(AssuredPNTConfig(duration_s=300.0),'tactical')
df=compare_modes(cfg,runs=20)
s=summarize_validation(df)

plt.figure(figsize=(8,4.5))
plt.bar(s['mode'],s['terminal_median_m'])
plt.ylabel('Median terminal error (m)')
plt.title('v0.7 reproducible validation campaign')
plt.grid(axis='y',alpha=.25)
plt.tight_layout(); plt.savefig(out/'v07_validation_summary.png',dpi=180); plt.close()

plt.figure(figsize=(8,4.5))
for mode,g in df.groupby('mode'):
    vals=g['terminal_error_m'].sort_values().to_numpy()
    p=(pd.Series(range(1,len(vals)+1))/len(vals)).to_numpy()
    plt.plot(vals,p,label=mode)
plt.xlabel('Terminal error (m)'); plt.ylabel('Empirical CDF')
plt.title('Terminal-error distribution by aiding mode')
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(out/'v07_terminal_error_cdf.png',dpi=180); plt.close()
