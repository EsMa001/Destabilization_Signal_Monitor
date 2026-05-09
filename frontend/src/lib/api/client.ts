// Traceability: AP-01, AP-02, AP-04, AP-06, AP-07, AP-08, AP-10
import {
  FALLBACK_ARTIFACTS_OVERVIEW,
  FALLBACK_COVERAGE,
  FALLBACK_HEALTH,
  FALLBACK_OPTIONS,
  FALLBACK_OVERVIEW,
  FALLBACK_RUNS,
  fallbackCompare,
  fallbackCountryDetail,
  fallbackRunArtifacts,
  fallbackRunDetail,
  fallbackRunStatus,
  fallbackRunSummary,
} from "@/lib/api/fallback";
import type {
  ArtifactsOverviewResponse,
  ArtifactItem,
  AvailabilityState,
  BackendConnectivityStatus,
  CompareResponse,
  CountryDetailResponse,
  CountryWatchState,
  CoverageResponse,
  HealthResponse,
  OverviewSnapshot,
  RunArtifactsResponse,
  RunCreateRequest,
  RunCreateResponse,
  RunDetailResponse,
  RunOptionsResponse,
  RunRecord,
  RunsResponse,
  RunStatus,
  RunStatusResponse,
  RunSummaryResponse,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;
const LEGACY_FALLBACK_MODE = (process.env.NEXT_PUBLIC_API_FALLBACK_MODE ?? "").toLowerCase();
const EXPLICIT_MOCK_FALLBACK = process.env.NEXT_PUBLIC_ENABLE_MOCK_FALLBACK;
const MOCK_FALLBACK_ENABLED =
  typeof EXPLICIT_MOCK_FALLBACK === "string" && EXPLICIT_MOCK_FALLBACK.length > 0
    ? EXPLICIT_MOCK_FALLBACK.toLowerCase() === "true"
    : LEGACY_FALLBACK_MODE === "on";

const RUN_STATUSES: RunStatus[] = [
  "queued",
  "running",
  "succeeded",
  "failed",
  "completed",
  "cancelled",
  "unknown",
];
const WATCH_STATES: CountryWatchState[] = ["active", "watch", "stable", "unknown"];
const AVAILABILITY_STATES: AvailabilityState[] = ["ok", "partial", "stale", "missing"];

export class ApiClientError extends Error {
  constructor(
    public readonly path: string,
    public readonly status: number,
    public readonly details?: unknown,
  ) {
    super(`API request failed: ${path} (${status})`);
    this.name = "ApiClientError";
  }
}

export class BackendUnavailableError extends Error {
  constructor(
    public readonly path: string,
    message?: string,
    public readonly causeError?: unknown,
  ) {
    super(message ?? `Backend unavailable for request: ${path}`);
    this.name = "BackendUnavailableError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function isPresent<T>(value: T | null): value is T {
  return value !== null;
}

function asString(...values: unknown[]): string | null {
  for (const value of values) {
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }
  return null;
}

function asNumber(...values: unknown[]): number | null {
  for (const value of values) {
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === "string" && value.trim().length > 0) {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }
  return null;
}

function asBoolean(...values: unknown[]): boolean | null {
  for (const value of values) {
    if (typeof value === "boolean") {
      return value;
    }
    if (value === "true") {
      return true;
    }
    if (value === "false") {
      return false;
    }
  }
  return null;
}

function toRunStatus(value: unknown, fallback: RunStatus = "unknown"): RunStatus {
  const normalized = asString(value)?.toLowerCase();
  return RUN_STATUSES.find((status) => status === normalized) ?? fallback;
}

function toWatchState(value: unknown, fallback: CountryWatchState = "unknown"): CountryWatchState {
  const normalized = asString(value)?.toLowerCase();
  return WATCH_STATES.find((status) => status === normalized) ?? fallback;
}

function toAvailability(value: unknown, fallback: AvailabilityState = "missing"): AvailabilityState {
  const normalized = asString(value)?.toLowerCase();
  return AVAILABILITY_STATES.find((status) => status === normalized) ?? fallback;
}

function encodePathPart(value: string): string {
  return encodeURIComponent(value);
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
      ...init.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let details: unknown = null;
    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }
    throw new ApiClientError(path, response.status, details);
  }

  return (await response.json()) as T;
}

async function requestJsonOrNull(path: string): Promise<unknown | null> {
  try {
    return await requestJson<unknown>(path, { method: "GET" });
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

async function requestFirstAvailable(paths: string[]): Promise<unknown | null> {
  let lastError: unknown = null;

  for (const path of paths) {
    try {
      return await requestJson<unknown>(path, { method: "GET" });
    } catch (error) {
      if (error instanceof ApiClientError && error.status === 404) {
        continue;
      }
      lastError = error;
      break;
    }
  }

  if (lastError) {
    throw lastError;
  }

  return null;
}

function isFallbackEnabled(error: unknown): boolean {
  if (!MOCK_FALLBACK_ENABLED) {
    return false;
  }
  if (error instanceof ApiClientError) {
    return error.status === 404 || error.status >= 500;
  }
  return true;
}

async function withFallback<T>(work: () => Promise<T>, fallback: () => T): Promise<T> {
  try {
    return await work();
  } catch (error) {
    if (!isFallbackEnabled(error)) {
      throw error;
    }
    return fallback();
  }
}

function toBackendConnectivityStatus(
  state: BackendConnectivityStatus["state"],
  detail: string,
): BackendConnectivityStatus {
  return {
    state,
    label: state === "connected" ? "Backend connected" : state === "mock_mode" ? "Mock mode active" : "Backend unavailable",
    detail,
    checked_at: new Date().toISOString(),
    mock_fallback_enabled: MOCK_FALLBACK_ENABLED,
  };
}

function normalizeRunRecord(value: unknown): RunRecord | null {
  if (!isRecord(value)) {
    return null;
  }

  const runId = asString(value.run_id, value.id);
  const createdAt = asString(value.created_at, value.createdAt);
  if (!runId || !createdAt) {
    return null;
  }

  const countriesSource = asArray(value.countries).filter((entry): entry is string => typeof entry === "string");
  const errorRecord = isRecord(value.error)
    ? {
        code: asString(value.error.code) ?? "error",
        message: asString(value.error.message) ?? "Unknown run error",
      }
    : null;

  return {
    run_id: runId,
    status: toRunStatus(value.status, "unknown"),
    created_at: createdAt,
    started_at: asString(value.started_at, value.startedAt),
    finished_at: asString(value.finished_at, value.finishedAt),
    countries: countriesSource,
    progress_percent: asNumber(value.progress_percent, value.progress),
    warning_count: asNumber(value.warning_count, value.warnings_count) ?? 0,
    error: errorRecord,
  };
}

function normalizeRunArtifactsResponse(value: unknown, runId: string): RunArtifactsResponse | null {
  if (!isRecord(value)) {
    return null;
  }
  const artifactsRaw = asArray(value.artifacts);
  const artifacts: ArtifactItem[] = artifactsRaw
    .map((entry, index) => {
      if (!isRecord(entry)) {
        return null;
      }
      const label = asString(entry.label, entry.name);
      const id = asString(entry.id, entry.key, label ? `artifact_${index}` : null);
      const path = asString(entry.path, entry.url, entry.download_url);
      if (!id || !label || !path) {
        return null;
      }
      const type = asString(entry.type)?.toLowerCase();
      const normalizedType =
        type === "json" || type === "csv" || type === "md" || type === "png" || type === "bundle"
          ? type
          : "other";
      return {
        id,
        label,
        type: normalizedType,
        path,
        size_bytes: asNumber(entry.size_bytes, entry.size) ?? undefined,
        available: asBoolean(entry.available, entry.is_available) ?? true,
        status: asString(entry.status)?.toLowerCase() ?? "available",
        created_at: asString(entry.created_at, entry.createdAt) ?? undefined,
        run_id: asString(entry.run_id) ?? runId,
      } satisfies ArtifactItem;
    })
    .filter(isPresent);

  const normalizedRunId = asString(value.run_id) ?? runId;
  return { run_id: normalizedRunId, artifacts };
}

function normalizeOverviewSnapshot(value: unknown): OverviewSnapshot | null {
  if (!isRecord(value)) {
    return null;
  }

  const merged: OverviewSnapshot = {
    ...FALLBACK_OVERVIEW,
  };

  merged.generated_at = asString(value.generated_at, value.generatedAt, value.timestamp) ?? merged.generated_at;

  const rankings = asArray(value.country_rankings ?? value.rankings)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const country = asString(entry.country, entry.country_code, entry.code);
      const score = asNumber(entry.score, entry.current_score);
      if (!country || score === null) {
        return null;
      }
      return {
        country,
        score,
        delta: asNumber(entry.delta, entry.delta_7d, entry.change) ?? 0,
        status: toWatchState(entry.status, "unknown"),
      };
    })
    .filter(isPresent);
  if (rankings.length > 0) {
    merged.country_rankings = rankings;
  }

  const changes = asArray(value.latest_changes ?? value.changes)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const label = asString(entry.label, entry.title);
      const detail = asString(entry.detail, entry.description, entry.message);
      if (!label || !detail) {
        return null;
      }
      return {
        label,
        detail,
        severity: (asString(entry.severity)?.toLowerCase() ?? "info") as "info" | "warn" | "critical",
      };
    })
    .filter(isPresent);
  if (changes.length > 0) {
    merged.latest_changes = changes;
  }

  const activeRuns = asArray(value.active_runs ?? value.runs)
    .map((entry) => normalizeRunRecord(entry))
    .filter(isPresent);
  if (activeRuns.length > 0) {
    merged.active_runs = activeRuns;
  }

  const metrics = asArray(value.metrics)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const id = asString(entry.id, entry.key);
      const label = asString(entry.label, entry.title);
      const valueNumber = asNumber(entry.value);
      const valueText = asString(entry.value);
      if (!id || !label || (valueNumber === null && valueText === null)) {
        return null;
      }
      return {
        id,
        label,
        value: valueNumber ?? valueText ?? 0,
        unit: asString(entry.unit) ?? undefined,
        change: asNumber(entry.change, entry.delta),
        status: (asString(entry.status)?.toLowerCase() ?? undefined) as "ok" | "info" | "warn" | "critical" | undefined,
      };
    })
    .filter(isPresent);
  if (metrics.length > 0) {
    merged.metrics = metrics;
  }

  const countries = asArray(value.countries ?? value.country_status)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const countryCode = asString(entry.country_code, entry.code, entry.country);
      const country = asString(entry.country, entry.label, countryCode);
      if (!countryCode || !country) {
        return null;
      }
      return {
        country,
        country_code: countryCode,
        status: toWatchState(entry.status, "unknown"),
        has_data: asBoolean(entry.has_data, entry.available) ?? true,
        score: asNumber(entry.score, entry.current_score),
        delta_7d: asNumber(entry.delta_7d, entry.delta, entry.change),
        confidence: asNumber(entry.confidence),
        freshness_hours: asNumber(entry.freshness_hours, entry.freshness),
        coverage_ratio: asNumber(entry.coverage_ratio, entry.coverage),
        last_updated: asString(entry.last_updated, entry.updated_at),
      };
    })
    .filter(isPresent);
  if (countries.length > 0) {
    merged.countries = countries;
  }

  if (isRecord(value.data_availability ?? value.availability)) {
    const summary = (value.data_availability ?? value.availability) as Record<string, unknown>;
    merged.data_availability = {
      available: asNumber(summary.available) ?? 0,
      partial: asNumber(summary.partial) ?? 0,
      stale: asNumber(summary.stale) ?? 0,
      missing: asNumber(summary.missing) ?? 0,
    };
  }

  return merged;
}

function normalizeCountryDetail(value: unknown, countryCode: string): CountryDetailResponse | null {
  const base = fallbackCountryDetail(countryCode);
  if (!isRecord(value)) {
    return null;
  }

  const merged: CountryDetailResponse = {
    ...base,
    country_code: asString(value.country_code, value.countryCode, value.code, base.country_code) ?? base.country_code,
    country_label: asString(value.country_label, value.country, value.label, base.country_label) ?? base.country_label,
    generated_at: asString(value.generated_at, value.generatedAt, value.timestamp) ?? base.generated_at,
    source_run_id: asString(value.source_run_id, value.run_id, value.sourceRunId) ?? base.source_run_id,
    summary: { ...base.summary },
  };

  const summary = isRecord(value.summary) ? value.summary : null;
  if (summary) {
    merged.summary = {
      status: toWatchState(summary.status, base.summary.status),
      confidence: asNumber(summary.confidence) ?? base.summary.confidence,
      freshness_hours: asNumber(summary.freshness_hours, summary.freshness) ?? base.summary.freshness_hours,
      last_updated: asString(summary.last_updated, summary.updated_at) ?? base.summary.last_updated,
    };
  }

  const kpis = asArray(value.kpis)
    .map((entry, index) => {
      if (!isRecord(entry)) {
        return null;
      }
      const id = asString(entry.id, entry.key, `kpi_${index}`);
      const label = asString(entry.label, entry.title);
      const numberValue = asNumber(entry.value);
      const textValue = asString(entry.value);
      if (!id || !label || (numberValue === null && textValue === null)) {
        return null;
      }
      return {
        id,
        label,
        value: numberValue ?? textValue ?? 0,
        unit: asString(entry.unit) ?? undefined,
        delta: asNumber(entry.delta, entry.change),
        status: (asString(entry.status)?.toLowerCase() ?? undefined) as "ok" | "info" | "warn" | "critical" | undefined,
      };
    })
    .filter(isPresent);
  if (kpis.length > 0) {
    merged.kpis = kpis;
  }

  const trendRaw = asArray(value.trend ?? value.series ?? value.time_series)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const timestamp = asString(entry.timestamp, entry.date, entry.period_start);
      if (!timestamp) {
        return null;
      }
      return {
        timestamp,
        value: asNumber(entry.value, entry.score),
        confidence: asNumber(entry.confidence),
        freshness_hours: asNumber(entry.freshness_hours, entry.freshness),
      };
    })
    .filter(isPresent);
  if (trendRaw.length > 0) {
    merged.trend = trendRaw;
  }

  const layers = asArray(value.layers)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const layerName = asString(entry.layer, entry.name);
      if (!layerName) {
        return null;
      }
      return {
        layer: layerName,
        value: asNumber(entry.value),
        status: toAvailability(entry.status, "missing"),
        freshness_hours: asNumber(entry.freshness_hours, entry.freshness),
        note: asString(entry.note, entry.message) ?? undefined,
      };
    })
    .filter(isPresent);
  if (layers.length > 0) {
    merged.layers = layers;
  }

  const dailyBriefing = asArray(value.daily_briefing ?? value.briefing)
    .filter((entry): entry is string => typeof entry === "string" && entry.trim().length > 0);
  if (dailyBriefing.length > 0) {
    merged.daily_briefing = dailyBriefing;
  }

  const longTermNotes = asArray(value.long_term_notes ?? value.long_term)
    .filter((entry): entry is string => typeof entry === "string" && entry.trim().length > 0);
  if (longTermNotes.length > 0) {
    merged.long_term_notes = longTermNotes;
  }

  if (isRecord(value.coverage)) {
    const coverage = value.coverage;
    merged.coverage = {
      ...(base.coverage ?? {}),
      available_layers: asNumber(coverage.available_layers) ?? base.coverage?.available_layers ?? 0,
      expected_layers: asNumber(coverage.expected_layers) ?? base.coverage?.expected_layers ?? 0,
      coverage_ratio: asNumber(coverage.coverage_ratio, coverage.coverage) ?? base.coverage?.coverage_ratio ?? 0,
      freshness_hours: asNumber(coverage.freshness_hours, coverage.freshness) ?? base.coverage?.freshness_hours,
      last_updated: asString(coverage.last_updated, coverage.updated_at) ?? base.coverage?.last_updated,
      warning_count: asNumber(coverage.warning_count, coverage.warnings) ?? base.coverage?.warning_count,
      layer_status: isRecord(coverage.layer_status)
        ? (coverage.layer_status as Record<string, AvailabilityState>)
        : base.coverage?.layer_status,
    };
  }

  const artifacts = normalizeRunArtifactsResponse({ run_id: merged.source_run_id, artifacts: value.artifacts }, merged.source_run_id ?? "unknown")?.artifacts;
  if (artifacts && artifacts.length > 0) {
    merged.artifacts = artifacts;
  }

  const notes = asArray(value.notes)
    .map((entry, index) => {
      if (!isRecord(entry)) {
        return null;
      }
      const text = asString(entry.text, entry.message);
      if (!text) {
        return null;
      }
      return {
        id: asString(entry.id, `${merged.country_code}_note_${index + 1}`) ?? `${merged.country_code}_note_${index + 1}`,
        text,
        severity: (asString(entry.severity)?.toLowerCase() ?? "info") as "info" | "warn" | "critical",
        source: asString(entry.source) ?? undefined,
      };
    })
    .filter(isPresent);
  if (notes.length > 0) {
    merged.notes = notes;
  }

  return merged;
}

function normalizeCoverage(value: unknown): CoverageResponse | null {
  if (!isRecord(value)) {
    return null;
  }

  const rows = asArray(value.rows ?? value.countries)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const code = asString(entry.country_code, entry.code, entry.country);
      const country = asString(entry.country, entry.label, code);
      if (!code || !country) {
        return null;
      }
      const layerStatusSource = isRecord(entry.layer_status) ? (entry.layer_status as Record<string, unknown>) : {};
      const layerStatus: Record<string, AvailabilityState> = {};
      for (const [key, raw] of Object.entries(layerStatusSource)) {
        layerStatus[key] = toAvailability(raw, "missing");
      }
      return {
        country,
        country_code: code,
        status: toAvailability(entry.status, "missing"),
        available_layers: asNumber(entry.available_layers) ?? 0,
        expected_layers: asNumber(entry.expected_layers) ?? 0,
        coverage_ratio: asNumber(entry.coverage_ratio, entry.coverage) ?? 0,
        freshness_hours: asNumber(entry.freshness_hours, entry.freshness),
        last_updated: asString(entry.last_updated, entry.updated_at),
        layer_status: layerStatus,
        warnings: asArray(entry.warnings).filter((item): item is string => typeof item === "string"),
      };
    })
    .filter(isPresent);

  if (rows.length === 0) {
    return null;
  }

  return {
    generated_at: asString(value.generated_at, value.generatedAt, value.timestamp) ?? new Date().toISOString(),
    layers: asArray(value.layers).filter((entry): entry is string => typeof entry === "string"),
    rows,
    warnings: asArray(value.warnings).filter((entry): entry is string => typeof entry === "string"),
  };
}

function normalizeCompare(value: unknown, countries: string[]): CompareResponse | null {
  if (!isRecord(value)) {
    return null;
  }

  const entries = asArray(value.countries ?? value.items)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const country = asString(entry.country, entry.country_code, entry.code);
      if (!country) {
        return null;
      }
      const trend = asArray(entry.trend ?? entry.series)
        .map((point) => {
          if (!isRecord(point)) {
            return null;
          }
          const timestamp = asString(point.timestamp, point.date, point.period_start);
          if (!timestamp) {
            return null;
          }
          return {
            timestamp,
            value: asNumber(point.value, point.score),
            confidence: asNumber(point.confidence),
            freshness_hours: asNumber(point.freshness_hours, point.freshness),
          };
        })
        .filter(isPresent);

      const kpis = asArray(entry.kpis)
        .map((kpi, index) => {
          if (!isRecord(kpi)) {
            return null;
          }
          const id = asString(kpi.id, `kpi_${index}`);
          const label = asString(kpi.label, kpi.title);
          const numValue = asNumber(kpi.value);
          const strValue = asString(kpi.value);
          if (!id || !label || (numValue === null && strValue === null)) {
            return null;
          }
          return {
            id,
            label,
            value: numValue ?? strValue ?? 0,
            unit: asString(kpi.unit) ?? undefined,
            delta: asNumber(kpi.delta, kpi.change),
            status: (asString(kpi.status)?.toLowerCase() ?? undefined) as "ok" | "info" | "warn" | "critical" | undefined,
          };
        })
        .filter(isPresent);

      return {
        country,
        status: toWatchState(entry.status, "unknown"),
        score: asNumber(entry.score, entry.current_score),
        delta_7d: asNumber(entry.delta_7d, entry.delta),
        confidence: asNumber(entry.confidence),
        freshness_hours: asNumber(entry.freshness_hours, entry.freshness),
        trend,
        kpis,
      };
    })
    .filter(isPresent);

  if (entries.length === 0 && countries.length > 0) {
    return null;
  }

  return {
    generated_at: asString(value.generated_at, value.generatedAt, value.timestamp) ?? new Date().toISOString(),
    warnings: asArray(value.warnings).filter((entry): entry is string => typeof entry === "string"),
    countries: entries,
  };
}

function normalizeArtifactsOverview(value: unknown): ArtifactsOverviewResponse | null {
  if (!isRecord(value)) {
    return null;
  }
  const runs = asArray(value.runs)
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const runId = asString(entry.run_id, entry.id);
      if (!runId) {
        return null;
      }
      const artifacts = normalizeRunArtifactsResponse({ run_id: runId, artifacts: entry.artifacts }, runId)?.artifacts ?? [];
      const bundle = artifacts.find((artifact) => artifact.type === "bundle") ?? null;
      return {
        run_id: runId,
        status: toRunStatus(entry.status, "unknown"),
        created_at: asString(entry.created_at, entry.createdAt),
        artifacts,
        bundle,
      };
    })
    .filter(isPresent);
  if (runs.length === 0) {
    return null;
  }
  return {
    generated_at: asString(value.generated_at, value.generatedAt, value.timestamp) ?? new Date().toISOString(),
    runs,
  };
}

function normalizeRunOptions(countriesPayload: unknown, layersPayload: unknown): RunOptionsResponse | null {
  const countriesRecord = isRecord(countriesPayload) ? countriesPayload : null;
  const layersRecord = isRecord(layersPayload) ? layersPayload : null;
  const countriesRaw = asArray(countriesRecord?.countries ?? countriesPayload);
  const layersRaw = asArray(layersRecord?.layers ?? layersPayload);

  const countries = countriesRaw
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const code = asString(entry.code, entry.country_code, entry.id);
      const label = asString(entry.label, entry.name, code);
      if (!code || !label) {
        return null;
      }
      return { code, label };
    })
    .filter(isPresent);

  const layers = layersRaw
    .map((entry) => {
      if (!isRecord(entry)) {
        return null;
      }
      const key = asString(entry.key, entry.id);
      const label = asString(entry.label, entry.name, key);
      if (!key || !label) {
        return null;
      }
      return {
        key,
        label,
        description: asString(entry.description) ?? undefined,
      };
    })
    .filter(isPresent);

  if (countries.length === 0 || layers.length === 0) {
    return null;
  }

  return {
    countries,
    layers,
    horizons: [7, 30, 356],
  };
}

function buildCoverageFromOverview(overview: OverviewSnapshot, options: RunOptionsResponse): CoverageResponse {
  const countries = overview.countries ?? [];
  const rankingsByCountry = new Map((overview.country_rankings ?? []).map((entry) => [entry.country, entry]));
  const countryRows = options.countries.map((countryOption) => {
    const countryData = countries.find(
      (entry) =>
        entry.country_code.toLowerCase() === countryOption.code.toLowerCase() ||
        entry.country.toLowerCase() === countryOption.label.toLowerCase(),
    );
    const ranking = rankingsByCountry.get(countryOption.code) ?? rankingsByCountry.get(countryOption.label);
    const coverageRatio = countryData?.coverage_ratio ?? (countryData?.has_data ? 0.72 : 0.0);
    const freshness = countryData?.freshness_hours ?? null;
    const status: AvailabilityState =
      coverageRatio < 0.45 ? "missing" : freshness !== null && freshness > 72 ? "stale" : coverageRatio < 0.75 ? "partial" : "ok";
    const layerStatus: Record<string, AvailabilityState> = {};
    for (const layer of options.layers) {
      layerStatus[layer.key] = status;
    }
    return {
      country: countryOption.label,
      country_code: countryOption.code,
      status,
      available_layers: Math.round(options.layers.length * coverageRatio),
      expected_layers: options.layers.length,
      coverage_ratio: coverageRatio,
      freshness_hours: freshness,
      last_updated: countryData?.last_updated ?? overview.generated_at,
      layer_status: layerStatus,
      warnings: status === "ok" ? [] : ["Derived from overview-level availability only."],
    };
  });

  return {
    generated_at: overview.generated_at ?? new Date().toISOString(),
    layers: options.layers.map((layer) => layer.key),
    rows: countryRows,
    warnings: ["Coverage response derived from available overview/options endpoints."],
  };
}

export const apiClient = {
  getBackendConnectivity(): Promise<BackendConnectivityStatus> {
    return requestJson<Record<string, unknown>>("/health", { method: "GET" })
      .then((payload) => {
        const statusText = asString(payload.status) ?? "ok";
        const detail =
          MOCK_FALLBACK_ENABLED
            ? `Health endpoint reachable (${statusText}). Mock fallback is enabled via NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true.`
            : `Health endpoint reachable (${statusText}).`;
        return toBackendConnectivityStatus("connected", detail);
      })
      .catch((error) => {
        if (MOCK_FALLBACK_ENABLED) {
          return toBackendConnectivityStatus(
            "mock_mode",
            "Backend is not reachable; frontend currently uses explicit mock/fallback paths.",
          );
        }
        return toBackendConnectivityStatus(
          "unavailable",
          error instanceof Error ? error.message : "Health probe failed.",
        );
      });
  },

  getHealth(): Promise<HealthResponse> {
    return withFallback(
      async () => {
        const payload = await requestJson<Record<string, unknown>>("/health", { method: "GET" });
        return {
          status: asString(payload.status) ?? "unknown",
          api_version: asString(payload.api_version, payload.version) ?? undefined,
          timestamp: asString(payload.timestamp) ?? undefined,
        };
      },
      () => FALLBACK_HEALTH,
    );
  },

  getRunOptions(): Promise<RunOptionsResponse> {
    return withFallback(
      async () => {
        const [countriesPayload, layersPayload] = await Promise.all([
          requestJson<unknown>("/options/countries", { method: "GET" }),
          requestJson<unknown>("/options/layers", { method: "GET" }),
        ]);
        const normalized = normalizeRunOptions(countriesPayload, layersPayload);
        if (!normalized) {
          throw new ApiClientError("/options/*", 422, "Unable to normalize options payload");
        }
        return normalized;
      },
      () => FALLBACK_OPTIONS,
    );
  },

  listRuns(): Promise<RunsResponse> {
    return withFallback(
      async () => {
        const payload = await requestJson<unknown>("/runs", { method: "GET" });
        const record = isRecord(payload) ? payload : {};
        const runs = asArray(record.runs ?? payload)
          .map((entry) => normalizeRunRecord(entry))
          .filter(isPresent);
        if (runs.length === 0) {
          throw new ApiClientError("/runs", 422, "No run records in response");
        }
        return { runs };
      },
      () => FALLBACK_RUNS,
    );
  },

  createRun(payload: RunCreateRequest): Promise<RunCreateResponse> {
    return (async () => {
      try {
        const response = await requestJson<unknown>("/runs", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        if (!isRecord(response)) {
          throw new ApiClientError("/runs", 422, "Unexpected createRun payload");
        }
        const runId = asString(response.run_id, response.id);
        const createdAt = asString(response.created_at, response.createdAt);
        if (!runId || !createdAt) {
          throw new ApiClientError("/runs", 422, "Missing run metadata in create response");
        }
        return {
          run_id: runId,
          status: toRunStatus(response.status, "queued"),
          created_at: createdAt,
          source: "api",
        };
      } catch (error) {
        if (MOCK_FALLBACK_ENABLED) {
          return {
            run_id: `mock_run_${Date.now()}`,
            status: "queued",
            created_at: new Date().toISOString(),
            source: "mock",
          } satisfies RunCreateResponse;
        }
        if (error instanceof ApiClientError) {
          throw new BackendUnavailableError("/runs", `Backend request failed: ${error.status}`, error);
        }
        throw new BackendUnavailableError(
          "/runs",
          "Run start failed because backend is unavailable and mock fallback is disabled.",
          error,
        );
      }
    })();
  },

  getRunDetail(runId: string): Promise<RunDetailResponse> {
    return withFallback(
      async () => {
        const payload = await requestJson<unknown>(`/runs/${encodePathPart(runId)}`, { method: "GET" });
        if (!isRecord(payload)) {
          throw new ApiClientError(`/runs/${runId}`, 422, "Unexpected run detail payload");
        }
        const run = normalizeRunRecord(payload.run ?? payload);
        if (!run) {
          throw new ApiClientError(`/runs/${runId}`, 422, "Missing run details");
        }
        return {
          run,
          metadata: isRecord(payload.metadata) ? payload.metadata : undefined,
        };
      },
      () => fallbackRunDetail(runId),
    );
  },

  getRunStatus(runId: string): Promise<RunStatusResponse> {
    return withFallback(
      async () => {
        const payload = await requestJson<unknown>(`/runs/${encodePathPart(runId)}/status`, { method: "GET" });
        if (!isRecord(payload)) {
          throw new ApiClientError(`/runs/${runId}/status`, 422, "Unexpected run status payload");
        }
        const normalized: RunStatusResponse = {
          run_id: asString(payload.run_id, runId) ?? runId,
          status: toRunStatus(payload.status, "unknown"),
          progress: isRecord(payload.progress)
            ? {
                phase: asString(payload.progress.phase) ?? undefined,
                percent: asNumber(payload.progress.percent, payload.progress.progress) ?? undefined,
                message: asString(payload.progress.message) ?? undefined,
              }
            : undefined,
          started_at: asString(payload.started_at, payload.startedAt),
          finished_at: asString(payload.finished_at, payload.finishedAt),
          updated_at: asString(payload.updated_at, payload.updatedAt) ?? undefined,
          error: isRecord(payload.error)
            ? {
                code: asString(payload.error.code) ?? "error",
                message: asString(payload.error.message) ?? "Unknown run status error",
              }
            : null,
        };
        return normalized;
      },
      () => fallbackRunStatus(runId),
    );
  },

  getRunSummary(runId: string): Promise<RunSummaryResponse> {
    return withFallback(
      async () => {
        const payload = await requestJson<unknown>(`/runs/${encodePathPart(runId)}/summary`, { method: "GET" });
        if (!isRecord(payload)) {
          throw new ApiClientError(`/runs/${runId}/summary`, 422, "Unexpected run summary payload");
        }
        const summary = isRecord(payload.summary) ? payload.summary : payload;
        const warnings = asArray(payload.warnings).filter((entry): entry is string => typeof entry === "string");
        return {
          run_id: asString(payload.run_id, runId) ?? runId,
          summary,
          warnings,
        };
      },
      () => fallbackRunSummary(runId),
    );
  },

  getRunArtifacts(runId: string): Promise<RunArtifactsResponse> {
    return withFallback(
      async () => {
        const payload = await requestJson<unknown>(`/runs/${encodePathPart(runId)}/artifacts`, { method: "GET" });
        const normalized = normalizeRunArtifactsResponse(payload, runId);
        if (!normalized) {
          throw new ApiClientError(`/runs/${runId}/artifacts`, 422, "Unexpected run artifacts payload");
        }
        return normalized;
      },
      () => fallbackRunArtifacts(runId),
    );
  },

  getOverviewSnapshot(): Promise<OverviewSnapshot> {
    return withFallback(
      async () => {
        const payload = await requestFirstAvailable(["/overview", "/dashboard/overview"]);
        if (!payload) {
          throw new ApiClientError("/overview", 404);
        }
        const normalized = normalizeOverviewSnapshot(payload);
        if (!normalized) {
          throw new ApiClientError("/overview", 422, "Unexpected overview payload");
        }
        return normalized;
      },
      () => FALLBACK_OVERVIEW,
    );
  },

  getCountryDetail(countryCode: string): Promise<CountryDetailResponse> {
    return withFallback(
      async () => {
        const encoded = encodePathPart(countryCode);
        const directPayload = await requestFirstAvailable([
          `/countries/${encoded}/detail`,
          `/countries/${encoded}/summary`,
          `/countries/${encoded}`,
        ]);
        if (directPayload) {
          const normalized = normalizeCountryDetail(directPayload, countryCode);
          if (normalized) {
            return normalized;
          }
        }

        const overviewPayload = await requestJsonOrNull("/overview");
        const overview = overviewPayload ? normalizeOverviewSnapshot(overviewPayload) : null;
        if (!overview) {
          throw new ApiClientError(`/countries/${encoded}`, 404, "Country endpoint and overview endpoint unavailable");
        }

        const derived = fallbackCountryDetail(countryCode);
        const overviewCountry =
          overview.countries?.find((entry) => entry.country_code.toLowerCase() === countryCode.toLowerCase()) ??
          overview.countries?.find((entry) => entry.country.toLowerCase() === countryCode.toLowerCase());
        const ranking =
          overview.country_rankings?.find((entry) => entry.country.toLowerCase() === countryCode.toLowerCase()) ??
          overview.country_rankings?.find((entry) => entry.country.toLowerCase() === derived.country_label.toLowerCase());

        if (overviewCountry || ranking) {
          derived.summary.status = overviewCountry?.status ?? ranking?.status ?? derived.summary.status;
          derived.summary.confidence = overviewCountry?.confidence ?? derived.summary.confidence;
          derived.summary.freshness_hours = overviewCountry?.freshness_hours ?? derived.summary.freshness_hours;
          derived.summary.last_updated = overviewCountry?.last_updated ?? overview.generated_at ?? derived.summary.last_updated;
          derived.kpis = derived.kpis.map((kpi) => {
            if (kpi.id === "score") {
              return {
                ...kpi,
                value: ranking?.score ?? overviewCountry?.score ?? kpi.value,
                delta: ranking?.delta ?? overviewCountry?.delta_7d ?? kpi.delta,
              };
            }
            if (kpi.id === "confidence" && overviewCountry?.confidence !== undefined && overviewCountry.confidence !== null) {
              return {
                ...kpi,
                value: Math.round(overviewCountry.confidence * 100),
              };
            }
            if (kpi.id === "freshness" && overviewCountry?.freshness_hours !== undefined && overviewCountry.freshness_hours !== null) {
              return {
                ...kpi,
                value: overviewCountry.freshness_hours,
              };
            }
            if (kpi.id === "coverage" && overviewCountry?.coverage_ratio !== undefined && overviewCountry.coverage_ratio !== null) {
              return {
                ...kpi,
                value: Math.round(overviewCountry.coverage_ratio * 100),
              };
            }
            return kpi;
          });
        }

        derived.notes = [
          {
            id: `${derived.country_code}_derived_overview`,
            text: "Country detail currently derived from overview payload because dedicated country endpoint is unavailable.",
            severity: "info",
            source: "frontend_adapter",
          },
          ...derived.notes,
        ];

        return derived;
      },
      () => fallbackCountryDetail(countryCode),
    );
  },

  getCoverage(): Promise<CoverageResponse> {
    return withFallback(
      async () => {
        const directPayload = await requestFirstAvailable(["/coverage", "/data-status", "/countries/coverage"]);
        if (directPayload) {
          const normalized = normalizeCoverage(directPayload);
          if (normalized) {
            return normalized;
          }
        }

        const [overviewPayload, countriesPayload, layersPayload] = await Promise.all([
          requestJsonOrNull("/overview"),
          requestJsonOrNull("/options/countries"),
          requestJsonOrNull("/options/layers"),
        ]);
        if (!overviewPayload || !countriesPayload || !layersPayload) {
          throw new ApiClientError("/coverage", 404, "Coverage endpoint unavailable and derive-path incomplete");
        }
        const overview = normalizeOverviewSnapshot(overviewPayload);
        const options = normalizeRunOptions(countriesPayload, layersPayload);
        if (!overview || !options) {
          throw new ApiClientError("/coverage", 422, "Unable to normalize derive-path payloads");
        }
        return buildCoverageFromOverview(overview, options);
      },
      () => FALLBACK_COVERAGE,
    );
  },

  getCompare(countries: string[]): Promise<CompareResponse> {
    return withFallback(
      async () => {
        const query = countries.length > 0 ? `?countries=${countries.map(encodeURIComponent).join(",")}` : "";
        const directPayload = await requestFirstAvailable([`/compare${query}`, `/countries/compare${query}`]);
        if (directPayload) {
          const normalized = normalizeCompare(directPayload, countries);
          if (normalized) {
            return normalized;
          }
        }

        const base = fallbackCompare(countries);
        const overviewPayload = await requestJsonOrNull("/overview");
        const overview = overviewPayload ? normalizeOverviewSnapshot(overviewPayload) : null;
        if (!overview) {
          throw new ApiClientError("/compare", 404, "Compare derive-path unavailable because overview endpoint is missing");
        }

        const rankings = new Map((overview.country_rankings ?? []).map((entry) => [entry.country.toLowerCase(), entry]));
        const status = new Map((overview.countries ?? []).map((entry) => [entry.country_code.toLowerCase(), entry]));
        return {
          ...base,
          generated_at: overview.generated_at ?? base.generated_at,
          countries: base.countries.map((entry) => {
            const rank = rankings.get(entry.country.toLowerCase());
            const availability = status.get(entry.country.toLowerCase());
            return {
              ...entry,
              status: availability?.status ?? rank?.status ?? entry.status,
              score: rank?.score ?? availability?.score ?? entry.score,
              delta_7d: rank?.delta ?? availability?.delta_7d ?? entry.delta_7d,
              confidence: availability?.confidence ?? entry.confidence,
              freshness_hours: availability?.freshness_hours ?? entry.freshness_hours,
            };
          }),
          warnings: [
            ...base.warnings,
            "Compare response is currently derived from overview endpoint (dedicated compare endpoint unavailable).",
          ],
        };
      },
      () => fallbackCompare(countries),
    );
  },

  getArtifactsOverview(): Promise<ArtifactsOverviewResponse> {
    return withFallback(
      async () => {
        const directPayload = await requestFirstAvailable(["/artifacts", "/runs/artifacts"]);
        if (directPayload) {
          const normalized = normalizeArtifactsOverview(directPayload);
          if (normalized) {
            return normalized;
          }
        }

        const runsResponse = await apiClient.listRuns();
        const runGroups = await Promise.all(
          runsResponse.runs.map(async (run) => {
            const payload = await requestJsonOrNull(`/runs/${encodePathPart(run.run_id)}/artifacts`);
            const artifacts =
              normalizeRunArtifactsResponse(payload ?? { run_id: run.run_id, artifacts: [] }, run.run_id)?.artifacts ?? [];
            const bundle = artifacts.find((artifact) => artifact.type === "bundle") ?? null;
            return {
              run_id: run.run_id,
              status: run.status,
              created_at: run.created_at,
              artifacts,
              bundle,
            };
          }),
        );
        return {
          generated_at: new Date().toISOString(),
          runs: runGroups,
        };
      },
      () => FALLBACK_ARTIFACTS_OVERVIEW,
    );
  },
};
