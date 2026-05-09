from __future__ import annotations

"""
Presentation mappings for deterministic V1 report output.

Traceability:
- PSR-002
- PSR-006
- PM-002
- PM-004
"""

COUNTRY_ORDER = [
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
COUNTRY_DISPLAY = {
    "Germany": "Germany",
    "Israel": "Israel",
    "Iran": "Iran",
    "Ukraine": "Ukraine",
    "Russia": "Russia",
    "Japan": "Japan",
    "China": "China",
    "Taiwan": "Taiwan",
    "Poland": "Poland",
    "Nigeria": "Nigeria",
    "Deutschland": "Germany",
}

CLUSTER_ORDER = ["tension", "escalation", "vulnerability"]
CLUSTER_DISPLAY = {
    "tension": "gesellschaftlich-politische Spannung",
    "escalation": "gewaltsame Eskalation",
    "vulnerability": "strukturelle / systemische Verwundbarkeit",
}


def country_order_index(country: str) -> int:
    """
    Stable order key for country output.

    Traceability:
    - PSR-002
    - PSR-006
    """
    try:
        return COUNTRY_ORDER.index(country)
    except ValueError:
        return len(COUNTRY_ORDER)


def cluster_order_index(cluster: str) -> int:
    """
    Stable order key for cluster output.

    Traceability:
    - PSR-006
    - PM-004
    """
    try:
        return CLUSTER_ORDER.index(cluster)
    except ValueError:
        return len(CLUSTER_ORDER)


def display_country(country: str) -> str:
    """
    Display label for countries.

    Traceability:
    - PSR-002
    - OI-001
    """
    return COUNTRY_DISPLAY.get(country, country)


def display_cluster(cluster: str) -> str:
    """
    Display label for clusters.

    Traceability:
    - PSR-006
    - PM-004
    """
    return CLUSTER_DISPLAY.get(cluster, cluster)
