"use client";

import { useEffect, useMemo, useState } from "react";

import { ArtifactList } from "@/components/artifacts/ArtifactList";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { apiClient } from "@/lib/api/client";
import type { ArtifactsOverviewResponse, RunStatus } from "@/types/api";

interface ArtifactsState {
  loading: boolean;
  error: string | null;
  payload: ArtifactsOverviewResponse | null;
}

const STATUS_FILTERS: Array<{ id: "all" | RunStatus; label: string }> = [
  { id: "all", label: "All" },
  { id: "running", label: "Running" },
  { id: "completed", label: "Completed" },
  { id: "succeeded", label: "Succeeded" },
  { id: "failed", label: "Failed" },
];

export function ArtifactsView(): React.JSX.Element {
  const [statusFilter, setStatusFilter] = useState<"all" | RunStatus>("all");
  const [availableOnly, setAvailableOnly] = useState(false);
  const [state, setState] = useState<ArtifactsState>({
    loading: true,
    error: null,
    payload: null,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const payload = await apiClient.getArtifactsOverview();
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
            error: error instanceof Error ? error.message : "Artifacts load failed",
            payload: null,
          });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredRuns = useMemo(() => {
    if (!state.payload) {
      return [];
    }
    return state.payload.runs
      .filter((run) => (statusFilter === "all" ? true : run.status === statusFilter))
      .map((run) => {
        if (!availableOnly) {
          return run;
        }
        return {
          ...run,
          artifacts: run.artifacts.filter((artifact) => artifact.available !== false),
        };
      })
      .filter((run) => run.artifacts.length > 0 || !availableOnly);
  }, [availableOnly, state.payload, statusFilter]);

  const summary = useMemo(() => {
    if (!state.payload) {
      return null;
    }
    const runs = state.payload.runs.length;
    const artifactCount = state.payload.runs.reduce((acc, run) => acc + run.artifacts.length, 0);
    const unavailableCount = state.payload.runs.reduce(
      (acc, run) => acc + run.artifacts.filter((artifact) => artifact.available === false).length,
      0,
    );
    const bundleCount = state.payload.runs.filter((run) => run.bundle !== null).length;
    return {
      runs,
      artifactCount,
      bundleCount,
      unavailableCount,
    };
  }, [state.payload]);

  if (state.loading) {
    return <StateCard tone="loading" title="Loading artifacts" detail="Collecting run artifacts and bundle availability." />;
  }

  if (state.error && !state.payload) {
    return <StateCard tone="error" title="Artifacts unavailable" detail={state.error} />;
  }

  if (!state.payload) {
    return <StateCard tone="empty" title="No artifact payload available" />;
  }

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title="Artifacts / Reports"
          subtitle="Run-grouped artifacts with availability status, bundle access, and diagnostics."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Artifacts" },
          ]}
        >
          <StatusBadge status={state.error ? "warn" : "ok"} label={state.error ? "partial" : "live"} />
        </PageHeader>
      </div>

      {summary ? (
        <div style={{ gridColumn: "span 12" }} className="kpi-grid">
          <KpiCard label="Runs" value={summary.runs} status="ok" />
          <KpiCard label="Artifacts" value={summary.artifactCount} status="info" />
          <KpiCard label="Bundles" value={summary.bundleCount} status={summary.bundleCount > 0 ? "ok" : "warn"} />
          <KpiCard label="Unavailable" value={summary.unavailableCount} status={summary.unavailableCount > 0 ? "warn" : "ok"} />
        </div>
      ) : null}

      <div style={{ gridColumn: "span 12" }}>
        <Panel title="Artifacts by Run" data-testid="artifacts-by-run-panel">
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.8rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
            <div className="filter-chip-row">
              {STATUS_FILTERS.map((filter) => (
                <button
                  key={filter.id}
                  type="button"
                  className={`chip-button ${statusFilter === filter.id ? "active" : ""}`}
                  onClick={() => setStatusFilter(filter.id)}
                >
                  {filter.label}
                </button>
              ))}
            </div>
            <label className="selection-item" style={{ width: "auto" }}>
              <input
                type="checkbox"
                checked={availableOnly}
                onChange={(event) => setAvailableOnly(event.target.checked)}
              />
              <span>Available only</span>
            </label>
          </div>

          {filteredRuns.length === 0 ? (
            <StateCard tone="empty" title="No artifacts found for current filter" detail="Adjust status filter or disable available-only mode." />
          ) : (
            <ArtifactList runs={filteredRuns} />
          )}
        </Panel>
      </div>
    </div>
  );
}
