// Traceability: AP-01, AP-02, AP-04, AP-06, AP-07, AP-08, AP-10
import type {
  ArtifactsOverviewResponse,
  AvailabilityState,
  CompareResponse,
  CountryCoverageSummary,
  CountryDetailResponse,
  CountryTrendPoint,
  CoverageResponse,
  HealthResponse,
  OverviewSnapshot,
  RunArtifactsResponse,
  RunDetailResponse,
  RunOptionsResponse,
  RunsResponse,
  RunSummaryResponse,
  RunStatusResponse,
} from "@/types/api";

const nowIso = new Date().toISOString();
const dayMs = 24 * 60 * 60 * 1000;

interface CountrySeed {
  code: string;
  label: string;
  status: "active" | "watch" | "stable";
  score: number;
  delta: number;
  confidence: number;
  freshnessHours: number;
  coverageRatio: number;
  notes: string[];
}

const COUNTRY_SEEDS: CountrySeed[] = [
  {
    code: "Iran",
    label: "Iran",
    status: "active",
    score: 54.39,
    delta: 2.12,
    confidence: 0.79,
    freshnessHours: 14,
    coverageRatio: 0.81,
    notes: ["Event support uneven for the latest 14-day segment."],
  },
  {
    code: "Ukraine",
    label: "Ukraine",
    status: "active",
    score: 53.18,
    delta: 1.2,
    confidence: 0.77,
    freshnessHours: 11,
    coverageRatio: 0.84,
    notes: ["Shock layer remains elevated versus 30-day baseline."],
  },
  {
    code: "Israel",
    label: "Israel",
    status: "watch",
    score: 51.07,
    delta: -0.4,
    confidence: 0.81,
    freshnessHours: 8,
    coverageRatio: 0.86,
    notes: ["Recent delta softened while event layer stayed elevated."],
  },
  {
    code: "Nigeria",
    label: "Nigeria",
    status: "watch",
    score: 46.98,
    delta: 0.63,
    confidence: 0.73,
    freshnessHours: 26,
    coverageRatio: 0.69,
    notes: ["Coverage in narrative signals is still partial."],
  },
  {
    code: "Germany",
    label: "Germany",
    status: "stable",
    score: 31.42,
    delta: -0.18,
    confidence: 0.88,
    freshnessHours: 6,
    coverageRatio: 0.91,
    notes: ["Signals remain broad with low cross-layer volatility."],
  },
  {
    code: "Russia",
    label: "Russia",
    status: "watch",
    score: 48.77,
    delta: 0.49,
    confidence: 0.75,
    freshnessHours: 17,
    coverageRatio: 0.72,
    notes: ["Structural contribution dominates over event spikes."],
  },
  {
    code: "Japan",
    label: "Japan",
    status: "stable",
    score: 29.86,
    delta: -0.31,
    confidence: 0.86,
    freshnessHours: 13,
    coverageRatio: 0.89,
    notes: ["No critical deviations in the last 30-day horizon."],
  },
  {
    code: "China",
    label: "China",
    status: "watch",
    score: 44.13,
    delta: 0.81,
    confidence: 0.8,
    freshnessHours: 22,
    coverageRatio: 0.74,
    notes: ["Market/Food and governance move in the same direction."],
  },
  {
    code: "Taiwan",
    label: "Taiwan",
    status: "watch",
    score: 43.55,
    delta: 1.43,
    confidence: 0.76,
    freshnessHours: 19,
    coverageRatio: 0.7,
    notes: ["Event-driven swings increased compared with prior month."],
  },
  {
    code: "Poland",
    label: "Poland",
    status: "stable",
    score: 35.62,
    delta: 0.1,
    confidence: 0.83,
    freshnessHours: 15,
    coverageRatio: 0.87,
    notes: ["Layer coverage remains high with moderate trend slope."],
  },
];

function getCountrySeed(countryCode: string): CountrySeed {
  return (
    COUNTRY_SEEDS.find((entry) => entry.code.toLowerCase() === countryCode.toLowerCase()) ??
    COUNTRY_SEEDS[0]
  );
}

function buildTrend(seed: CountrySeed): CountryTrendPoint[] {
  const result: CountryTrendPoint[] = [];
  const now = Date.now();

  for (let index = 23; index >= 0; index -= 1) {
    const pointDate = new Date(now - index * 14 * dayMs).toISOString();
    const wobble = Math.sin((index + seed.score) / 2.6) * 2.4 + Math.cos((index + seed.delta) / 3.7) * 1.6;
    const trendDrift = (23 - index) * (seed.delta / 20);
    const rawValue = seed.score - 8 + wobble + trendDrift;
    result.push({
      timestamp: pointDate,
      value: Number(Math.max(8, rawValue).toFixed(2)),
      confidence: Number(Math.max(0.45, seed.confidence - index * 0.004).toFixed(2)),
      freshness_hours: seed.freshnessHours + Math.floor(index / 2),
    });
  }

  return result;
}

function coverageState(ratio: number, freshnessHours: number): AvailabilityState {
  if (ratio < 0.45) {
    return "missing";
  }
  if (freshnessHours > 72) {
    return "stale";
  }
  if (ratio < 0.75) {
    return "partial";
  }
  return "ok";
}

function buildCoverageSummary(seed: CountrySeed): CountryCoverageSummary {
  return {
    available_layers: Math.round(seed.coverageRatio * 7),
    expected_layers: 7,
    coverage_ratio: seed.coverageRatio,
    freshness_hours: seed.freshnessHours,
    last_updated: new Date(Date.now() - seed.freshnessHours * 60 * 60 * 1000).toISOString(),
    warning_count: seed.notes.length > 0 ? 1 : 0,
    layer_status: {
      event: seed.freshnessHours > 48 ? "stale" : "ok",
      narrative: seed.coverageRatio < 0.78 ? "partial" : "ok",
      governance: "ok",
      market_food: "ok",
      shock: seed.coverageRatio < 0.72 ? "partial" : "ok",
      displacement: seed.coverageRatio < 0.65 ? "partial" : "ok",
      structural: "ok",
    },
  };
}

export const FALLBACK_HEALTH: HealthResponse = {
  status: "degraded_fallback",
  api_version: "v1",
  timestamp: nowIso,
};

export const FALLBACK_OPTIONS: RunOptionsResponse = {
  countries: COUNTRY_SEEDS.map((entry) => ({ code: entry.code, label: entry.label })),
  layers: [
    { key: "event", label: "Event" },
    { key: "narrative", label: "Narrative" },
    { key: "governance", label: "Governance" },
    { key: "market_food", label: "Market/Food" },
    { key: "shock", label: "Shock" },
    { key: "displacement", label: "Displacement" },
    { key: "structural", label: "Structural" },
  ],
  horizons: [7, 30, 356],
};

export const FALLBACK_RUNS: RunsResponse = {
  runs: [
    {
      run_id: "run_2026_04_15_a1",
      status: "running",
      created_at: "2026-04-15T09:20:00Z",
      started_at: "2026-04-15T09:20:06Z",
      finished_at: null,
      countries: ["Germany", "Israel", "Iran", "Ukraine", "Poland"],
      progress_percent: 58,
      warning_count: 1,
    },
    {
      run_id: "run_2026_04_14_z9",
      status: "succeeded",
      created_at: "2026-04-14T21:00:00Z",
      started_at: "2026-04-14T21:00:04Z",
      finished_at: "2026-04-14T21:01:08Z",
      countries: ["Germany", "Israel", "Iran", "Ukraine", "Poland", "Nigeria"],
      progress_percent: 100,
      warning_count: 2,
    },
    {
      run_id: "run_2026_04_14_f2",
      status: "failed",
      created_at: "2026-04-14T16:13:00Z",
      started_at: "2026-04-14T16:13:09Z",
      finished_at: "2026-04-14T16:14:02Z",
      countries: ["Nigeria", "Russia", "China", "Taiwan"],
      progress_percent: 41,
      warning_count: 0,
      error: {
        code: "API-RUN-500",
        message: "Source ingestion timeout on one adapter.",
      },
    },
  ],
};

export function fallbackRunDetail(runId: string): RunDetailResponse {
  const run = FALLBACK_RUNS.runs.find((entry) => entry.run_id === runId) ?? FALLBACK_RUNS.runs[0];
  return {
    run,
    metadata: {
      query_version: "v1",
      scoring_version: "v4.3.2",
      short_days: 7,
      recent_days: 30,
      baseline_days: 356,
      bridge_file_version: "bridge_v2",
      context_table_version: "context_v4",
    },
  };
}

export function fallbackRunStatus(runId: string): RunStatusResponse {
  const run = FALLBACK_RUNS.runs.find((entry) => entry.run_id === runId) ?? FALLBACK_RUNS.runs[0];
  return {
    run_id: run.run_id,
    status: run.status,
    progress: {
      phase: run.status === "running" ? "fusion_validation" : "completed",
      percent: run.progress_percent ?? 0,
      message:
        run.status === "failed" ? "Run terminated with source timeout." : "Processing and export generation in progress.",
    },
    started_at: run.started_at ?? null,
    finished_at: run.finished_at ?? null,
    updated_at: nowIso,
    error: run.error ?? null,
  };
}

export function fallbackRunSummary(runId: string): RunSummaryResponse {
  return {
    run_id: runId,
    summary: {
      top_country: "Iran",
      top_score: 54.39,
      event_alignment_quality: 0.58,
      freshness_coverage_rate: 0.81,
      data_window_start: "2025-04-26",
      data_window_end: "2026-04-16",
    },
    warnings: [
      "Trajectory differentiation is weak in multiple country profiles.",
      "Event-registry coverage is sparse for at least one country.",
    ],
  };
}

export function fallbackRunArtifacts(runId: string): RunArtifactsResponse {
  return {
    run_id: runId,
    artifacts: [
      {
        id: "summary_export",
        label: "Snapshot Summary Export",
        type: "json",
        path: `/api/v1/runs/${runId}/summary`,
        available: true,
        status: "available",
      },
      {
        id: "coverage_export",
        label: "Coverage Summary",
        type: "csv",
        path: `/api/v1/runs/${runId}/coverage`,
        available: true,
        status: "available",
      },
      {
        id: "country_profile_plot",
        label: "Country Profile Plot Pack",
        type: "png",
        path: `/api/v1/runs/${runId}/plots/profiles`,
        available: false,
        status: "pending",
      },
      {
        id: "bundle",
        label: "Review Bundle",
        type: "bundle",
        path: `/api/v1/runs/${runId}/bundle`,
        available: true,
        status: "available",
      },
    ],
  };
}

export const FALLBACK_OVERVIEW: OverviewSnapshot = {
  generated_at: nowIso,
  country_rankings: COUNTRY_SEEDS.map((entry) => ({
    country: entry.code,
    score: entry.score,
    delta: entry.delta,
    status: entry.status,
  })),
  latest_changes: [
    {
      label: "Event Alignment Review",
      detail: "5 peaks require manual overlap review.",
      severity: "warn",
    },
    {
      label: "Governance Instability",
      detail: "3 countries show elevated governance contribution.",
      severity: "info",
    },
    {
      label: "Coverage Alert",
      detail: "Sparse event coverage in 3 country trajectories.",
      severity: "critical",
    },
  ],
  active_runs: FALLBACK_RUNS.runs.filter((run) => run.status === "running"),
  metrics: [
    { id: "countries_total", label: "Tracked Countries", value: COUNTRY_SEEDS.length, status: "ok" },
    { id: "active_runs", label: "Active Runs", value: 1, status: "ok" },
    { id: "high_risk", label: "Active/Watch Countries", value: 7, status: "warn" },
    { id: "avg_freshness", label: "Avg Freshness", value: 15.1, unit: "h", status: "info" },
  ],
  countries: COUNTRY_SEEDS.map((entry) => ({
    country: entry.label,
    country_code: entry.code,
    status: entry.status,
    has_data: entry.coverageRatio > 0.35,
    score: entry.score,
    delta_7d: entry.delta,
    confidence: entry.confidence,
    freshness_hours: entry.freshnessHours,
    coverage_ratio: entry.coverageRatio,
    last_updated: new Date(Date.now() - entry.freshnessHours * 60 * 60 * 1000).toISOString(),
  })),
  data_availability: {
    available: 7,
    partial: 3,
    stale: 0,
    missing: 0,
  },
};

export function fallbackCountryDetail(countryCode: string): CountryDetailResponse {
  const seed = getCountrySeed(countryCode);
  const coverage = buildCoverageSummary(seed);
  const trend = buildTrend(seed);

  return {
    country_code: seed.code,
    country_label: seed.label,
    generated_at: nowIso,
    source_run_id: FALLBACK_RUNS.runs[0].run_id,
    summary: {
      status: seed.status,
      confidence: seed.confidence,
      freshness_hours: seed.freshnessHours,
      last_updated: new Date(Date.now() - seed.freshnessHours * 60 * 60 * 1000).toISOString(),
    },
    kpis: [
      { id: "score", label: "Current Score", value: seed.score, delta: seed.delta, status: "info" },
      { id: "confidence", label: "Confidence", value: Math.round(seed.confidence * 100), unit: "%", status: "ok" },
      { id: "coverage", label: "Coverage", value: Math.round(seed.coverageRatio * 100), unit: "%", status: "warn" },
      { id: "freshness", label: "Freshness", value: seed.freshnessHours, unit: "h", status: "ok" },
    ],
    daily_briefing: [
      `${seed.label}: status ${seed.status} with score ${seed.score.toFixed(2)} and delta ${seed.delta.toFixed(2)}.`,
      `Latest refresh is ${seed.freshnessHours} hours old with coverage ratio ${(seed.coverageRatio * 100).toFixed(0)}%.`,
      "No front-end domain scoring applied; values are API/fallback sourced only.",
    ],
    long_term_notes: [
      "Trend line shows medium volatility with sustained baseline load.",
      "Event and governance layers remain the dominant short-term drivers.",
    ],
    trend,
    layers: [
      {
        layer: "event",
        value: Number((seed.score / 100).toFixed(2)),
        status: coverage.layer_status?.event ?? "ok",
        freshness_hours: seed.freshnessHours + 2,
      },
      {
        layer: "narrative",
        value: Number((seed.score / 118).toFixed(2)),
        status: coverage.layer_status?.narrative ?? "partial",
        freshness_hours: seed.freshnessHours + 6,
      },
      {
        layer: "governance",
        value: Number((seed.score / 105).toFixed(2)),
        status: coverage.layer_status?.governance ?? "ok",
        freshness_hours: seed.freshnessHours + 3,
      },
      {
        layer: "market_food",
        value: Number((seed.score / 130).toFixed(2)),
        status: coverage.layer_status?.market_food ?? "ok",
        freshness_hours: seed.freshnessHours + 8,
      },
      {
        layer: "structural",
        value: Number((seed.score / 112).toFixed(2)),
        status: coverage.layer_status?.structural ?? "ok",
        freshness_hours: seed.freshnessHours + 12,
      },
    ],
    coverage,
    artifacts: fallbackRunArtifacts(FALLBACK_RUNS.runs[0].run_id).artifacts.map((artifact) => ({
      ...artifact,
      id: `${seed.code}_${artifact.id}`,
      run_id: FALLBACK_RUNS.runs[0].run_id,
    })),
    notes: seed.notes.map((text, index) => ({
      id: `${seed.code}_note_${index + 1}`,
      text,
      severity: index === 0 ? "warn" : "info",
      source: "fallback",
    })),
  };
}

export const FALLBACK_COVERAGE: CoverageResponse = {
  generated_at: nowIso,
  layers: ["event", "narrative", "governance", "market_food", "shock", "displacement", "structural"],
  rows: COUNTRY_SEEDS.map((seed) => {
    const summary = buildCoverageSummary(seed);
    return {
      country: seed.label,
      country_code: seed.code,
      status: coverageState(seed.coverageRatio, seed.freshnessHours),
      available_layers: summary.available_layers,
      expected_layers: summary.expected_layers,
      coverage_ratio: summary.coverage_ratio,
      freshness_hours: summary.freshness_hours,
      last_updated: summary.last_updated,
      layer_status: summary.layer_status ?? {},
      warnings: seed.coverageRatio < 0.75 ? ["Coverage below preferred threshold."] : [],
    };
  }),
  warnings: ["Coverage values are fallback estimates in this environment."],
};

export function fallbackCompare(countries: string[]): CompareResponse {
  const selected = (countries.length > 0 ? countries : COUNTRY_SEEDS.slice(0, 3).map((entry) => entry.code)).slice(0, 6);

  return {
    generated_at: nowIso,
    warnings: selected.length < 2 ? ["Select at least two countries for full comparison context."] : [],
    countries: selected.map((countryCode) => {
      const seed = getCountrySeed(countryCode);
      return {
        country: seed.code,
        status: seed.status,
        score: seed.score,
        delta_7d: seed.delta,
        confidence: seed.confidence,
        freshness_hours: seed.freshnessHours,
        trend: buildTrend(seed),
        kpis: [
          { id: "score", label: "Score", value: seed.score, delta: seed.delta, status: "info" },
          { id: "confidence", label: "Confidence", value: Math.round(seed.confidence * 100), unit: "%" },
          { id: "coverage", label: "Coverage", value: Math.round(seed.coverageRatio * 100), unit: "%" },
        ],
      };
    }),
  };
}

export const FALLBACK_ARTIFACTS_OVERVIEW: ArtifactsOverviewResponse = {
  generated_at: nowIso,
  runs: FALLBACK_RUNS.runs.map((run) => {
    const runArtifacts = fallbackRunArtifacts(run.run_id).artifacts;
    const bundle = runArtifacts.find((artifact) => artifact.type === "bundle") ?? null;
    return {
      run_id: run.run_id,
      status: run.status,
      created_at: run.created_at,
      artifacts: runArtifacts,
      bundle,
    };
  }),
};
