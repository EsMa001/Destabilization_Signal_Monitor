"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { TrendLineChart } from "@/components/charts/TrendLineChart";
import { ArtifactList } from "@/components/artifacts/ArtifactList";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { apiClient } from "@/lib/api/client";
import type { CountryDetailResponse } from "@/types/api";

type CountryViewMode = "daily" | "long_term";

interface CountryDetailViewProps {
  countryCode: string;
}

interface CountryDetailState {
  loading: boolean;
  error: string | null;
  payload: CountryDetailResponse | null;
}

export function CountryDetailView({ countryCode }: CountryDetailViewProps): React.JSX.Element {
  const [mode, setMode] = useState<CountryViewMode>("daily");
  const [state, setState] = useState<CountryDetailState>({
    loading: true,
    error: null,
    payload: null,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const payload = await apiClient.getCountryDetail(countryCode);
        if (!cancelled) {
          setState({
            loading: false,
            error: null,
            payload,
          });
        }
      } catch (error) {
        if (!cancelled) {
          setState({
            loading: false,
            error: error instanceof Error ? error.message : "Country detail load failed",
            payload: null,
          });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [countryCode]);

  const chartSeries = useMemo(() => {
    if (!state.payload) {
      return [];
    }
    return [
      {
        id: "score",
        label: "Score",
        color: "#51e1a5",
        points: state.payload.trend,
      },
      {
        id: "confidence",
        label: "Confidence x100",
        color: "#8ed0ff",
        points: state.payload.trend.map((point) => ({
          ...point,
          value: point.confidence !== null && point.confidence !== undefined ? point.confidence * 100 : null,
        })),
      },
    ];
  }, [state.payload]);

  const freshnessSeries = useMemo(() => {
    if (!state.payload) {
      return [];
    }
    return [
      {
        id: "freshness",
        label: "Freshness (h)",
        color: "#f6c77a",
        points: state.payload.trend.map((point) => ({
          ...point,
          value: point.freshness_hours ?? null,
        })),
      },
    ];
  }, [state.payload]);

  const dataWarnings = useMemo(() => {
    if (!state.payload) {
      return [];
    }
    const warnings: string[] = [];
    if (state.payload.trend.length < 3) {
      warnings.push("Trend series has limited depth.");
    }
    if (state.payload.coverage && state.payload.coverage.coverage_ratio < 0.6) {
      warnings.push("Coverage is below 60% and may bias interpretation.");
    }
    if (
      state.payload.summary.freshness_hours !== null &&
      state.payload.summary.freshness_hours !== undefined &&
      state.payload.summary.freshness_hours > 72
    ) {
      warnings.push("Latest update is stale (>72h).");
    }
    return warnings;
  }, [state.payload]);

  const compareCountryCode = state.payload?.country_code ?? countryCode;
  const compareQuery = useMemo(() => `?countries=${encodeURIComponent(compareCountryCode)}`, [compareCountryCode]);

  if (state.loading) {
    return <StateCard tone="loading" title={`Loading ${countryCode}`} detail="Fetching country summary, trend, coverage, and artifacts." />;
  }

  if (state.error && !state.payload) {
    return (
      <StateCard
        tone="error"
        title="Country detail unavailable"
        detail={`${state.error}. Enable NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true for explicit mock country mode.`}
      />
    );
  }

  if (!state.payload) {
    return <StateCard tone="empty" title="No country detail payload" detail="Country endpoint returned no payload." />;
  }

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title={`Country Detail / ${state.payload.country_label}`}
          subtitle="Daily briefing and long-term trend context with freshness/coverage diagnostics."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Countries", href: "/countries" },
            { label: state.payload.country_label },
          ]}
        >
          <StatusBadge
            status={state.payload.summary.status === "active" ? "error" : state.payload.summary.status === "watch" ? "warn" : "ok"}
            label={state.payload.summary.status}
          />
          <Link href={`/compare${compareQuery}`} className="btn">
            Compare
          </Link>
          {state.payload.source_run_id ? (
            <Link href={`/runs/${state.payload.source_run_id}`} className="btn">
              Source run
            </Link>
          ) : null}
        </PageHeader>
      </div>

      {dataWarnings.length > 0 ? (
        <div style={{ gridColumn: "span 12" }}>
          <StateCard tone="warn" title="Data quality note" detail={dataWarnings.join(" ")} />
        </div>
      ) : null}

      <div style={{ gridColumn: "span 12" }} className="kpi-grid">
        {state.payload.kpis.map((kpi) => (
          <KpiCard key={kpi.id} label={kpi.label} value={kpi.value} unit={kpi.unit} delta={kpi.delta} status={kpi.status} />
        ))}
      </div>

      <div style={{ gridColumn: "span 8", display: "grid", gap: "1rem" }}>
        <Panel title="Briefing Mode">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.8rem", flexWrap: "wrap" }}>
            <div className="toggle" role="tablist" aria-label="Country detail mode" data-testid="country-mode-toggle">
              <button
                type="button"
                role="tab"
                aria-selected={mode === "daily"}
                className={mode === "daily" ? "active" : ""}
                onClick={() => setMode("daily")}
                data-testid="country-mode-daily"
              >
                Daily Briefing
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={mode === "long_term"}
                className={mode === "long_term" ? "active" : ""}
                onClick={() => setMode("long_term")}
                data-testid="country-mode-long-term"
              >
                Long-Term Trends
              </button>
            </div>
            <StatusBadge status={mode === "daily" ? "ok" : "warn"} label={mode === "daily" ? "daily active" : "trend mode"} />
          </div>

          {mode === "daily" ? (
            <ul className="note-list" data-testid="country-briefing-content">
              {state.payload.daily_briefing.length === 0 ? (
                <li className="muted">No daily briefing entries available.</li>
              ) : (
                state.payload.daily_briefing.map((entry) => <li key={entry}>{entry}</li>)
              )}
            </ul>
          ) : (
            <ul className="note-list" data-testid="country-trend-content">
              {state.payload.long_term_notes.length === 0 ? (
                <li className="muted">No long-term notes available.</li>
              ) : (
                state.payload.long_term_notes.map((entry) => <li key={entry}>{entry}</li>)
              )}
            </ul>
          )}
        </Panel>

        <Panel title="Trend">
          <div style={{ display: "grid", gap: "1rem" }}>
            <div>
              <p className="panel-title">Score / Confidence</p>
              <TrendLineChart series={chartSeries} />
            </div>
            <div>
              <p className="panel-title">Freshness</p>
              <TrendLineChart series={freshnessSeries} height={170} />
            </div>
          </div>
        </Panel>

        <Panel title="Layer Contribution">
          {state.payload.layers.length === 0 ? (
            <StateCard tone="empty" title="No layer contribution data" />
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Layer</th>
                    <th>Value</th>
                    <th>Status</th>
                    <th>Freshness</th>
                  </tr>
                </thead>
                <tbody>
                  {state.payload.layers.map((layer) => (
                    <tr key={layer.layer}>
                      <td>{layer.layer}</td>
                      <td>{layer.value !== null ? layer.value.toFixed(2) : "n/a"}</td>
                      <td>
                        <StatusBadge status={layer.status === "missing" ? "error" : layer.status === "ok" ? "ok" : "warn"} label={layer.status} />
                      </td>
                      <td>{layer.freshness_hours !== null && layer.freshness_hours !== undefined ? `${layer.freshness_hours}h` : "n/a"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>

      <aside style={{ gridColumn: "span 4", display: "grid", gap: "1rem", alignContent: "start" }}>
        <Panel title="Status / Confidence / Freshness" high>
          <div className="status-matrix">
            <div>
              <p className="panel-title">Status</p>
              <StatusBadge
                status={state.payload.summary.status === "active" ? "error" : state.payload.summary.status === "watch" ? "warn" : "ok"}
                label={state.payload.summary.status}
              />
            </div>
            <div>
              <p className="panel-title">Confidence</p>
              <p className="kpi-value">{state.payload.summary.confidence !== null && state.payload.summary.confidence !== undefined ? `${Math.round(state.payload.summary.confidence * 100)}%` : "n/a"}</p>
            </div>
            <div>
              <p className="panel-title">Freshness</p>
              <p className="kpi-value">{state.payload.summary.freshness_hours !== null && state.payload.summary.freshness_hours !== undefined ? `${state.payload.summary.freshness_hours}h` : "n/a"}</p>
            </div>
            <div>
              <p className="panel-title">Updated</p>
              <p className="muted">{state.payload.summary.last_updated ? new Date(state.payload.summary.last_updated).toLocaleString("de-DE") : "n/a"}</p>
            </div>
          </div>
        </Panel>

        <Panel title="Coverage">
          {state.payload.coverage ? (
            <div className="table-wrap">
              <table className="data-table">
                <tbody>
                  <tr>
                    <td>Layer Coverage</td>
                    <td>{Math.round(state.payload.coverage.coverage_ratio * 100)}%</td>
                  </tr>
                  <tr>
                    <td>Available Layers</td>
                    <td>
                      {state.payload.coverage.available_layers}/{state.payload.coverage.expected_layers}
                    </td>
                  </tr>
                  <tr>
                    <td>Freshness</td>
                    <td>{state.payload.coverage.freshness_hours !== null && state.payload.coverage.freshness_hours !== undefined ? `${state.payload.coverage.freshness_hours}h` : "n/a"}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ) : (
            <StateCard tone="empty" title="No coverage summary" />
          )}
        </Panel>

        <Panel title="Artifacts">
          {state.payload.artifacts.length === 0 ? (
            <StateCard tone="empty" title="No country artifacts available" />
          ) : (
            <ArtifactList
              runs={[
                {
                  run_id: state.payload.source_run_id ?? `${state.payload.country_code}_run`,
                  status: "completed",
                  created_at: state.payload.generated_at ?? null,
                  artifacts: state.payload.artifacts,
                  bundle: state.payload.artifacts.find((artifact) => artifact.type === "bundle") ?? null,
                },
              ]}
            />
          )}
        </Panel>

        <Panel title="Notes">
          {state.payload.notes.length === 0 ? (
            <StateCard tone="empty" title="No notes" />
          ) : (
            <div style={{ display: "grid", gap: "0.55rem" }}>
              {state.payload.notes.map((note) => (
                <div key={note.id} className="insight-item">
                  <StatusBadge status={note.severity === "critical" ? "error" : note.severity} />
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {note.text}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Panel>
      </aside>
    </div>
  );
}
