from __future__ import annotations

from calendar import monthrange
import csv
from dataclasses import dataclass
from datetime import date, timedelta
import math
from pathlib import Path
import random


RUN_DATE = date(2026, 4, 12)
HORIZON_DAYS = 356
START_DATE = RUN_DATE - timedelta(days=HORIZON_DAYS - 1)

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

BASE_RISK = {
    "Germany": 0.33,
    "Israel": 0.66,
    "Iran": 0.86,
    "Ukraine": 0.80,
    "Russia": 0.74,
    "Japan": 0.28,
    "China": 0.55,
    "Taiwan": 0.60,
    "Poland": 0.47,
    "Nigeria": 0.77,
}

PEAKS = {
    "Germany": [(95, 0.09), (250, 0.11)],
    "Israel": [(120, 0.16), (260, 0.18)],
    "Iran": [(135, 0.22), (290, 0.26)],
    "Ukraine": [(150, 0.22), (300, 0.21)],
    "Russia": [(145, 0.18), (298, 0.17)],
    "Japan": [(175, 0.06)],
    "China": [(160, 0.10), (305, 0.11)],
    "Taiwan": [(165, 0.12), (315, 0.13)],
    "Poland": [(170, 0.09), (308, 0.10)],
    "Nigeria": [(140, 0.20), (285, 0.24)],
}

EVENT_TYPES = [
    "internal_violence",
    "repression",
    "domestic_attack",
    "war_activity",
    "external_attack",
    "regional_spillover",
]


@dataclass(frozen=True)
class MonthPeriod:
    start: date
    end: date
    label: str


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _rng(country: str, salt: str) -> random.Random:
    seed = sum(ord(ch) for ch in f"{country}:{salt}:v43")
    return random.Random(seed)


def _day_index(current: date) -> int:
    return (current - START_DATE).days


def _peak_component(country: str, index: int) -> float:
    peaks = PEAKS[country]
    total = 0.0
    for center, amplitude in peaks:
        distance = abs(index - center)
        width = 22.0
        total += amplitude * math.exp(-(distance * distance) / (2.0 * width * width))
    return total


def _monthly_periods() -> list[MonthPeriod]:
    start = date(2025, 5, 1)
    periods: list[MonthPeriod] = []
    current = start
    while current <= RUN_DATE:
        end_day = monthrange(current.year, current.month)[1]
        period_end = date(current.year, current.month, end_day)
        if period_end > RUN_DATE:
            period_end = RUN_DATE
        periods.append(
            MonthPeriod(
                start=current,
                end=period_end,
                label=f"{current.year:04d}-{current.month:02d}",
            )
        )
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return periods


def _daily_pressure(country: str, current: date) -> float:
    index = _day_index(current)
    base = BASE_RISK[country]
    seasonal = 0.04 * math.sin(2.0 * math.pi * index / 92.0)
    weekly = 0.02 * math.sin(2.0 * math.pi * index / 7.0)
    peak = _peak_component(country, index)
    return _clamp(base + seasonal + weekly + peak, 0.02, 0.98)


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def generate_gdelt(path: Path) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        country_rng = _rng(country, "gdelt")
        for offset in range(HORIZON_DAYS):
            current = START_DATE + timedelta(days=offset)
            pressure = _daily_pressure(country, current)
            for category, factor in (
                ("protest", 0.92),
                ("crisis", 1.02),
                ("negativity", 0.97),
            ):
                noise = country_rng.uniform(-2.4, 2.4)
                raw_value = _clamp(100.0 * pressure * factor + noise, 1.0, 99.0)
                tone = -_clamp(raw_value / 11.0 + country_rng.uniform(-0.7, 0.7), 0.8, 9.5)
                article_count = _clamp(raw_value * 1.6 + country_rng.uniform(6.0, 28.0), 4.0, 250.0)
                rows.append(
                    [
                        current.isoformat(),
                        country,
                        category,
                        f"{raw_value:.1f}",
                        f"{tone:.1f}",
                        f"{article_count:.1f}",
                    ]
                )
    _write_csv(
        path,
        ["date", "country", "category", "raw_value", "tone", "article_count"],
        rows,
    )


def _external_factor(country: str) -> float:
    return {
        "Iran": 0.92,
        "Israel": 0.82,
        "Ukraine": 0.94,
        "Russia": 0.88,
        "Taiwan": 0.72,
        "China": 0.61,
        "Nigeria": 0.66,
        "Poland": 0.42,
        "Germany": 0.18,
        "Japan": 0.12,
    }[country]


def generate_ucdp(path: Path) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        country_rng = _rng(country, "ucdp")
        for offset in range(HORIZON_DAYS):
            current = START_DATE + timedelta(days=offset)
            pressure = _daily_pressure(country, current)
            ext = _external_factor(country)
            values = {
                "internal_violence": 100.0 * (pressure * 0.95),
                "repression": 100.0 * (pressure * 0.84),
                "domestic_attack": 100.0 * (pressure * 0.76),
                "war_activity": 100.0 * (0.32 * pressure + 0.68 * ext),
                "external_attack": 100.0 * (0.30 * pressure + 0.70 * ext),
                "regional_spillover": 100.0 * (0.52 * pressure + 0.48 * ext),
            }
            for event_type in EVENT_TYPES:
                noise = country_rng.uniform(-2.8, 2.8)
                raw_value = _clamp(values[event_type] + noise, 0.0, 99.0)
                fatalities = int(_clamp(raw_value / 5.8 + country_rng.uniform(-1.2, 1.9), 0.0, 62.0))
                rows.append(
                    [
                        current.isoformat(),
                        country,
                        event_type,
                        f"{raw_value:.1f}",
                        str(fatalities),
                    ]
                )
    _write_csv(path, ["date", "country", "event_type", "raw_value", "fatalities"], rows)


def generate_bridge(path: Path) -> None:
    rows = [
        ["2025-11-10", "Ukraine", "security_event", "escalation", "external", "0.9", "Bridge escalation marker", "manual_seed_v43", "medium", "true"],
        ["2025-12-18", "Russia", "security_event", "escalation", "external", "0.8", "Bridge escalation marker", "manual_seed_v43", "medium", "true"],
        ["2026-01-15", "Iran", "security_event", "escalation", "external", "0.8", "Bridge escalation marker", "manual_seed_v43", "medium", "true"],
        ["2026-02-04", "Israel", "security_event", "escalation", "external", "0.7", "Bridge escalation marker", "manual_seed_v43", "medium", "true"],
        ["2026-03-08", "Nigeria", "security_event", "escalation", "internal", "0.8", "Bridge escalation marker", "manual_seed_v43", "medium", "true"],
        ["2025-10-22", "Germany", "protest_marker", "tension", "na", "0.3", "Bridge protest marker", "manual_seed_v43", "medium", "true"],
        ["2025-12-05", "Poland", "protest_marker", "tension", "na", "0.4", "Bridge protest marker", "manual_seed_v43", "medium", "true"],
        ["2026-01-22", "Taiwan", "crisis_marker", "tension", "na", "0.5", "Bridge crisis marker", "manual_seed_v43", "medium", "true"],
        ["2026-02-18", "China", "negativity_marker", "tension", "na", "0.4", "Bridge negativity marker", "manual_seed_v43", "medium", "true"],
        ["2026-03-26", "Japan", "protest_marker", "tension", "na", "0.2", "Bridge protest marker", "manual_seed_v43", "medium", "true"],
    ]
    _write_csv(
        path,
        [
            "date",
            "country",
            "event_type",
            "cluster",
            "subcluster",
            "severity",
            "description",
            "source_note",
            "confidence",
            "include_in_cluster",
        ],
        rows,
    )


def generate_context(path: Path) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        risk = BASE_RISK[country]
        economic = _clamp(12.0 + risk * 88.0, 8.0, 95.0)
        hybrid = _clamp(18.0 + risk * 76.0, 10.0, 94.0)
        governance = _clamp(15.0 + risk * 90.0, 10.0, 96.0)
        rows.append(
            [
                country,
                f"{economic:.1f}",
                "Synthetic V4.3 economic vulnerability baseline",
                f"{hybrid:.1f}",
                "Synthetic V4.3 hybrid vulnerability baseline",
                f"{governance:.1f}",
                "Synthetic V4.3 governance stress baseline",
            ]
        )
    _write_csv(
        path,
        [
            "country",
            "economic_vulnerability_score",
            "economic_vulnerability_note",
            "hybrid_vulnerability_score",
            "hybrid_vulnerability_note",
            "governance_stress_score",
            "governance_stress_note",
        ],
        rows,
    )


def _monthly_base(country: str, period_index: int) -> float:
    pressure = BASE_RISK[country]
    seasonal = 0.05 * math.sin(2.0 * math.pi * period_index / 6.0)
    return _clamp(pressure + seasonal + _peak_component(country, 80 + period_index * 24), 0.02, 0.98)


def generate_fao_ffpi(path: Path, periods: list[MonthPeriod]) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        for i, period in enumerate(periods):
            pressure = _monthly_base(country, i)
            raw = _clamp(88.0 + pressure * 64.0, 85.0, 170.0)
            rows.append(
                [
                    period.start.isoformat(),
                    period.end.isoformat(),
                    country,
                    f"{raw:.1f}",
                    "index_points",
                    "FAO_FFPI_snapshot_v43",
                    "0.95",
                ]
            )
    _write_csv(
        path,
        ["period_start", "period_end", "country", "raw_value", "unit", "provenance", "quality_completeness"],
        rows,
    )


def generate_fao_fpma(path: Path, periods: list[MonthPeriod]) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        for i, period in enumerate(periods):
            pressure = _monthly_base(country, i)
            raw = _clamp(6.0 + pressure * 92.0, 3.0, 98.0)
            rows.append(
                [
                    period.start.isoformat(),
                    period.end.isoformat(),
                    country,
                    f"{raw:.1f}",
                    "warning_index",
                    "FAO_FPMA_snapshot_v43",
                    "0.91",
                ]
            )
    _write_csv(
        path,
        ["period_start", "period_end", "country", "raw_value", "unit", "provenance", "quality_completeness"],
        rows,
    )


def generate_un_comtrade(path: Path) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        risk = BASE_RISK[country]
        for year in (2024, 2025):
            swing = 0.01 if year == 2025 else -0.01
            raw = _clamp(0.18 + risk * 0.62 + swing, 0.12, 0.92)
            rows.append(
                [
                    f"{year}-01-01",
                    f"{year}-12-31",
                    country,
                    f"{raw:.3f}",
                    "dependency_share",
                    "UN_COMTRADE_snapshot_v43",
                    "0.89",
                ]
            )
    _write_csv(
        path,
        ["period_start", "period_end", "country", "raw_value", "unit", "provenance", "quality_completeness"],
        rows,
    )


def generate_gdacs(path: Path, periods: list[MonthPeriod]) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        for i, period in enumerate(periods):
            pressure = _monthly_base(country, i)
            severity = _clamp(0.08 + pressure * 0.9, 0.05, 0.98)
            relevance = _clamp(0.32 + pressure * 0.68, 0.2, 0.99)
            if severity >= 0.66:
                alert = "red"
            elif severity >= 0.38:
                alert = "orange"
            else:
                alert = "green"
            rows.append(
                [
                    period.start.isoformat(),
                    period.end.isoformat(),
                    country,
                    f"{severity:.3f}",
                    alert,
                    f"{relevance:.3f}",
                    "shock_index",
                    "GDACS_snapshot_v43",
                    "0.90",
                ]
            )
    _write_csv(
        path,
        [
            "period_start",
            "period_end",
            "country",
            "severity",
            "alert_level",
            "relevance",
            "unit",
            "provenance",
            "quality_completeness",
        ],
        rows,
    )


def generate_unhcr(path: Path, periods: list[MonthPeriod]) -> None:
    rows: list[list[str]] = []
    previous_by_country: dict[str, float] = {}
    for country in COUNTRIES:
        previous_by_country[country] = 0.25 + BASE_RISK[country] * 0.55
    for i, period in enumerate(periods):
        for country in COUNTRIES:
            base = _clamp(0.22 + _monthly_base(country, i) * 0.72, 0.05, 0.97)
            previous = previous_by_country[country]
            delta = base - previous
            exposure = _clamp(0.18 + BASE_RISK[country] * 0.72, 0.08, 0.98)
            rows.append(
                [
                    period.start.isoformat(),
                    period.end.isoformat(),
                    country,
                    f"{base:.3f}",
                    f"{delta:.3f}",
                    f"{exposure:.3f}",
                    "displacement_index",
                    "UNHCR_snapshot_v43",
                    "0.91",
                ]
            )
            previous_by_country[country] = base
    _write_csv(
        path,
        [
            "period_start",
            "period_end",
            "country",
            "displacement_pressure",
            "delta_pressure",
            "exposure",
            "unit",
            "provenance",
            "quality_completeness",
        ],
        rows,
    )


def generate_narrative(path: Path, periods: list[MonthPeriod]) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        for i, period in enumerate(periods):
            pressure = _monthly_base(country, i)
            if pressure >= 0.62:
                direction = "escalatory"
            elif pressure <= 0.35:
                direction = "deescalatory"
            else:
                direction = "neutral"
            relevance = _clamp(0.30 + pressure * 0.65, 0.2, 0.98)
            confidence = _clamp(0.60 + pressure * 0.30, 0.55, 0.95)
            topic = "governance_contestation" if i % 3 == 0 else "societal_stress"
            rows.append(
                [
                    "regional_expert_brief",
                    country,
                    period.start.isoformat(),
                    period.end.isoformat(),
                    topic,
                    direction,
                    f"{relevance:.3f}",
                    f"{confidence:.3f}",
                    "NARRATIVE_snapshot_v43",
                ]
            )
    _write_csv(
        path,
        [
            "source_id",
            "country",
            "period_start",
            "period_end",
            "topic",
            "narrative_direction",
            "relevance",
            "confidence",
            "provenance",
        ],
        rows,
    )


def generate_governance(path: Path, periods: list[MonthPeriod]) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        for i, period in enumerate(periods):
            pressure = _monthly_base(country, i)
            government_effectiveness = _clamp(0.90 - pressure * 0.78, 0.08, 0.94)
            institutional_trust = _clamp(0.88 - pressure * 0.74, 0.08, 0.95)
            political_polarization = _clamp(0.12 + pressure * 0.82, 0.08, 0.98)
            protest_pressure = _clamp(0.10 + pressure * 0.86, 0.08, 0.98)
            policy_blockage = _clamp(0.14 + pressure * 0.80, 0.08, 0.98)
            resilience_buffer = _clamp(0.90 - pressure * 0.70, 0.08, 0.96)
            rows.append(
                [
                    period.start.isoformat(),
                    period.end.isoformat(),
                    country,
                    f"{government_effectiveness:.3f}",
                    f"{institutional_trust:.3f}",
                    f"{political_polarization:.3f}",
                    f"{protest_pressure:.3f}",
                    f"{policy_blockage:.3f}",
                    f"{resilience_buffer:.3f}",
                    "GOVERNANCE_snapshot_v43",
                    "0.90",
                ]
            )
    _write_csv(
        path,
        [
            "period_start",
            "period_end",
            "country",
            "government_effectiveness",
            "institutional_trust",
            "political_polarization",
            "protest_pressure",
            "policy_blockage",
            "resilience_buffer",
            "provenance",
            "quality_completeness",
        ],
        rows,
    )


def _expected_reaction(country: str) -> str:
    risk = BASE_RISK[country]
    if risk >= 0.79:
        return "high"
    if risk >= 0.56:
        return "elevated"
    return "low"


def _expected_groups(country: str) -> str:
    risk = BASE_RISK[country]
    if risk >= 0.79:
        return "event|governance|displacement|shock|market_food"
    if risk >= 0.60:
        return "event|governance|shock|market_food"
    if risk >= 0.45:
        return "governance|market_food|narrative"
    return "market_food|governance"


def generate_reference_episodes(path: Path) -> None:
    rows: list[list[str]] = []
    for country in COUNTRIES:
        reaction = _expected_reaction(country)
        groups = _expected_groups(country)
        rows.extend(
            [
                [
                    f"{country[:3].upper()}-2025-EARLY",
                    country,
                    "2025-05-01",
                    "2025-07-31",
                    "2025-07",
                    "low",
                    "structural",
                    "2",
                    "Early horizon phase with limited dynamic-layer support.",
                    "Low-stage interpretation expected with explicit low-coverage caveat.",
                ],
                [
                    f"{country[:3].upper()}-2025-AUTUMN",
                    country,
                    "2025-09-01",
                    "2025-11-30",
                    "2025-11",
                    "elevated" if reaction != "low" else "low",
                    groups,
                    "1",
                    "Autumn transition phase with broadened multi-layer pressure.",
                    "At least elevated reaction for medium/high-risk profiles; otherwise low-to-elevated.",
                ],
                [
                    f"{country[:3].upper()}-2026-WINTER",
                    country,
                    "2025-12-01",
                    "2026-02-28",
                    "2026-01",
                    reaction,
                    groups,
                    "1",
                    "Winter peak phase with visible pressure concentration and spillovers.",
                    "Peak window should show strongest annual reaction for country profile.",
                ],
                [
                    f"{country[:3].upper()}-2026-SPRING",
                    country,
                    "2026-03-01",
                    "2026-04-12",
                    "2026-03",
                    "elevated" if reaction == "high" else reaction,
                    groups,
                    "1",
                    "Spring phase with partial normalization but persistent baseline fragility.",
                    "Post-peak response should remain interpretable with dominant-driver visibility.",
                ],
            ]
        )
    _write_csv(
        path,
        [
            "episode_id",
            "country",
            "period_start",
            "period_end",
            "expected_peak_period",
            "expected_total_reaction",
            "expected_groups",
            "timing_tolerance_months",
            "real_world_summary",
            "expected_total_summary",
        ],
        rows,
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    periods = _monthly_periods()
    generate_gdelt(root / "data/gdelt/gdelt_events.csv")
    generate_ucdp(root / "data/ucdp/ucdp_events.csv")
    generate_bridge(root / "data/bridge/bridge_events.csv")
    generate_context(root / "data/context/country_context.csv")
    generate_fao_ffpi(root / "data/fao_ffpi/fao_ffpi.csv", periods)
    generate_fao_fpma(root / "data/fao_fpma/fao_fpma.csv", periods)
    generate_un_comtrade(root / "data/un_comtrade/un_comtrade.csv")
    generate_gdacs(root / "data/gdacs/gdacs_events.csv", periods)
    generate_unhcr(root / "data/unhcr/unhcr_displacement.csv", periods)
    generate_narrative(root / "data/narrative_input/narrative_input.csv", periods)
    generate_governance(root / "data/governance_input/governance_input.csv", periods)
    generate_reference_episodes(root / "data/validation/reference_episodes.csv")
    print("V4.3 seed data generated")


if __name__ == "__main__":
    main()

