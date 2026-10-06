#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
p=argparse.ArgumentParser(); p.add_argument('--summary',default='benchmark/reports/golden/benchmark_summary.csv'); p.add_argument('--runs',default='benchmark/reports/golden/benchmark_runs.csv'); p.add_argument('--out-dir',default='benchmark/figures'); a=p.parse_args()
out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
s=pd.read_csv(a.summary); r=pd.read_csv(a.runs)
fig,ax=plt.subplots(figsize=(9,5)); ax.bar(s['mode'],s['terminal_median_m']); ax.set_ylabel('Median terminal error (m)'); ax.set_title('Public-Data Benchmark: Terminal Error by Navigation Mode'); fig.tight_layout(); fig.savefig(out/'terminal_error_by_mode.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5));
for mode,g in r.groupby('mode'):
    x=sorted(g.terminal_error_m); y=[(i+1)/len(x) for i in range(len(x))]; ax.plot(x,y,label=mode)
ax.set_xlabel('Terminal error (m)'); ax.set_ylabel('Empirical CDF'); ax.set_title('Public-Data Benchmark Terminal Error CDF'); ax.legend(); fig.tight_layout(); fig.savefig(out/'terminal_error_cdf.png',dpi=180); plt.close(fig)
