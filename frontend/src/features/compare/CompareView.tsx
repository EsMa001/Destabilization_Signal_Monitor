"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

import { TrendLineChart } from "@/components/charts/TrendLineChart";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { apiClient } from "@/lib/api/client";
import type { CompareResponse, RunOptionsResponse } from "@/types/api";

interface CompareState {
  loading: boolean;
  refreshing: boolean;
  options: RunOptionsResponse | null;
  compare: CompareResponse | null;
  error: string | null;
}

function parseCountriesQuery(raw: string | null): string[] {
  if (!raw) {
    return [];
  }
  return raw
    .split(",")
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0)
    .slice(0, 6);
}

export function CompareView(): React.JSX.Element {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchParamsString = searchParams.toString();
  const initialQueryCountries = useMemo(
    () => parseCountriesQuery(new URLSearchParams(searchParamsString).get("countries")),
    [searchParamsString],
  );

  const skipRefreshRef = useRef(false);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [state, setState] = useState<CompareState>({
    loading: true,
    refreshing: false,
    options: null,
    compare: null,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const options = await apiClient.getRunOptions();
        const allowed = new Set(options.countries.map((country) => country.code.toLowerCase()));
        const sanitizedQuery = initialQueryCountries.filter((country) => allowed.has(country.toLowerCase()));
        const initialSelection =
          sanitizedQuery.length > 0
            ? sanitizedQuery
            : options.countries.slice(0, 3).map((entry) => entry.code);
        const compare = await apiClient.getCompare(initialSelection);
        if (!cancelled) {
          skipRefreshRef.current = true;
          setSelectedCountries(initialSelection);
          setState({
            loading: false,
            refreshing: false,
            options,
            compare,
            error: null,
          });
        }
      } catch (error) {
        if (!cancelled) {
          setState({
            loading: false,
            refreshing: false,
            options: null,
            compare: null,
            error: error instanceof Error ? error.message : "Compare loading failed",
          });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [initialQueryCountries]);

  useEffect(() => {
    if (!state.options) {
      return;
    }
    const currentParams = new URLSearchParams(searchParamsString);
    const currentCountriesParam = currentParams.get("countries") ?? "";
    const targetCountriesParam = selectedCountries.join(",");
    const params = new URLSearchParams(searchParamsString);
    if (selectedCountries.length === 0) {
      params.delete("countries");
    } else {
      params.set("countries", targetCountriesParam);
    }
    if (
      (selectedCountries.length === 0 && currentCountriesParam.length > 0) ||
      (selectedCountries.length > 0 && currentCountriesParam !== targetCountriesParam)
    ) {
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    }

    if (selectedCountries.length === 0) {
      setState((previous) => ({
        ...previous,
        compare: previous.compare
          ? {
              ...previous.compare,
              countries: [],
            }
          : previous.compare,
      }));
      return;
    }

    if (skipRefreshRef.current) {
      skipRefreshRef.current = false;
      return;
    }

    let cancelled = false;

    (async () => {
      setState((previous) => ({
        ...previous,
        refreshing: true,
      }));
      try {
        const compare = await apiClient.getCompare(selectedCountries);
        if (!cancelled) {
          setState((previous) => ({
            ...previous,
            compare,
            refreshing: false,
            error: null,
          }));
        }
      } catch (error) {
        if (!cancelled) {
          setState((previous) => ({
            ...previous,
            refreshing: false,
            error: error instanceof Error ? error.message : "Compare refresh failed",
          }));
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [pathname, router, searchParamsString, selectedCountries, state.options]);

  const summary = useMemo(() => {
    if (!state.compare) {
      return null;
    }
    const scores = state.compare.countries
      .map((entry) => entry.score)
      .filter((value): value is number => value !== null && value !== undefined);
    const avg = scores.length > 0 ? scores.reduce((acc, entry) => acc + entry, 0) / scores.length : null;
    return {
      selected: state.compare.countries.length,
      averageScore: avg,
      warnings: state.compare.warnings.length,
    };
  }, [state.compare]);

  const peaks = useMemo(() => {
    if (!state.compare) {
      return [];
    }
    return state.compare.countries.map((entry) => {
      const numericTrend = entry.trend.filter((point): point is { timestamp: string; value: number } => point.value !== null);
      const peak = numericTrend.reduce(
        (acc, point) => (point.value > acc.value ? { value: point.value, timestamp: point.timestamp } : acc),
        { value: Number.NEGATIVE_INFINITY, timestamp: "" },
      );
      const first = numericTrend[0]?.value ?? null;
      const last = numericTrend[numericTrend.length - 1]?.value ?? null;
      return {
        country: entry.country,
        peakValue: Number.isFinite(peak.value) ? peak.value : null,
        peakDate: peak.timestamp,
        spanDelta: first !== null && last !== null ? last - first : null,
      };
    });
  }, [state.compare]);

  if (state.loading) {
    return <StateCard tone="loading" title="Loading compare workspace" detail="Fetching country options and initial compare payload." />;
  }

  if (state.error && !state.compare) {
    return <StateCard tone="error" title="Compare unavailable" detail={state.error} />;
  }

  if (!state.options || !state.compare) {
    return <StateCard tone="empty" title="No compare data available" detail="Country compare payload is empty." />;
  }

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title="Country Compare"
          subtitle="Multi-country KPI, trend, and peak comparison workspace."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Compare" },
          ]}
        >
          {state.refreshing ? <StatusBadge status="info" label="refreshing" /> : null}
          {state.error ? <StatusBadge status="warn" label="partial" /> : <StatusBadge status="ok" label="live" />}
        </PageHeader>
      </div>

      {summary ? (
        <div style={{ gridColumn: "span 12" }} className="kpi-grid">
          <KpiCard label="Selected Countries" value={summary.selected} status="ok" />
          <KpiCard label="Average Score" value={summary.averageScore ? summary.averageScore.toFixed(2) : "n/a"} status="info" />
          <KpiCard label="Warnings" value={summary.warnings} status={summary.warnings > 0 ? "warn" : "ok"} />
        </div>
      ) : null}

      <div style={{ gridColumn: "span 12" }}>
        <Panel title="Country Selection" data-testid="compare-selection-panel">
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.9rem", marginBottom: "0.6rem", flexWrap: "wrap" }}>
            <p className="muted" style={{ margin: 0 }}>
              Choose 2 to 6 countries for balanced comparison depth.
            </p>
            <div style={{ display: "flex", gap: "0.45rem" }}>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const defaults = state.options?.countries.slice(0, 3).map((entry) => entry.code) ?? [];
                  skipRefreshRef.current = false;
                  setSelectedCountries(defaults);
                }}
                data-testid="compare-top3-button"
              >
                Top 3
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  skipRefreshRef.current = false;
                  setSelectedCountries([]);
                }}
                data-testid="compare-clear-button"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="selection-grid">
            {state.options.countries.map((country) => (
              <label key={country.code} className="selection-item">
                <input
                  type="checkbox"
                  checked={selectedCountries.includes(country.code)}
                  onChange={(event) => {
                    setSelectedCountries((previous) => {
                      if (event.target.checked) {
                        return Array.from(new Set([...previous, country.code])).slice(0, 6);
                      }
                      return previous.filter((item) => item !== country.code);
                    });
                  }}
                  data-testid={`compare-country-checkbox-${country.code.toLowerCase()}`}
                />
                <span>{country.label}</span>
              </label>
            ))}
          </div>

          {selectedCountries.length < 2 ? (
            <div style={{ marginTop: "0.7rem" }}>
              <StateCard tone="warn" title="Select at least two countries for meaningful comparison." />
            </div>
          ) : null}
        </Panel>
      </div>

      <div style={{ gridColumn: "span 8", display: "grid", gap: "1rem" }}>
        <Panel title="Trend Comparison" data-testid="compare-trend-panel">
          <TrendLineChart
            series={state.compare.countries.map((entry, index) => ({
              id: entry.country,
              label: entry.country,
              color: ["#51e1a5", "#8ed0ff", "#f6c77a", "#ffb4ab", "#c8f9e2", "#89b4fa"][index % 6],
              points: entry.trend,
            }))}
          />
        </Panel>

        <Panel title="KPI Comparison">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Country</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Delta 7d</th>
                  <th>Confidence</th>
                  <th>Freshness</th>
                </tr>
              </thead>
              <tbody>
                {state.compare.countries.map((entry) => (
                  <tr key={entry.country}>
                    <td>{entry.country}</td>
                    <td>
                      <StatusBadge status={entry.status === "active" ? "error" : entry.status === "watch" ? "warn" : "ok"} label={entry.status} />
                    </td>
                    <td>{entry.score !== null && entry.score !== undefined ? entry.score.toFixed(2) : "n/a"}</td>
                    <td>{entry.delta_7d !== null && entry.delta_7d !== undefined ? `${entry.delta_7d > 0 ? "+" : ""}${entry.delta_7d.toFixed(2)}` : "n/a"}</td>
                    <td>{entry.confidence !== null && entry.confidence !== undefined ? `${Math.round(entry.confidence * 100)}%` : "n/a"}</td>
                    <td>{entry.freshness_hours !== null && entry.freshness_hours !== undefined ? `${entry.freshness_hours}h` : "n/a"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Peak Comparison">
          {peaks.length === 0 ? (
            <StateCard tone="empty" title="No peak data available" />
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Country</th>
                    <th>Peak</th>
                    <th>Peak Date</th>
                    <th>Span Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {peaks.map((peak) => (
                    <tr key={peak.country}>
                      <td>{peak.country}</td>
                      <td>{peak.peakValue !== null ? peak.peakValue.toFixed(2) : "n/a"}</td>
                      <td>{peak.peakDate ? new Date(peak.peakDate).toLocaleDateString("de-DE") : "n/a"}</td>
                      <td>{peak.spanDelta !== null ? `${peak.spanDelta > 0 ? "+" : ""}${peak.spanDelta.toFixed(2)}` : "n/a"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>

      <aside style={{ gridColumn: "span 4", display: "grid", gap: "1rem", alignContent: "start" }}>
        <Panel title="Compare Notes" high>
          {state.compare.warnings.length === 0 ? (
            <StateCard tone="empty" title="No compare warnings" />
          ) : (
            <div style={{ display: "grid", gap: "0.6rem" }}>
              {state.compare.warnings.map((warning) => (
                <div key={warning} className="insight-item">
                  <StatusBadge status="warn" label="warning" />
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {warning}
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
