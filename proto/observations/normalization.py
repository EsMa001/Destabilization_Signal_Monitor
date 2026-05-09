from __future__ import annotations

"""
Simple transparent normalization rules for canonical source signals.

Traceability:
- PSwR-040
- ALG-013
- PM-018
"""

from statistics import mean, pstdev

SUPPORTED_NORMALIZATION_METHODS = {
    "z_score",
    "percentile",
    "baseline_deviation",
}


def _clamp_01(value: float) -> float:
    # Traceability:
    # - PSwR-040
    # - ALG-013
    # - PM-018
    return max(0.0, min(1.0, value))


def _normalize_z_score(values: list[float]) -> list[float]:
    # Traceability:
    # - PSwR-040
    # - ALG-013
    # - PM-018
    if not values:
        return []
    avg = mean(values)
    sigma = pstdev(values)
    if sigma == 0:
        return [0.5 for _ in values]
    # Clip to [-3, 3] and map linearly to [0, 1].
    normalized: list[float] = []
    for value in values:
        z = (value - avg) / sigma
        mapped = (max(-3.0, min(3.0, z)) + 3.0) / 6.0
        normalized.append(round(_clamp_01(mapped), 4))
    return normalized


def _normalize_percentile(values: list[float]) -> list[float]:
    # Traceability:
    # - PSwR-040
    # - ALG-013
    # - PM-018
    if not values:
        return []
    if len(values) == 1:
        return [0.5]
    sorted_values = sorted(values)
    denominator = float(len(values) - 1)
    normalized: list[float] = []
    for value in values:
        less_or_equal = sum(1 for item in sorted_values if item <= value)
        rank = (less_or_equal - 1) / denominator
        normalized.append(round(_clamp_01(rank), 4))
    return normalized


def _normalize_baseline_deviation(
    values: list[float],
    *,
    baseline_value: float,
    baseline_scale: float,
) -> list[float]:
    # Traceability:
    # - PSwR-040
    # - ALG-013
    # - PM-018
    if not values:
        return []
    denominator = max(1e-6, abs(baseline_scale))
    normalized = [
        round(_clamp_01((value - baseline_value) / denominator), 4)
        for value in values
    ]
    return normalized


def normalize_series(
    values: list[float],
    *,
    method: str,
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[float]:
    """
    Normalize source values to [0, 1] using explicit configured method.

    Traceability:
    - PSwR-040
    - ALG-013
    """
    normalized_method = method.strip().lower()
    if normalized_method not in SUPPORTED_NORMALIZATION_METHODS:
        raise ValueError(
            f"unsupported normalization method {method!r}; "
            f"expected one of {sorted(SUPPORTED_NORMALIZATION_METHODS)}"
        )
    if normalized_method == "z_score":
        return _normalize_z_score(values)
    if normalized_method == "percentile":
        return _normalize_percentile(values)

    if baseline_value is None:
        raise ValueError("baseline_deviation requires baseline_value")
    scale = baseline_scale if baseline_scale is not None else max(1.0, abs(float(baseline_value)))
    return _normalize_baseline_deviation(
        values,
        baseline_value=float(baseline_value),
        baseline_scale=float(scale),
    )
