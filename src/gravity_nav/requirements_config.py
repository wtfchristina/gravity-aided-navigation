from __future__ import annotations
from pathlib import Path
import yaml
from .assured_pnt import AssuredPNTConfig
from .requirements import MissionRequirement


def load_mission_requirement(path: str | Path):
    data=yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}
    return AssuredPNTConfig(**data.get('scenario',{})), MissionRequirement(**data.get('requirement',{}))
