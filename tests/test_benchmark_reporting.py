import json, pandas as pd
from gravity_nav.benchmark_reporting import build_markdown_report

def test_report(tmp_path):
    pd.DataFrame([{'mode':'fused','runs':2,'terminal_median_m':10,'terminal_p95_m':12,'terminal_mean_m':10.5,'terminal_std_m':1,'rmse_median_m':8,'rmse_p95_m':9}]).to_csv(tmp_path/'s.csv',index=False)
    (tmp_path/'m.json').write_text(json.dumps({'runs':2,'profile':'tactical','ref_lat':1,'ref_lon':2,'ref_alt':3}))
    (tmp_path/'p.json').write_text(json.dumps({'datasets':[{'product':'WMM2025','provider':'NOAA','source_url':'u','sha256':'x','license_note':'n'}]}))
    build_markdown_report(tmp_path/'s.csv',tmp_path/'m.json',tmp_path/'p.json',tmp_path/'r.md')
    assert 'Public-Data Benchmark' in (tmp_path/'r.md').read_text()
