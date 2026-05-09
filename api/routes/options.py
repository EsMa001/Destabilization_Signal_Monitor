from __future__ import annotations

"""
Options/config routes.

Traceability:
- AP-03
"""

from fastapi import APIRouter

from api.schemas.options import (
    ConfigTemplateResponse,
    CountriesOptionsResponse,
    LayersOptionsResponse,
)
from api.services.config_service import config_template, countries_options, layer_options

router = APIRouter()


@router.get("/options/countries", response_model=CountriesOptionsResponse)
def get_options_countries() -> CountriesOptionsResponse:
    return CountriesOptionsResponse(countries=countries_options())


@router.get("/options/layers", response_model=LayersOptionsResponse)
def get_options_layers() -> LayersOptionsResponse:
    return LayersOptionsResponse(layers=layer_options())


@router.get("/config/template", response_model=ConfigTemplateResponse)
def get_config_template() -> ConfigTemplateResponse:
    payload = config_template()
    return ConfigTemplateResponse(**payload)

