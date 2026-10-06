#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from gravity_nav.config import load_config
from gravity_nav.sensor_profiles import apply_profile
from gravity_nav.geogrid import GeoGridMap, LocalENUFieldMap
from gravity_nav.validation import compare_modes, summarize_validation
from gravity_nav.assured_pnt import run_assured_pnt

ROOT = Path(__file__).resolve().parents[1]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load_maps(gravity_path: Path, magnetic_path: Path, lat: float, lon: float, alt: float):
    gg=GeoGridMap.from_csv(gravity_path,'gravity_golden','demo_units')
    mg=GeoGridMap.from_csv(magnetic_path,'magnetic_golden','demo_units')
    return LocalENUFieldMap(gg,lat,lon,alt), LocalENUFieldMap(mg,lat,lon,alt)

def plot_summary(summary: pd.DataFrame, out: Path):
    s=summary.set_index('mode').loc[['ins','gravity','magnetic','fused']]
    fig,ax=plt.subplots(figsize=(9,5.4))
    x=np.arange(len(s))
    ax.bar(x-0.18,s['terminal_median_m'],0.36,label='Median terminal error')
    ax.bar(x+0.18,s['terminal_p95_m'],0.36,label='95th-percentile terminal error')
    ax.set_xticks(x,s.index.str.upper())
    ax.set_ylabel('Position error (m)')
    ax.set_title('Phoenix Golden Demo — 30-run GNSS-denied trade study')
    ax.legend()
    ax.grid(axis='y',alpha=.25)
    fig.tight_layout(); fig.savefig(out,dpi=180); plt.close(fig)

def plot_trajectory(trace: pd.DataFrame, out: Path):
    fig,ax=plt.subplots(figsize=(8.5,6.2))
    ax.plot(trace.truth_x_m/1000,trace.truth_y_m/1000,label='Truth',linewidth=2.4)
    ax.plot(trace.ins_x_m/1000,trace.ins_y_m/1000,label='INS only',linestyle='--')
    ax.plot(trace.aided_x_m/1000,trace.aided_y_m/1000,label='Fused environmental aiding',linewidth=2)
    ax.set_xlabel('East (km)'); ax.set_ylabel('North (km)')
    ax.set_title('Representative GNSS-denied trajectory')
    ax.axis('equal'); ax.grid(alpha=.25); ax.legend()
    fig.tight_layout(); fig.savefig(out,dpi=180); plt.close(fig)

def plot_error(trace: pd.DataFrame, out: Path):
    t=trace.time_s
    ins=np.hypot(trace.ins_x_m-trace.truth_x_m, trace.ins_y_m-trace.truth_y_m)
    aided=np.hypot(trace.aided_x_m-trace.truth_x_m, trace.aided_y_m-trace.truth_y_m)
    fig,ax=plt.subplots(figsize=(9,5.2))
    ax.plot(t,ins,label='INS only')
    ax.plot(t,aided,label='Fused environmental aiding')
    ax.set_xlabel('Time (s)'); ax.set_ylabel('Position error (m)')
    ax.set_title('Representative position error')
    ax.grid(alpha=.25); ax.legend()
    fig.tight_layout(); fig.savefig(out,dpi=180); plt.close(fig)

def write_report(summary: pd.DataFrame, metrics: dict, meta: dict, report_path: Path):
    idx=summary.set_index('mode')
    ins=float(idx.loc['ins','terminal_median_m']); fused=float(idx.loc['fused','terminal_median_m'])
    reduction=100*(1-fused/ins)
    lines=[
        '# Phoenix GNSS-Denied Golden Demo', '',
        '> Reproducible research simulation. Bundled environmental-field values are synthetic on a real geodetic grid. These results are not flight-test, hardware-validation, or certified-navigation claims.', '',
        '## Mission', '',
        f"- Duration: {meta['duration_s']:.0f} s",
        f"- Representative distance: {metrics['distance_km']:.1f} km",
        f"- Sensor profile: {meta['profile']}",
        f"- Monte Carlo runs per mode: {meta['runs']}",
        f"- Reference origin: {meta['ref_lat']:.4f}, {meta['ref_lon']:.4f}", '',
        '## Headline result', '',
        f"Median terminal error fell from **{ins:,.0f} m (INS-only)** to **{fused:,.0f} m (fused)** in this modeled scenario — a **{reduction:.1f}% reduction**.", '',
        '## Mode comparison', '', summary.to_markdown(index=False), '',
        '## Representative fused run', '',
        f"- INS terminal error: {metrics['ins_terminal_m']:,.1f} m",
        f"- Fused terminal error: {metrics['aided_terminal_m']:,.1f} m",
        f"- Fused terminal improvement: {metrics['terminal_improvement_pct']:.1f}%",
        f"- Gravity updates accepted: {metrics['gravity_updates_accepted']}",
        f"- Magnetic updates accepted: {metrics['magnetic_updates_accepted']}", '',
        '## Reproducibility', '',
        f"- Gravity-map SHA-256: `{meta['gravity_sha256']}`",
        f"- Magnetic-map SHA-256: `{meta['magnetic_sha256']}`",
        '- Fixed scenario configuration is stored in `golden_demo/golden_demo.yaml`.',
        '- Raw Monte Carlo runs, summary CSV, representative trajectory, metadata, and figures are packaged with the demo.', '',
        '## Interpretation', '',
        'The demo is designed to answer a trade-study question: under the same trajectory and inertial realization policy, how do INS-only, gravity-aided, magnetic-aided, and fused solutions compare?', '',
        'The bundled maps are deliberately synthetic so the demo is fully redistributable and runnable without third-party data licenses. For external validation, replace them with provenance-controlled EGM2008, WMM/anomaly products, or customer-supplied maps using the public-data workflow already included in the repository.', '',
        '## Limitations', '',
        '- Synthetic environmental-field values do not establish real-world map observability.',
        '- Sensor profiles are illustrative modeling assumptions, not hardware specifications.',
        '- No flight test, hardware-in-the-loop certification, or safety-of-life claim is made.',
        '- WMM main-field data alone may not provide the spatial anomaly content needed for all magnetic map-matching missions.',
    ]
    report_path.write_text('\n'.join(lines),encoding='utf-8')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',type=int,default=30)
    ap.add_argument('--profile',default='tactical')
    ap.add_argument('--gravity',default='golden_demo/data/phoenix_gravity_demo.csv')
    ap.add_argument('--magnetic',default='golden_demo/data/phoenix_magnetic_demo.csv')
    ap.add_argument('--out',default='golden_demo/results')
    args=ap.parse_args()
    gravity=(ROOT/args.gravity).resolve(); magnetic=(ROOT/args.magnetic).resolve(); out=(ROOT/args.out).resolve()
    figs=ROOT/'golden_demo/figures'; reps=ROOT/'golden_demo/reports'
    out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); reps.mkdir(parents=True,exist_ok=True)
    ref_lat,ref_lon,ref_alt=33.4484,-112.0740,350.0
    cfg=apply_profile(load_config(ROOT/'configs/real_data_validation.yaml'),args.profile)
    gmap,mmap=load_maps(gravity,magnetic,ref_lat,ref_lon,ref_alt)
    raw=compare_modes(cfg,args.runs,gravity_map=gmap,magnetic_map=mmap)
    summary=summarize_validation(raw)
    raw.to_csv(out/'golden_demo_runs.csv',index=False); summary.to_csv(out/'golden_demo_summary.csv',index=False)
    # Representative trace uses the fixed base seed in fused mode.
    cfg.mode='fused'
    trace,metrics,_,_=run_assured_pnt(cfg,gravity_map=gmap,magnetic_map=mmap)
    trace.to_csv(out/'representative_fused_trace.csv',index=False)
    meta={'runs':args.runs,'profile':args.profile,'ref_lat':ref_lat,'ref_lon':ref_lon,'ref_alt':ref_alt,
          'duration_s':cfg.duration_s,'gravity_sha256':sha256(gravity),'magnetic_sha256':sha256(magnetic),
          'gravity_input':str(gravity.relative_to(ROOT)) if gravity.is_relative_to(ROOT) else str(gravity),
          'magnetic_input':str(magnetic.relative_to(ROOT)) if magnetic.is_relative_to(ROOT) else str(magnetic)}
    (out/'golden_demo_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    (out/'representative_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    plot_summary(summary,figs/'golden_demo_summary.png')
    plot_trajectory(trace,figs/'golden_demo_trajectory.png')
    plot_error(trace,figs/'golden_demo_position_error.png')
    write_report(summary,metrics,meta,reps/'GOLDEN_DEMO_REPORT.md')
    print(summary.to_string(index=False))
    print('\nReport:',reps/'GOLDEN_DEMO_REPORT.md')

if __name__=='__main__': main()
