from __future__ import annotations

"""
Traceability:
- PSwR-015
"""


def build_short_summary(
    cluster_name: str,
    stage: str,
    trend: str,
    confidence_level: str,
) -> str:
    """
    Build short interpretation text.

    Traceability:
    - PSwR-015
    """
    return (
        f"{cluster_name} ist {stage}; Trend {trend}; "
        f"Confidence {confidence_level}."
    )
