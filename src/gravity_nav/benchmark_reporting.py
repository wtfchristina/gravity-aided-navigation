from __future__ import annotations
from pathlib import Path
import json
import pandas as pd


def build_markdown_report(summary_csv, metadata_json, provenance_json, out_path):
    s=pd.read_csv(summary_csv); meta=json.loads(Path(metadata_json).read_text()); prov=json.loads(Path(provenance_json).read_text())
    lines=['# Assured PNT Public-Data Benchmark Report','',
           '> Research benchmark. Results are simulation outputs driven by public/reference environmental-field data; they are not flight-test or certified navigation performance.','',
           '## Scenario','',f"- Runs per mode: {meta.get('runs')}",f"- Sensor profile: {meta.get('profile')}",
           f"- Reference: {meta.get('ref_lat')}, {meta.get('ref_lon')} at {meta.get('ref_alt')} m",'',
           '## Results','',s.to_markdown(index=False),'','## Data provenance','']
    for d in prov.get('datasets',[]):
        lines += [f"### {d.get('product')}",f"- Provider: {d.get('provider')}",f"- Source: {d.get('source_url')}",f"- SHA-256: {d.get('sha256') or 'not recorded'}",f"- Note: {d.get('license_note') or ''}",'']
    lines += ['## Interpretation','',
              'Compare INS-only, single-field aiding, and fused modes using the same trajectory, sensor profile, random-seed policy, and map region. Report median and 95th-percentile terminal/RMS error rather than a single best-case run.','',
              '## Limitations','',
              '- Environmental maps may be model products rather than local survey truth.','- Simulation sensor models do not establish hardware performance.','- Map observability varies geographically.','- This report is not a certification artifact.']
    Path(out_path).write_text('\n'.join(lines),encoding='utf-8')
