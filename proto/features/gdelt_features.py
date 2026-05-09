from __future__ import annotations

"""
Traceability:
- PSwR-007
- PSwR-001
- ALG-001
- FeatureSpec: Spannung
"""

from collections import defaultdict
from datetime import date
from statistics import mean

from proto.common import canonical_country, sorted_unique_dates
from proto.models import FeatureRecord, SourceRecord
from proto.sources.bridge import BridgeRecord

GDELT_CATEGORY_TO_FEATURE = {
    "protest": "protest_signal",
    "crisis": "crisis_discourse_signal",
    "negativity": "negativity_signal",
    "stability": "stability_signal",
}

BRIDGE_EVENT_TO_FEATURE = {
    "protest_marker": "protest_signal",
    "crisis_marker": "crisis_discourse_signal",
    "negativity_marker": "negativity_signal",
}

MANDATORY_TENSION_FEATURES = [
    "protest_signal",
    "crisis_discourse_signal",
    "negativity_signal",
]


def _clamp_score(value: float) -> float:
    # Traceability:
    # - PSwR-007
    # - PSwR-001
    # - ALG-001
    # - PM-001
    # - PM-005
    return max(0.0, min(100.0, value))


def build_tension_features(
    gdelt_records: list[SourceRecord],
    bridge_records: list[BridgeRecord],
    *,
    countries: list[str],
) -> list[FeatureRecord]:
    """
    Build daily tension features from GDELT (+ bridge marker uplift).

    Traceability:
    - PSwR-007
    - ALG-001
    - PM-001
    - PM-005
    """
    normalized_countries = {canonical_country(country) for country in countries}
    raw_feature_values: dict[tuple[str, date, str], list[float]] = defaultdict(list)
    bridge_uplift: dict[tuple[str, date, str], float] = defaultdict(float)
    all_dates_by_country: dict[str, list[date]] = defaultdict(list)

    for record in gdelt_records:
        country = canonical_country(record.country)
        if country not in normalized_countries:
            continue
        feature_name = GDELT_CATEGORY_TO_FEATURE.get(record.category)
        if feature_name is None:
            continue
        key = (country, record.date, feature_name)
        raw_feature_values[key].append(record.raw_value)
        all_dates_by_country[country].append(record.date)

    for bridge_record in bridge_records:
        if not bridge_record.include_in_cluster:
            continue
        if bridge_record.cluster != "tension":
            continue
        country = canonical_country(bridge_record.country)
        if country not in normalized_countries:
            continue
        feature_name = BRIDGE_EVENT_TO_FEATURE.get(bridge_record.event_type)
        if feature_name is None:
            continue
        key = (country, bridge_record.date, feature_name)
        bridge_uplift[key] += bridge_record.severity * 100.0
        all_dates_by_country[country].append(bridge_record.date)

    output: list[FeatureRecord] = []
    for country in sorted(normalized_countries):
        feature_names = list(MANDATORY_TENSION_FEATURES)
        if any(key[2] == "stability_signal" for key in raw_feature_values):
            feature_names.append("stability_signal")

        for feature_date in sorted_unique_dates(all_dates_by_country.get(country, [])):
            for feature_name in feature_names:
                key = (country, feature_date, feature_name)
                base_value = mean(raw_feature_values.get(key, [0.0]))
                uplift_value = bridge_uplift.get(key, 0.0)
                feature_value = _clamp_score(base_value + uplift_value)
                output.append(
                    FeatureRecord(
                        feature_id=f"{country}-{feature_date.isoformat()}-{feature_name}",
                        country=country,
                        date=feature_date,
                        cluster="tension",
                        subcluster="na",
                        feature_name=feature_name,
                        feature_value=feature_value,
                    )
                )
    return output
