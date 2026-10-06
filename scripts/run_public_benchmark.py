#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from gravity_nav.benchmark import run_public_benchmark, save_public_benchmark
from gravity_nav.public_data import DataProvenance, write_provenance, sha256_file, NGA_EGM2008_PAGE, NOAA_WMM_PAGE
from gravity_nav.benchmark_reporting import build_markdown_report
p=argparse.ArgumentParser(); p.add_argument('--gravity',required=True); p.add_argument('--magnetic',required=True); p.add_argument('--scenario',default='configs/real_data_validation.yaml'); p.add_argument('--ref-lat',type=float,default=33.4484); p.add_argument('--ref-lon',type=float,default=-112.0740); p.add_argument('--ref-alt',type=float,default=350); p.add_argument('--runs',type=int,default=30); p.add_argument('--profile',default='tactical'); p.add_argument('--out-dir',default='benchmark/reports/golden'); a=p.parse_args()
r=run_public_benchmark(scenario_config=a.scenario,gravity_csv=a.gravity,magnetic_csv=a.magnetic,ref_lat=a.ref_lat,ref_lon=a.ref_lon,ref_alt=a.ref_alt,runs=a.runs,profile=a.profile)
save_public_benchmark(r,a.out_dir)
out=Path(a.out_dir)
write_provenance(out/'provenance.json',DataProvenance('NGA Office of Geomatics','EGM2008',NGA_EGM2008_PAGE,license_note='User-acquired/cropped source data; verify NGA terms and provenance.',sha256=sha256_file(a.gravity)),DataProvenance('NOAA NCEI / NGA / DGC / BGS','WMM2025',NOAA_WMM_PAGE,license_note='NOAA states WMM source code is public domain; model citation retained.',sha256=sha256_file(a.magnetic)),extra=r.metadata)
build_markdown_report(out/'benchmark_summary.csv',out/'benchmark_metadata.json',out/'provenance.json',out/'BENCHMARK_REPORT.md')
print(r.summary.to_string(index=False)); print(f'report: {out/"BENCHMARK_REPORT.md"}')
