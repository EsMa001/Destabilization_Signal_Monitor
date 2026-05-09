from __future__ import annotations

"""
Traceability:
- PSwR-008
- PSwR-001
- ALG-002
- FeatureSpec: Eskalation intern/extern
"""

from collections import defaultdict
from datetime import date
from statistics import mean

from proto.common import canonical_country, sorted_unique_dates
from proto.models import FeatureRecord, SourceRecord
from proto.sources.bridge import BridgeRecord

UCDP_CATEGORY_TO_FEATURE = {
    "internal_violence": ("internal", "internal_violence_signal"),
    "repression": ("internal", "repression_signal"),
    "domestic_attack": ("internal", "domestic_attack_signal"),
    "war_activity": ("external", "war_activity_signal"),
    "external_attack": ("external", "external_attack_signal"),
    "regional_spillover": ("external", "regional_spillover_signal"),
}

MANDATORY_ESCALATION_FEATURES = {
    "internal": [
        "internal_violence_signal",
        "repression_signal",
        "domestic_attack_signal",
    ],
    "external": [
        "war_activity_signal",
        "external_attack_signal",
        "regional_spillover_signal",
    ],
}

BRIDGE_SUBCLUSTER_DEFAULT_FEATURE = {
    "internal": "internal_violence_signal",
    "external": "war_activity_signal",
}


def _clamp_score(value: float) -> float:
    # Traceability:
    # - PSwR-008
    # - PSwR-001
    # - ALG-002
    # - PSyR-004
    # - PM-001
    # - PM-005
    return max(0.0, min(100.0, value))


def build_escalation_features(
    ucdp_records: list[SourceRecord],
    bridge_records: list[BridgeRecord],
    *,
    countries: list[str],
) -> list[FeatureRecord]:
    """
    Build daily internal/external escalation features.

    Traceability:
    - PSwR-008
    - PSyR-004
    - ALG-002
    - PM-001
    - PM-005
    """
    normalized_countries = {canonical_country(country) for country in countries}
    raw_feature_values: dict[tuple[str, date, str, str], list[float]] = defaultdict(list)
    bridge_uplift: dict[tuple[str, date, str, str], float] = defaultdict(float)
    all_dates_by_country: dict[str, list[date]] = defaultdict(list)

    for record in ucdp_records:
        country = canonical_country(record.country)
        if country not in normalized_countries:
            continue
        mapping = UCDP_CATEGORY_TO_FEATURE.get(record.category)
        if mapping is None:
            continue
        subcluster, feature_name = mapping
        key = (country, record.date, subcluster, feature_name)
        raw_feature_values[key].append(record.raw_value)
        all_dates_by_country[country].append(record.date)

    for bridge_record in bridge_records:
        if not bridge_record.include_in_cluster:
            continue
        if bridge_record.cluster != "escalation":
            continue
        country = canonical_country(bridge_record.country)
        if country not in normalized_countries:
            continue
        subcluster = bridge_record.subcluster if bridge_record.subcluster in {"internal", "external"} else "external"
        feature_name = BRIDGE_SUBCLUSTER_DEFAULT_FEATURE[subcluster]
        key = (country, bridge_record.date, subcluster, feature_name)
        bridge_uplift[key] += bridge_record.severity * 100.0
        all_dates_by_country[country].append(bridge_record.date)

    output: list[FeatureRecord] = []
    for country in sorted(normalized_countries):
        for feature_date in sorted_unique_dates(all_dates_by_country.get(country, [])):
            for subcluster, feature_names in MANDATORY_ESCALATION_FEATURES.items():
                for feature_name in feature_names:
                    key = (country, feature_date, subcluster, feature_name)
                    base_value = mean(raw_feature_values.get(key, [0.0]))
                    uplift_value = bridge_uplift.get(key, 0.0)
                    feature_value = _clamp_score(base_value + uplift_value)
                    output.append(
                        FeatureRecord(
                            feature_id=f"{country}-{feature_date.isoformat()}-{subcluster}-{feature_name}",
                            country=country,
                            date=feature_date,
                            cluster="escalation",
                            subcluster=subcluster,
                            feature_name=feature_name,
                            feature_value=feature_value,
                        )
                    )
    return output
