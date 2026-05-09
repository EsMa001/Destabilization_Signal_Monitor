"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { InteractiveWorldMap } from "@/components/map/InteractiveWorldMap";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { apiClient } from "@/lib/api/client";
import type { CountryAvailability, HealthResponse, OverviewSnapshot } from "@/types/api";

interface OverviewState {
  health: HealthResponse | null;
  snapshot: OverviewSnapshot | null;
  error: string | null;
  loading: boolean;
}

type CountryFilter = "all" | "active" | "watch" | "stable" | "no_data";

interface FilterOption {
  id: CountryFilter;
  label: string;
}

const FILTERS: FilterOption[] = [
  { id: "all", label: "All" },
  { id: "active", label: "Active" },
  { id: "watch", label: "Watch" },
  { id: "stable", label: "Stable" },
  { id: "no_data", label: "No Data" },
];

function matchesFilter(country: CountryAvailability, filter: CountryFilter): boolean {
  if (filter === "all") {
    return true;
  }
  if (filter === "no_data") {
    return country.has_data === false;
  }
  return country.status === filter;
}

export function OverviewPage(): React.JSX.Element {
  const router = useRouter();
  const [countryFilter, setCountryFilter] = useState<CountryFilter>("all");
  const [state, setState] = useState<OverviewState>({
    health: null,
    snapshot: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [health, snapshot] = await Promise.all([apiClient.getHealth(), apiClient.getOverviewSnapshot()]);
        if (!cancelled) {
          setState({
            health,
            snapshot,
            error: null,
            loading: false,
          });
        }
      } catch (error) {
        if (!cancelled) {
          setState({
            health: null,
            snapshot: null,
            error: error instanceof Error ? error.message : "Unknown overview error",
            loading: false,
          });
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const derived = useMemo(() => {
    const snapshot = state.snapshot;
    if (!snapshot) {
      return null;
    }
    const rankings = snapshot.country_rankings ?? [];
    const countries = snapshot.countries ?? [];
    const metrics =
      snapshot.metrics && snapshot.metrics.length > 0
        ? snapshot.metrics
        : [
            { id: "countries", label: "Countries", value: countries.length || rankings.length, status: "ok" as const },
            { id: "active_runs", label: "Active Runs", value: (snapshot.active_runs ?? []).length, status: "ok" as const },
            {
              id: "watchlist",
              label: "Active/Watch",
              value: rankings.filter((entry) => entry.status !== "stable").length,
              status: "warn" as const,
            },
          ];
    const staleCountries = countries.filter(
      (entry) => entry.freshness_hours !== null && entry.freshness_hours !== undefined && entry.freshness_hours > 72,
    );
    const missingCountries = countries.filter((entry) => !entry.has_data || (entry.coverage_ratio ?? 1) < 0.45);

    return {
      metrics,
      countries,
      rankings,
      activeRuns: snapshot.active_runs ?? [],
      changes: snapshot.latest_changes ?? [],
      generatedAt: snapshot.generated_at,
      availability: snapshot.data_availability,
      staleCountries,
      missingCountries,
    };
  }, [state.snapshot]);

  const filteredCountries = useMemo(() => {
    if (!derived) {
      return [];
    }
    return derived.countries.filter((country) => matchesFilter(country, countryFilter));
  }, [countryFilter, derived]);

  const filteredRankings = useMemo(() => {
    if (!derived) {
      return [];
    }
    if (countryFilter === "all") {
      return derived.rankings;
    }
    const allowed = new Set(
      filteredCountries.flatMap((country) => [country.country_code.toLowerCase(), country.country.toLowerCase()]),
    );
    return derived.rankings.filter((entry) => allowed.has(entry.country.toLowerCase()));
  }, [countryFilter, derived, filteredCountries]);

  if (state.loading) {
    return <StateCard tone="loading" title="Loading overview" detail="Collecting global indicators and run context." />;
  }

  if (state.error) {
    return (
      <StateCard
        tone="error"
        title="Overview currently unavailable"
        detail={`${state.error}. Enable NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true for explicit mock fallback mode.`}
      />
    );
  }

  if (!derived) {
    return <StateCard tone="empty" title="No overview data yet" detail="Run the pipeline to populate overview indicators." />;
  }

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title="Global Overview"
          subtitle="Operational signal map, active run context, and country-level prioritization."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Overview" },
          ]}
        >
          <StatusBadge status={state.health?.status === "degraded_fallback" ? "warn" : "ok"} label={state.health?.status ?? "unknown"} />
          <Link href="/runs/new" className="btn">
            Start Run
          </Link>
          <Link href="/coverage" className="btn">
            Coverage
          </Link>
        </PageHeader>
      </div>

      <div style={{ gridColumn: "span 12" }} className="kpi-grid">
        {derived.metrics.map((metric) => (
          <KpiCard
            key={metric.id}
            label={metric.label}
            value={metric.value}
            unit={metric.unit}
            delta={metric.change}
            status={metric.status}
          />
        ))}
      </div>

      <div style={{ gridColumn: "span 8", display: "grid", gap: "1rem" }}>
        <Panel title="World Availability Map" high data-testid="overview-map-panel">
          <div className="filter-chip-row" data-testid="overview-map-filter-row">
            {FILTERS.map((filter) => (
              <button
                key={filter.id}
                type="button"
                className={`chip-button ${countryFilter === filter.id ? "active" : ""}`}
                onClick={() => setCountryFilter(filter.id)}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {filteredCountries.length === 0 ? (
            <StateCard
              tone="empty"
              title="No countries for current filter"
              detail="Adjust status filter to inspect other country states."
            />
          ) : (
            <InteractiveWorldMap
              countries={filteredCountries}
              onCountrySelect={(countryCode) => router.push(`/countries/${countryCode}`)}
            />
          )}

          {countryFilter !== "all" ? (
            <p className="muted" style={{ marginBottom: 0 }}>
              Showing {filteredCountries.length} of {derived.countries.length} countries for filter {countryFilter}.
            </p>
          ) : null}
        </Panel>

        <Panel title="Country Rankings">
          {filteredRankings.length === 0 ? (
            <StateCard tone="empty" title="No rankings available for this filter" />
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Country</th>
                    <th>Score</th>
                    <th>Delta 7d</th>
                    <th>Status</th>
                    <th>Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRankings.map((entry) => (
                    <tr key={entry.country}>
                      <td>{entry.country}</td>
                      <td>{entry.score.toFixed(2)}</td>
                      <td>{entry.delta > 0 ? `+${entry.delta.toFixed(2)}` : entry.delta.toFixed(2)}</td>
                      <td>
                        <StatusBadge
                          status={entry.status === "active" ? "error" : entry.status === "watch" ? "warn" : "ok"}
                          label={entry.status}
                        />
                      </td>
                      <td>
                        <Link href={`/countries/${entry.country}`} className="linkish">
                          Open
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>

      <aside style={{ gridColumn: "span 4", display: "grid", gap: "1rem", alignContent: "start" }}>
        <Panel title="Insight Rail" high>
          {derived.changes.length === 0 ? (
            <StateCard tone="empty" title="No highlighted changes" />
          ) : (
            <div style={{ display: "grid", gap: "0.6rem" }}>
              {derived.changes.map((change) => (
                <div key={change.label} className="insight-item">
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                    <strong>{change.label}</strong>
                    <StatusBadge status={change.severity === "critical" ? "error" : change.severity} />
                  </div>
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {change.detail}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Active Runs">
          {derived.activeRuns.length === 0 ? (
            <StateCard tone="empty" title="No active runs" />
          ) : (
            <div style={{ display: "grid", gap: "0.55rem" }}>
              {derived.activeRuns.map((run) => (
                <div key={run.run_id} className="panel high">
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                    <strong>{run.run_id}</strong>
                    <StatusBadge status={run.status} />
                  </div>
                  <p className="muted" style={{ marginBottom: "0.55rem" }}>
                    {run.countries.length} countries | {run.progress_percent ?? 0}%
                  </p>
                  <Link href={`/runs/${run.run_id}`} className="linkish">
                    Open run detail
                  </Link>
                </div>
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Data Availability">
          {derived.availability ? (
            <div className="availability-grid">
              <KpiCard label="Available" value={derived.availability.available} status="ok" />
              <KpiCard label="Partial" value={derived.availability.partial} status="warn" />
              <KpiCard label="Stale" value={derived.availability.stale} status="warn" />
              <KpiCard label="Missing" value={derived.availability.missing} status="critical" />
            </div>
          ) : (
            <StateCard tone="empty" title="No availability summary" detail="Coverage summary was not provided by current API payload." />
          )}

          {derived.staleCountries.length > 0 ? (
            <div style={{ marginTop: "0.65rem" }}>
              <StateCard tone="warn" title={`${derived.staleCountries.length} stale country records`} />
            </div>
          ) : null}
          {derived.missingCountries.length > 0 ? (
            <div style={{ marginTop: "0.65rem" }}>
              <StateCard tone="warn" title={`${derived.missingCountries.length} low-coverage country records`} />
            </div>
          ) : null}

          <p className="muted" style={{ marginBottom: 0 }}>
            Generated: {derived.generatedAt ? new Date(derived.generatedAt).toLocaleString("de-DE") : "n/a"}
          </p>
        </Panel>
      </aside>
    </div>
  );
}
