from __future__ import annotations

from datetime import date
from pathlib import Path

from proto.features.escalation_features import build_escalation_features
from proto.features.gdelt_features import build_tension_features
from proto.features.vulnerability_features import build_vulnerability_features
from proto.sources.bridge import load_bridge_records
from proto.sources.context import load_context_records
from proto.sources.gdelt import load_gdelt_records
from proto.sources.ucdp import load_ucdp_records

COUNTRIES = [
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
]


def test_build_tension_features_from_gdelt_and_bridge():
    """
    Traceability:
    - PSwR-007
    - ALG-001
    - TV-PSwR-007-001
    """
    gdelt_records = load_gdelt_records(Path("data/gdelt/gdelt_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    features = build_tension_features(
        gdelt_records,
        bridge_records,
        countries=COUNTRIES,
    )

    assert len(features) == 10680
    germany_latest_protest = [
        feature
        for feature in features
        if feature.country == "Germany"
        and feature.date == date(2026, 4, 12)
        and feature.feature_name == "protest_signal"
    ]
    assert len(germany_latest_protest) == 1
    assert 0.0 <= germany_latest_protest[0].feature_value <= 100.0

    features_without_bridge = build_tension_features(
        gdelt_records,
        [],
        countries=COUNTRIES,
    )
    with_bridge = next(
        item
        for item in features
        if item.country == "Poland"
        and item.date == date(2025, 12, 5)
        and item.feature_name == "protest_signal"
    ).feature_value
    without_bridge = next(
        item
        for item in features_without_bridge
        if item.country == "Poland"
        and item.date == date(2025, 12, 5)
        and item.feature_name == "protest_signal"
    ).feature_value
    assert with_bridge > without_bridge


def test_build_escalation_features_internal_and_external():
    """
    Traceability:
    - PSwR-008
    - PSyR-004
    - ALG-002
    - TV-PSwR-008-001
    """
    ucdp_records = load_ucdp_records(Path("data/ucdp/ucdp_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    features = build_escalation_features(
        ucdp_records,
        bridge_records,
        countries=COUNTRIES,
    )

    assert len(features) == 21360
    iran_bridge_day = [
        feature
        for feature in features
        if feature.country == "Ukraine"
        and feature.date == date(2025, 11, 10)
        and feature.feature_name == "war_activity_signal"
    ]
    assert len(iran_bridge_day) == 1
    assert 0.0 <= iran_bridge_day[0].feature_value <= 100.0


def test_build_vulnerability_features_from_context():
    """
    Traceability:
    - PSwR-009
    - ALG-003
    - TV-PSwR-009-001
    """
    context_records = load_context_records(Path("data/context/country_context.csv"))
    features = build_vulnerability_features(
        context_records,
        countries=COUNTRIES,
        feature_date=date(2026, 1, 20),
    )

    assert len(features) == 30
    germany_governance = [
        feature
        for feature in features
        if feature.country == "Germany"
        and feature.feature_name == "governance_stress_signal"
    ]
    assert len(germany_governance) == 1
    assert germany_governance[0].feature_value == 44.7
