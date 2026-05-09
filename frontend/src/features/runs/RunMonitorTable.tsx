"use client";

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";

import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { usePolling } from "@/hooks/usePolling";
import { apiClient } from "@/lib/api/client";
import type { RunRecord, RunStatus } from "@/types/api";

interface RunsState {
  loading: boolean;
  error: string | null;
  runs: RunRecord[];
}

const RUN_FILTERS: Array<{ id: "all" | RunStatus; label: string }> = [
  { id: "all", label: "All" },
  { id: "running", label: "Running" },
  { id: "queued", label: "Queued" },
  { id: "failed", label: "Failed" },
  { id: "succeeded", label: "Succeeded" },
];

function formatTimestamp(value?: string | null): string {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("de-DE");
}

export function RunMonitorTable(): React.JSX.Element {
  const [statusFilter, setStatusFilter] = useState<"all" | RunStatus>("all");
  const [state, setState] = useState<RunsState>({
    loading: true,
    error: null,
    runs: [],
  });

  const loadRuns = useCallback(async () => {
    try {
      const response = await apiClient.listRuns();
      setState({
        loading: false,
        error: null,
        runs: response.runs,
      });
    } catch (error) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : "Unable to load runs",
        runs: [],
      });
    }
  }, []);

  usePolling(loadRuns, 10000, true);

  const filteredRuns = useMemo(() => {
    if (statusFilter === "all") {
      return state.runs;
    }
    return state.runs.filter((run) => run.status === statusFilter);
  }, [state.runs, statusFilter]);

  if (state.loading) {
    return <StateCard tone="loading" title="Loading runs" detail="Polling run state from backend API." />;
  }

  if (state.error) {
    return (
      <StateCard
        tone="error"
        title="Run monitor unavailable"
        detail={`${state.error}. Enable NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true for explicit mock run monitor mode.`}
      />
    );
  }

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title="Run Monitor"
          subtitle="Asynchronous run tracking with polling and direct jump to detail workspaces."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Runs" },
          ]}
        >
          <StatusBadge status="info" label="poll 10s" />
          <Link href="/runs/new" className="btn primary">
            New Run
          </Link>
        </PageHeader>
      </div>

      <div style={{ gridColumn: "span 12" }}>
        <Panel title="Asynchronous Run Monitor" data-testid="run-monitor-panel">
          <div
            style={{ display: "flex", justifyContent: "space-between", gap: "1rem", marginBottom: "0.8rem", flexWrap: "wrap" }}
            data-testid="run-monitor-controls"
          >
            <p className="muted" style={{ margin: 0 }}>
              Select a run to inspect detail, coverage implications, and artifacts.
            </p>
            <div className="filter-chip-row">
              {RUN_FILTERS.map((filter) => (
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
          </div>

          {filteredRuns.length === 0 ? (
            <StateCard tone="empty" title="No runs found for current filter" detail="Create a run from Run Builder to populate monitor." />
          ) : (
            <div className="table-wrap" data-testid="run-monitor-table">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Run ID</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>Countries</th>
                    <th>Created</th>
                    <th>Finished</th>
                    <th>Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRuns.map((run) => (
                    <tr key={run.run_id}>
                      <td>{run.run_id}</td>
                      <td>
                        <StatusBadge status={run.status} />
                      </td>
                      <td>{run.progress_percent ?? "-"}%</td>
                      <td>{run.countries.length}</td>
                      <td>{formatTimestamp(run.created_at)}</td>
                      <td>{formatTimestamp(run.finished_at)}</td>
                      <td>
                        <Link href={`/runs/${run.run_id}`} className="linkish">
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
    </div>
  );
}
