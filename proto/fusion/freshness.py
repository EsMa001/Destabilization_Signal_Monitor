from __future__ import annotations

"""
Freshness/staleness helpers for V4.1 operational responsiveness.

Traceability:
- PSR-022
- PSyR-032
- PSwR-083
- PSwR-084
- PM-042
- PM-043
- ALG-029
"""

from copy import deepcopy
from dataclasses import dataclass


DEFAULT_FRESHNESS_MODEL: dict[str, dict[str, float]] = {
    "default": {
        "fresh_max_days": 30.0,
        "stale_max_days": 120.0,
        "aging_floor_factor": 0.8,
        "stale_half_life_days": 60.0,
        "minimum_decay_factor": 0.45,
    },
    "event": {
        "fresh_max_days": 10.0,
        "stale_max_days": 35.0,
        "aging_floor_factor": 0.6,
        "stale_half_life_days": 25.0,
        "minimum_decay_factor": 0.22,
    },
    "narrative": {
        "fresh_max_days": 30.0,
        "stale_max_days": 90.0,
        "aging_floor_factor": 0.78,
        "stale_half_life_days": 50.0,
        "minimum_decay_factor": 0.38,
    },
    "governance": {
        "fresh_max_days": 45.0,
        "stale_max_days": 150.0,
        "aging_floor_factor": 0.82,
        "stale_half_life_days": 90.0,
        "minimum_decay_factor": 0.62,
    },
    "market_food": {
        "fresh_max_days": 45.0,
        "stale_max_days": 120.0,
        "aging_floor_factor": 0.82,
        "stale_half_life_days": 70.0,
        "minimum_decay_factor": 0.5,
    },
    "shock": {
        "fresh_max_days": 21.0,
        "stale_max_days": 75.0,
        "aging_floor_factor": 0.74,
        "stale_half_life_days": 45.0,
        "minimum_decay_factor": 0.35,
    },
    "displacement": {
        "fresh_max_days": 35.0,
        "stale_max_days": 110.0,
        "aging_floor_factor": 0.8,
        "stale_half_life_days": 60.0,
        "minimum_decay_factor": 0.4,
    },
    "structural": {
        "fresh_max_days": 120.0,
        "stale_max_days": 365.0,
        "aging_floor_factor": 0.92,
        "stale_half_life_days": 180.0,
        "minimum_decay_factor": 0.72,
    },
}


@dataclass(frozen=True)
class FreshnessRule:
    fresh_max_days: int
    stale_max_days: int
    aging_floor_factor: float
    stale_half_life_days: int
    minimum_decay_factor: float


def copy_default_freshness_model() -> dict[str, dict[str, float]]:
    """
    Return a writable copy of the default V4.1 freshness model.

    Traceability:
    - PSwR-083
    """
    return deepcopy(DEFAULT_FRESHNESS_MODEL)


def resolve_freshness_rule(
    *,
    freshness_model: dict[str, dict[str, float]] | None,
    group: str,
) -> FreshnessRule:
    """
    Resolve one group-specific freshness rule with `default` fallback.

    Traceability:
    - PSwR-083
    - ALG-029
    """
    model = freshness_model or DEFAULT_FRESHNESS_MODEL
    default_rule = model.get("default", DEFAULT_FRESHNESS_MODEL["default"])
    group_rule = model.get(group, default_rule)
    return FreshnessRule(
        fresh_max_days=int(group_rule["fresh_max_days"]),
        stale_max_days=int(group_rule["stale_max_days"]),
        aging_floor_factor=float(group_rule["aging_floor_factor"]),
        stale_half_life_days=int(group_rule["stale_half_life_days"]),
        minimum_decay_factor=float(group_rule["minimum_decay_factor"]),
    )


def classify_freshness(
    *,
    age_days: int,
    rule: FreshnessRule,
) -> str:
    """
    Classify signal age into `fresh`, `aging`, or `stale`.

    Traceability:
    - PSwR-083
    - ALG-029
    """
    if age_days <= rule.fresh_max_days:
        return "fresh"
    if age_days <= rule.stale_max_days:
        return "aging"
    return "stale"


def freshness_decay_factor(
    *,
    age_days: int,
    rule: FreshnessRule,
    fresh_boost_factor: float = 1.0,
) -> float:
    """
    Piecewise freshness decay:
    - fresh: keep/boost
    - aging: linear decay to aging floor
    - stale: exponential decay to minimum factor

    Traceability:
    - PSwR-084
    - PM-043
    - ALG-029
    """
    if age_days <= rule.fresh_max_days:
        return max(0.0, fresh_boost_factor)

    if age_days <= rule.stale_max_days:
        aging_window = max(1, rule.stale_max_days - rule.fresh_max_days)
        progress = (age_days - rule.fresh_max_days) / float(aging_window)
        value = fresh_boost_factor - progress * (fresh_boost_factor - rule.aging_floor_factor)
        return max(rule.minimum_decay_factor, value)

    overdue_days = age_days - rule.stale_max_days
    exponent = overdue_days / float(max(1, rule.stale_half_life_days))
    value = rule.aging_floor_factor * (0.5 ** exponent)
    return max(rule.minimum_decay_factor, value)
