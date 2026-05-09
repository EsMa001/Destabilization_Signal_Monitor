from __future__ import annotations

"""
Configuration access helpers for API layer.

Traceability:
- AP-03
- AP-08
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from proto.pipeline.config import PipelineConfig, load_pipeline_config

CONFIG_PATH = Path("config/default.yaml")
DEFAULT_HORIZONS = [7, 30, 356]


@lru_cache(maxsize=1)
def get_pipeline_config() -> PipelineConfig:
    return load_pipeline_config(CONFIG_PATH)


@lru_cache(maxsize=1)
def get_raw_config() -> dict[str, Any]:
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return {}


def countries_options() -> list[dict[str, str]]:
    config = get_pipeline_config()
    return [{"code": country, "label": country} for country in config.countries]


def layer_options() -> list[dict[str, str]]:
    config = get_pipeline_config()
    return [
        {
            "key": layer,
            "label": layer.replace("_", " ").title(),
            "description": f"{layer.replace('_', ' ').title()} layer",
        }
        for layer in config.v3_1.fusion.groups
    ]


def config_template() -> dict[str, object]:
    config = get_pipeline_config()
    default_countries = config.countries[:3]
    preferred_layers = [layer for layer in ("event", "market_food", "governance") if layer in config.v3_1.fusion.groups]
    return {
        "countries": countries_options(),
        "layers": layer_options(),
        "horizons": DEFAULT_HORIZONS,
        "defaults": {
            "horizon_days": config.recent_days,
            "countries": default_countries,
            "layers": preferred_layers or config.v3_1.fusion.groups[:3],
        },
        "versions": {
            "query_version": config.query_version,
            "scoring_version": config.scoring_version,
            "bridge_file_version": config.bridge_file_version,
            "context_table_version": config.context_table_version,
        },
    }

