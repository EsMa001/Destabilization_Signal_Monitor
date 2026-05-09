from __future__ import annotations

"""
Shared data models.

Traceability:
- PSwR-001
- PM-001
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class SourceRecord:
    """
    Canonical raw-source record.

    Traceability:
    - PSwR-001
    - PSwR-003
    - PSwR-004
    - DataModel: Source record
    """

    source_id: str
    country: str
    date: date
    category: str
    raw_value: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FeatureRecord:
    """
    Canonical feature record.

    Traceability:
    - PSwR-001
    - PSwR-007
    - PSwR-008
    - PSwR-009
    - DataModel: Feature record
    """

    feature_id: str
    country: str
    date: date
    cluster: str
    subcluster: str
    feature_name: str
    feature_value: float


@dataclass(frozen=True)
class ScoreRecord:
    """
    Canonical score record.

    Traceability:
    - PSwR-001
    - PSwR-010
    - PSwR-011
    - DataModel: Score record
    """

    score_id: str
    country: str
    date: date
    cluster: str
    subcluster: str
    score_name: str
    score_value: float


@dataclass(frozen=True)
class ClusterAssessment:
    """
    Final per-country cluster assessment.

    Traceability:
    - PSwR-012
    - PSwR-013
    - PSwR-014
    - PSwR-015
    """

    country: str
    cluster: str
    cluster_score: float
    stage: str
    trend: str
    confidence_score: float
    confidence_level: str
    summary_text: str
