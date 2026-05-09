from __future__ import annotations

"""
Options/config API schemas.

Traceability:
- AP-03
- AP-06
"""

from pydantic import BaseModel, Field


class CountryOption(BaseModel):
    code: str
    label: str


class LayerOption(BaseModel):
    key: str
    label: str
    description: str | None = None


class CountriesOptionsResponse(BaseModel):
    countries: list[CountryOption]


class LayersOptionsResponse(BaseModel):
    layers: list[LayerOption]


class ConfigTemplateDefaults(BaseModel):
    horizon_days: int
    countries: list[str]
    layers: list[str]


class ConfigTemplateResponse(BaseModel):
    countries: list[CountryOption]
    layers: list[LayerOption]
    horizons: list[int] = Field(description="Supported analysis horizons.")
    defaults: ConfigTemplateDefaults
    versions: dict[str, str]

