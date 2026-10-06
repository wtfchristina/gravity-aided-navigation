from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd
from .config import load_config
from .sensor_profiles import apply_profile
from .geogrid import GeoGridMap, LocalENUFieldMap
from .validation import compare_modes, summarize_validation

@dataclass
class PublicBenchmarkResult:
    raw: pd.DataFrame
    summary: pd.DataFrame
    metadata: dict


def run_public_benchmark(*,scenario_config:str,gravity_csv:str,magnetic_csv:str,
                         ref_lat:float,ref_lon:float,ref_alt:float=0.0,runs:int=30,
                         profile:str='tactical')->PublicBenchmarkResult:
    cfg=load_config(scenario_config)
    cfg=apply_profile(cfg,profile)
    gg=GeoGridMap.from_csv(gravity_csv,'gravity_public','source_units')
    mg=GeoGridMap.from_csv(magnetic_csv,'magnetic_public','nT')
    gmap=LocalENUFieldMap(gg,ref_lat,ref_lon,ref_alt)
    mmap=LocalENUFieldMap(mg,ref_lat,ref_lon,ref_alt)
    raw=compare_modes(cfg,runs,gravity_map=gmap,magnetic_map=mmap)
    summary=summarize_validation(raw)
    meta={'scenario_config':scenario_config,'runs':runs,'profile':profile,'ref_lat':ref_lat,'ref_lon':ref_lon,'ref_alt':ref_alt}
    return PublicBenchmarkResult(raw,summary,meta)


def save_public_benchmark(result:PublicBenchmarkResult,out_dir:str|Path):
    p=Path(out_dir); p.mkdir(parents=True,exist_ok=True)
    result.raw.to_csv(p/'benchmark_runs.csv',index=False)
    result.summary.to_csv(p/'benchmark_summary.csv',index=False)
    (p/'benchmark_metadata.json').write_text(json.dumps(result.metadata,indent=2),encoding='utf-8')
