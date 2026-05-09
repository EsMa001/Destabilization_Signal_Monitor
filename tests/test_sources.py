from pathlib import Path
from datetime import date

from proto.sources.bridge import load_bridge_records
from proto.sources.context import load_context_records
from proto.sources.fao_ffpi import load_fao_ffpi_observations, load_fao_ffpi_records
from proto.sources.fao_fpma import load_fao_fpma_observations, load_fao_fpma_records
from proto.sources.gdacs import load_gdacs_observations, load_gdacs_records
from proto.sources.gdelt_event import (
    load_gdelt_event_observations,
    load_gdelt_event_records,
    load_gdelt_event_rows,
)
from proto.sources.gdelt import load_gdelt_records
from proto.sources.governance_input import (
    load_governance_input_observations,
    load_governance_input_records,
)
from proto.sources.narrative_input import (
    load_narrative_input_observations,
    load_narrative_input_records,
)
from proto.sources.unhcr import load_unhcr_observations, load_unhcr_records
from proto.sources.un_comtrade import load_un_comtrade_observations, load_un_comtrade_records
from proto.sources.ucdp import load_ucdp_records

COUNTRIES = {
    "Germany",
    "Israel",
    "Iran",
    "Ukraine",
    "Russia",
    "Japan",
    "China",
    "Taiwan",
    "Poland",
    "Nigeria",
}


def test_load_gdelt_records():
    """
    Traceability:
    - PSwR-003
    - PSwR-001
    - TV-PSwR-003-001
    """
    records = load_gdelt_records(Path("data/gdelt/gdelt_events.csv"))
    assert len(records) == 10680
    assert records[0].source_id == "gdelt"
    assert records[0].country == "Germany"
    assert records[0].date == date(2025, 4, 22)
    assert records[0].category == "protest"
    assert set(record.country for record in records) == COUNTRIES


def test_load_gdelt_event_records_and_observations():
    """
    Traceability:
    - PSyR-029
    - PSwR-071
    - PSwR-072
    - PSwR-039
    - TV-PSwR-071-001
    """
    rows = load_gdelt_event_rows(Path("data/gdelt/gdelt_events.csv"))
    records = load_gdelt_event_records(Path("data/gdelt/gdelt_events.csv"))
    observations = load_gdelt_event_observations(
        Path("data/gdelt/gdelt_events.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    assert len(rows) == 10680
    assert len(records) == 130
    assert len(observations) == 130
    assert all(item.source_id == "gdelt_event" for item in observations)
    assert all(item.layer == "Event" for item in observations)
    assert all(item.native_periodicity == "monthly" for item in observations)
    assert all(item.metadata["event_count"] >= 1 for item in observations)
    assert all(0.0 <= item.normalized_value <= 1.0 for item in observations)
    assert set(item.country for item in observations) == COUNTRIES


def test_load_ucdp_records():
    """
    Traceability:
    - PSwR-004
    - PSwR-001
    - TV-PSwR-004-001
    """
    records = load_ucdp_records(Path("data/ucdp/ucdp_events.csv"))
    assert len(records) == 21360
    assert records[0].source_id == "ucdp"
    assert records[0].country == "Germany"
    assert records[0].date == date(2025, 4, 22)
    assert records[0].category == "internal_violence"
    assert set(record.country for record in records) == COUNTRIES

def test_load_bridge_records():
    """
    Traceability:
    - PSwR-005
    - TV-PSwR-005-001
    """
    records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    assert len(records) >= 1
    assert records[0].date == date(2025, 11, 10)
    assert records[0].cluster == "escalation"
    assert records[0].include_in_cluster is True

def test_load_context_records():
    """
    Traceability:
    - PSwR-006
    - TV-PSwR-006-001
    """
    records = load_context_records(Path("data/context/country_context.csv"))
    assert len(records) == 10


def test_load_fao_ffpi_records_and_observations():
    """
    Traceability:
    - PSwR-048
    - PSwR-039
    - TV-PSwR-048-001
    """
    records = load_fao_ffpi_records(Path("data/fao_ffpi/fao_ffpi.csv"))
    observations = load_fao_ffpi_observations(
        Path("data/fao_ffpi/fao_ffpi.csv"),
        normalization_method="z_score",
    )
    assert len(records) == 120
    assert len(observations) == 120
    assert observations[0].source_id == "fao_ffpi"
    assert observations[0].layer == "Market/Food"
    assert 0.0 <= observations[0].normalized_value <= 1.0
    assert set(item.country for item in observations) == COUNTRIES


def test_load_fao_fpma_records_and_observations():
    """
    Traceability:
    - PSwR-049
    - PSwR-039
    - TV-PSwR-049-001
    """
    records = load_fao_fpma_records(Path("data/fao_fpma/fao_fpma.csv"))
    observations = load_fao_fpma_observations(
        Path("data/fao_fpma/fao_fpma.csv"),
        normalization_method="percentile",
    )
    assert len(records) == 120
    assert len(observations) == 120
    assert observations[0].source_id == "fao_fpma"
    assert observations[0].layer == "Market/Food"
    assert 0.0 <= observations[0].normalized_value <= 1.0
    assert set(item.country for item in observations) == COUNTRIES


def test_load_un_comtrade_records_and_observations():
    """
    Traceability:
    - PSwR-050
    - PSwR-039
    - TV-PSwR-050-001
    """
    records = load_un_comtrade_records(Path("data/un_comtrade/un_comtrade.csv"))
    observations = load_un_comtrade_observations(
        Path("data/un_comtrade/un_comtrade.csv"),
        normalization_method="baseline_deviation",
        baseline_value=0.35,
        baseline_scale=0.35,
    )
    assert len(records) == 20
    assert len(observations) == 20
    assert observations[0].source_id == "un_comtrade"
    assert observations[0].layer == "Structural"
    assert 0.0 <= observations[0].normalized_value <= 1.0
    assert set(item.country for item in observations) == COUNTRIES


def test_load_gdacs_records_and_observations():
    """
    Traceability:
    - PSwR-059
    - PSwR-039
    - TV-PSwR-059-001
    """
    records = load_gdacs_records(Path("data/gdacs/gdacs_events.csv"))
    observations = load_gdacs_observations(
        Path("data/gdacs/gdacs_events.csv"),
        normalization_method="z_score",
    )
    assert len(records) == 120
    assert len(observations) == 120
    assert observations[0].source_id == "gdacs"
    assert observations[0].layer == "Shock"
    assert observations[0].native_periodicity == "monthly"
    assert 0.0 <= observations[0].normalized_value <= 1.0
    assert set(item.country for item in observations) == COUNTRIES


def test_load_unhcr_records_and_observations():
    """
    Traceability:
    - PSwR-060
    - PSwR-039
    - TV-PSwR-060-001
    """
    records = load_unhcr_records(Path("data/unhcr/unhcr_displacement.csv"))
    observations = load_unhcr_observations(
        Path("data/unhcr/unhcr_displacement.csv"),
        normalization_method="percentile",
    )
    assert len(records) == 120
    assert len(observations) == 120
    assert observations[0].source_id == "unhcr"
    assert observations[0].layer == "Displacement"
    assert observations[0].native_periodicity == "monthly"
    assert 0.0 <= observations[0].normalized_value <= 1.0
    assert set(item.country for item in observations) == COUNTRIES


def test_load_narrative_input_records_and_observations():
    """
    Traceability:
    - PSwR-061
    - PSwR-039
    - TV-PSwR-061-001
    """
    records = load_narrative_input_records(Path("data/narrative_input/narrative_input.csv"))
    observations = load_narrative_input_observations(
        Path("data/narrative_input/narrative_input.csv"),
        normalization_method="percentile",
    )
    assert len(records) == 120
    assert len(observations) == 120
    assert observations[0].source_id == "narrative_input"
    assert observations[0].layer == "Narrative"
    assert observations[0].native_periodicity == "monthly"
    assert observations[0].metadata["topic"]
    assert observations[0].metadata["narrative_direction"]
    assert 0.0 <= observations[0].normalized_value <= 1.0
    assert set(item.country for item in observations) == COUNTRIES


def test_load_governance_input_records_and_observations():
    """
    Traceability:
    - PSyR-034
    - PSwR-091
    - PSwR-092
    - PSwR-039
    - TV-PSwR-091-001
    """
    records = load_governance_input_records(
        Path("data/governance_input/governance_input.csv")
    )
    observations = load_governance_input_observations(
        Path("data/governance_input/governance_input.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    assert len(records) == 120
    assert len(observations) == 120
    assert observations[0].source_id == "governance_input"
    assert observations[0].layer == "Governance"
    assert observations[0].native_periodicity == "monthly"
    assert observations[0].metadata["government_effectiveness"] >= 0.0
    assert observations[0].metadata["policy_blockage"] >= 0.0
    assert 0.0 <= observations[0].normalized_value <= 1.0


def test_unhcr_global_normalization_produces_plausible_country_ordering():
    """
    Traceability:
    - PSyR-025
    - PSwR-060
    - PSwR-040
    - ALG-019
    - TV-PSwR-060-002
    """
    observations = load_unhcr_observations(
        Path("data/unhcr/unhcr_displacement.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    latest_by_country = {}
    for item in observations:
        previous = latest_by_country.get(item.country)
        if previous is None or item.period_end > previous.period_end:
            latest_by_country[item.country] = item
    germany = latest_by_country["Germany"].normalized_value
    israel = latest_by_country["Israel"].normalized_value
    iran = latest_by_country["Iran"].normalized_value
    assert germany < israel < iran
    assert latest_by_country["Germany"].metadata["normalization_scope"] == "global"


def test_narrative_global_normalization_avoids_trivial_all_country_saturation():
    """
    Traceability:
    - PSyR-026
    - PSwR-061
    - PSwR-040
    - ALG-020
    - TV-PSwR-061-002
    """
    observations = load_narrative_input_observations(
        Path("data/narrative_input/narrative_input.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    latest_by_country = {}
    for item in observations:
        previous = latest_by_country.get(item.country)
        if previous is None or item.period_end > previous.period_end:
            latest_by_country[item.country] = item
    latest_values = [item.normalized_value for item in latest_by_country.values()]
    assert len({round(value, 4) for value in latest_values}) >= 8
    assert max(latest_values) <= 1.0
    assert min(latest_values) >= 0.0
    assert all(item.metadata["normalization_scope"] == "global" for item in latest_by_country.values())


def test_gdelt_event_global_normalization_produces_country_differentiation():
    """
    Traceability:
    - PSyR-029
    - PSwR-072
    - PSwR-040
    - ALG-023
    - ALG-024
    - TV-PSwR-072-001
    """
    observations = load_gdelt_event_observations(
        Path("data/gdelt/gdelt_events.csv"),
        normalization_method="z_score",
        normalization_scope="global",
    )
    by_country = {item.country: item for item in observations}
    assert set(by_country.keys()) == COUNTRIES
    assert by_country["Iran"].normalized_value > by_country["Israel"].normalized_value
    assert by_country["Israel"].normalized_value > by_country["Germany"].normalized_value
    assert by_country["Nigeria"].normalized_value > by_country["Japan"].normalized_value
