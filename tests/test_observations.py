from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from proto.observations.adapter_contract import AdapterContractError, enforce_adapter_contract
from proto.observations.models import ObservationRecord
from proto.observations.normalization import normalize_series
from proto.observations.schema import ObservationValidationError, validate_observation_record
from proto.sources.gdacs import load_gdacs_observations
from proto.sources.gdelt_event import load_gdelt_event_observations
from proto.sources.governance_input import load_governance_input_observations
from proto.sources.narrative_input import load_narrative_input_observations
from proto.sources.unhcr import load_unhcr_observations


def _valid_observation(*, source_id: str = "fao_ffpi") -> ObservationRecord:
    return ObservationRecord(
        source_id=source_id,
        layer="Market/Food",
        signal_family="ffpi_price_index",
        country="Iran",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 1, 31),
        raw_value=130.0,
        normalized_value=0.8,
        unit="index_points",
        provenance="FAO_FFPI_snapshot_2026Q1",
        quality_completeness=0.95,
        native_periodicity="monthly",
    )


def test_canonical_observation_schema_validation_enforces_required_ranges():
    """
    Traceability:
    - PSyR-018
    - PSwR-036
    - PSwR-037
    - TV-PSwR-036-001
    """
    record = _valid_observation()
    validate_observation_record(record)

    with pytest.raises(ObservationValidationError):
        validate_observation_record(
            ObservationRecord(
                source_id="fao_ffpi",
                layer="Market/Food",
                signal_family="ffpi_price_index",
                country="Iran",
                period_start=date(2026, 2, 1),
                period_end=date(2026, 1, 31),
                raw_value=130.0,
                normalized_value=0.8,
                unit="index_points",
                provenance="x",
                quality_completeness=0.95,
            )
        )
    with pytest.raises(ObservationValidationError):
        validate_observation_record(
            ObservationRecord(
                source_id="fao_ffpi",
                layer="Market/Food",
                signal_family="ffpi_price_index",
                country="Iran",
                period_start=date(2026, 1, 1),
                period_end=date(2026, 1, 31),
                raw_value=130.0,
                normalized_value=1.2,
                unit="index_points",
                provenance="x",
                quality_completeness=0.95,
            )
        )


def test_observation_schema_supports_mixed_native_periods():
    """
    Traceability:
    - PSyR-022
    - PSwR-038
    - TV-PSwR-038-001
    """
    monthly = _valid_observation()
    yearly = ObservationRecord(
        source_id="un_comtrade",
        layer="Structural",
        signal_family="trade_dependency_exposure",
        country="Iran",
        period_start=date(2025, 1, 1),
        period_end=date(2025, 12, 31),
        raw_value=0.68,
        normalized_value=0.94,
        unit="dependency_share",
        provenance="UN_COMTRADE_snapshot_2025",
        quality_completeness=0.88,
        native_periodicity="annual",
    )
    validate_observation_record(monthly)
    validate_observation_record(yearly)


def test_adapter_contract_enforces_source_consistency():
    """
    Traceability:
    - PSwR-039
    - TV-PSwR-039-001
    """
    with pytest.raises(AdapterContractError):
        enforce_adapter_contract(
            source_id="fao_ffpi",
            observations=[_valid_observation(source_id="fao_fpma")],
        )


def test_normalization_methods_map_to_zero_one():
    """
    Traceability:
    - PSwR-040
    - ALG-013
    - TV-PSwR-040-002
    """
    values = [10.0, 20.0, 30.0]
    z_score = normalize_series(values, method="z_score")
    percentile = normalize_series(values, method="percentile")
    baseline = normalize_series(values, method="baseline_deviation", baseline_value=10.0, baseline_scale=20.0)

    assert all(0.0 <= value <= 1.0 for value in z_score)
    assert percentile == [0.0, 0.5, 1.0]
    assert baseline == [0.0, 0.5, 1.0]


def test_new_v32_observation_layers_are_validated_with_native_periods():
    """
    Traceability:
    - PSyR-024
    - PSyR-025
    - PSyR-026
    - PSwR-037
    - PSwR-038
    - TV-PSwR-056-001
    """
    gdacs = load_gdacs_observations(
        path=Path("data/gdacs/gdacs_events.csv"),
        normalization_method="z_score",
    )
    unhcr = load_unhcr_observations(
        path=Path("data/unhcr/unhcr_displacement.csv"),
        normalization_method="percentile",
    )
    narrative = load_narrative_input_observations(
        path=Path("data/narrative_input/narrative_input.csv"),
        normalization_method="percentile",
    )
    assert gdacs and unhcr and narrative
    assert all(record.layer == "Shock" for record in gdacs)
    assert all(record.layer == "Displacement" for record in unhcr)
    assert all(record.layer == "Narrative" for record in narrative)
    assert all(record.native_periodicity == "monthly" for record in gdacs + unhcr + narrative)
    for record in gdacs + unhcr + narrative:
        validate_observation_record(record)


def test_event_observations_include_event_metadata_and_validate():
    """
    Traceability:
    - PSyR-029
    - PSwR-071
    - PSwR-072
    - PSwR-037
    - PSwR-044
    - TV-PSwR-071-002
    """
    event_observations = load_gdelt_event_observations(
        path=Path("data/gdelt/gdelt_events.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    assert event_observations
    assert all(record.layer == "Event" for record in event_observations)
    assert all(record.native_periodicity == "monthly" for record in event_observations)
    for record in event_observations:
        validate_observation_record(record)
        assert record.metadata["event_count"] >= 1
        assert record.metadata["unique_event_types"] >= 1
        assert 0.0 <= float(record.metadata["category_coverage"]) <= 1.0


def test_governance_observations_are_schema_valid_and_include_provenance():
    """
    Traceability:
    - PSyR-034
    - PSwR-037
    - PSwR-044
    - PSwR-091
    - PSwR-092
    - TV-PSwR-091-002
    """
    governance_observations = load_governance_input_observations(
        path=Path("data/governance_input/governance_input.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    assert governance_observations
    assert all(record.layer == "Governance" for record in governance_observations)
    assert all(record.source_id == "governance_input" for record in governance_observations)
    assert all(record.native_periodicity == "monthly" for record in governance_observations)
    for record in governance_observations:
        validate_observation_record(record)
        assert record.provenance.startswith("GOVERNANCE_snapshot_")
        assert 0.0 <= float(record.metadata["government_effectiveness"]) <= 1.0
        assert 0.0 <= float(record.metadata["resilience_buffer"]) <= 1.0
