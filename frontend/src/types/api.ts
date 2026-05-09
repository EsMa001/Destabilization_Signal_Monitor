// Traceability: AP-04, AP-10
export type RunStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "completed"
  | "cancelled"
  | "unknown";

export type SeverityLevel = "info" | "warn" | "critical";
export type AvailabilityState = "ok" | "partial" | "stale" | "missing";
export type CountryWatchState = "active" | "watch" | "stable" | "unknown";
export type BackendConnectivityState = "connected" | "unavailable" | "mock_mode";

export interface ApiErrorPayload {
  code: string;
  message: string;
  details?: unknown;
  trace_id?: string;
}

export interface HealthResponse {
  status: string;
  api_version?: string;
  timestamp?: string;
}

export interface BackendConnectivityStatus {
  state: BackendConnectivityState;
  label: string;
  detail: string;
  checked_at: string;
  mock_fallback_enabled: boolean;
}

export interface CountryOption {
  code: string;
  label: string;
}

export interface LayerOption {
  key: string;
  label: string;
  description?: string;
}

export interface RunOptionsResponse {
  countries: CountryOption[];
  layers: LayerOption[];
  horizons: number[];
}

export interface RunCreateRequest {
  countries: string[];
  horizon_days: number;
  layers: string[];
  advanced?: {
    query_version?: string;
    scoring_version?: string;
    note?: string;
  };
}

export interface RunCreateResponse {
  run_id: string;
  status: RunStatus;
  created_at: string;
  source: "api" | "mock";
}

export interface RunRecord {
  run_id: string;
  status: RunStatus;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  countries: string[];
  progress_percent?: number | null;
  warning_count?: number;
  error?: ApiErrorPayload | null;
}

export interface RunsResponse {
  runs: RunRecord[];
}

export interface RunDetailResponse {
  run: RunRecord;
  metadata?: Record<string, unknown>;
}

export interface RunStatusResponse {
  run_id: string;
  status: RunStatus;
  progress?: {
    phase?: string;
    percent?: number;
    message?: string;
  };
  started_at?: string | null;
  finished_at?: string | null;
  updated_at?: string;
  error?: ApiErrorPayload | null;
}

export interface RunSummaryResponse {
  run_id: string;
  summary: Record<string, unknown>;
  warnings: string[];
}

export interface ArtifactItem {
  id: string;
  label: string;
  type: "json" | "csv" | "md" | "png" | "bundle" | "other";
  path: string;
  size_bytes?: number;
  available?: boolean;
  status?: string;
  created_at?: string;
  run_id?: string;
}

export interface RunArtifactsResponse {
  run_id: string;
  artifacts: ArtifactItem[];
}

export interface OverviewCountryRank {
  country: string;
  score: number;
  delta: number;
  status: CountryWatchState;
}

export interface OverviewChange {
  label: string;
  detail: string;
  severity: SeverityLevel;
}

export interface OverviewMetric {
  id: string;
  label: string;
  value: number | string;
  unit?: string;
  change?: number | null;
  status?: SeverityLevel | "ok";
}

export interface CountryAvailability {
  country: string;
  country_code: string;
  status: CountryWatchState;
  has_data: boolean;
  score?: number | null;
  delta_7d?: number | null;
  confidence?: number | null;
  freshness_hours?: number | null;
  coverage_ratio?: number | null;
  last_updated?: string | null;
}

export interface DataAvailabilitySummary {
  available: number;
  partial: number;
  stale: number;
  missing: number;
}

export interface OverviewSnapshot {
  generated_at?: string;
  country_rankings?: OverviewCountryRank[];
  latest_changes?: OverviewChange[];
  active_runs?: RunRecord[];
  metrics?: OverviewMetric[];
  countries?: CountryAvailability[];
  data_availability?: DataAvailabilitySummary;
}

export interface CountryKpi {
  id: string;
  label: string;
  value: number | string;
  unit?: string;
  delta?: number | null;
  status?: SeverityLevel | "ok";
}

export interface CountryTrendPoint {
  timestamp: string;
  value: number | null;
  confidence?: number | null;
  freshness_hours?: number | null;
}

export interface CountryLayerContribution {
  layer: string;
  value: number | null;
  status: AvailabilityState;
  freshness_hours?: number | null;
  note?: string;
}

export interface CountryCoverageSummary {
  available_layers: number;
  expected_layers: number;
  coverage_ratio: number;
  freshness_hours?: number | null;
  last_updated?: string | null;
  warning_count?: number;
  layer_status?: Record<string, AvailabilityState>;
}

export interface CountryNote {
  id: string;
  text: string;
  severity: SeverityLevel;
  source?: string;
}

export interface CountryDetailResponse {
  country_code: string;
  country_label: string;
  generated_at?: string;
  source_run_id?: string;
  summary: {
    status: CountryWatchState;
    confidence?: number | null;
    freshness_hours?: number | null;
    last_updated?: string | null;
  };
  kpis: CountryKpi[];
  daily_briefing: string[];
  long_term_notes: string[];
  trend: CountryTrendPoint[];
  layers: CountryLayerContribution[];
  coverage?: CountryCoverageSummary;
  artifacts: ArtifactItem[];
  notes: CountryNote[];
}

export interface CoverageRow {
  country: string;
  country_code: string;
  status: AvailabilityState;
  available_layers: number;
  expected_layers: number;
  coverage_ratio: number;
  freshness_hours?: number | null;
  last_updated?: string | null;
  layer_status: Record<string, AvailabilityState>;
  warnings: string[];
}

export interface CoverageResponse {
  generated_at?: string;
  layers: string[];
  rows: CoverageRow[];
  warnings: string[];
}

export interface CompareCountryEntry {
  country: string;
  status: CountryWatchState;
  score?: number | null;
  delta_7d?: number | null;
  confidence?: number | null;
  freshness_hours?: number | null;
  trend: CountryTrendPoint[];
  kpis: CountryKpi[];
}

export interface CompareResponse {
  generated_at?: string;
  warnings: string[];
  countries: CompareCountryEntry[];
}

export interface ArtifactRunGroup {
  run_id: string;
  status: RunStatus;
  created_at?: string | null;
  artifacts: ArtifactItem[];
  bundle?: ArtifactItem | null;
}

export interface ArtifactsOverviewResponse {
  generated_at?: string;
  runs: ArtifactRunGroup[];
}
