from __future__ import annotations
from pathlib import Path
import yaml
from .assured_pnt import AssuredPNTConfig


def load_config(path: str | Path) -> AssuredPNTConfig:
    data=yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if "scenario" in data: data=data["scenario"]
    return AssuredPNTConfig(**data)
