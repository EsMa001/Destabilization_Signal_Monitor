from __future__ import annotations

"""
Fusion-path records for V3.1 layer/group outputs.

Traceability:
- PSyR-019
- PSyR-020
- PSwR-045
- PSwR-046
- PSwR-056
- PSwR-062
- PSwR-063
- PSwR-066
- PM-020
- PM-021
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FusionSourceSignalRecord:
    """
    Source-level normalized signal selected for fusion target period.

    Traceability:
    - PSwR-040
    - PSwR-043
    - PSwR-044
    """

    country: str
    source_id: str
    group: str
    layer: str
    signal_family: str
    target_period_start: date
    target_period_end: date
    native_period_start: date
    native_period_end: date
    raw_value: float
    normalized_value: float
    unit: str
    provenance: str
    quality_completeness: float
    age_days: int


@dataclass(frozen=True)
class FusionGroupScoreRecord:
    """
    Group score for one country in one target period.

    Traceability:
    - PSwR-041
    - PSwR-045
    - PSwR-046
    """

    country: str
    group: str
    target_period_start: date
    target_period_end: date
    group_score: float | None
    status: str
    source_count: int
    expected_source_count: int
    source_coverage_ratio: float
    confidence_score: float
    confidence_level: str
    coverage_component: float
    recency_component: float
    completeness_component: float
    consistency_component: float
    sources_used: str


@dataclass(frozen=True)
class FusionTotalScoreRecord:
    """
    Parallel fusion total score for one country.

    Traceability:
    - PSwR-042
    - PSwR-045
    """

    country: str
    target_period_start: date
    target_period_end: date
    fusion_score: float
    confidence_score: float
    confidence_level: str
    group_count: int
    expected_group_count: int
    available_group_count: int
    available_group_ratio: float
    confidence_coverage_component: float
    confidence_recency_component: float
    confidence_completeness_component: float
    confidence_consistency_component: float
    confidence_dominance_penalty: float
    confidence_limited_penalty: float
    dominant_group_contribution_share: float
    groups_used: str
    bonus_applied: bool
    bonus_points: float


@dataclass(frozen=True)
class FusionHistoricalSourceSignalRecord:
    """
    Historical source-level signal per country/period.

    Traceability:
    - PSwR-056
    - PSwR-057
    """

    country: str
    source_id: str
    group: str
    layer: str
    period_label: str
    target_period_start: date
    target_period_end: date
    native_period_start: date
    native_period_end: date
    normalized_value: float
    raw_value: float
    provenance: str
    quality_completeness: float
    age_days: int


@dataclass(frozen=True)
class FusionHistoricalGroupScoreRecord:
    """
    Historical fusion group score per country/period.

    Traceability:
    - PSwR-056
    - PSwR-062
    - PSwR-066
    """

    country: str
    group: str
    period_label: str
    target_period_start: date
    target_period_end: date
    group_score: float | None
    status: str
    source_count: int
    expected_source_count: int
    source_coverage_ratio: float
    confidence_score: float
    confidence_level: str
    sources_used: str


@dataclass(frozen=True)
class FusionHistoricalTotalScoreRecord:
    """
    Historical fusion total score per country/period.

    Traceability:
    - PSwR-056
    - PSwR-063
    - PSwR-066
    """

    country: str
    period_label: str
    target_period_start: date
    target_period_end: date
    fusion_score: float
    stage: str
    trend: str
    confidence_score: float
    confidence_level: str
    group_count: int
    expected_group_count: int
    available_group_count: int
    available_group_ratio: float
    confidence_coverage_component: float
    confidence_recency_component: float
    confidence_completeness_component: float
    confidence_consistency_component: float
    confidence_dominance_penalty: float
    confidence_limited_penalty: float
    dominant_group_contribution_share: float
    groups_used: str
    dominant_group: str | None
    dominant_group_delta: float | None
    top_positive_group_1: str | None
    top_positive_group_1_contribution: float | None
    top_positive_group_2: str | None
    top_positive_group_2_contribution: float | None
    strongest_change_group: str | None
    strongest_change_delta: float | None
    no_material_change: bool
    interpretation_status: str
    bonus_applied: bool
    bonus_points: float
