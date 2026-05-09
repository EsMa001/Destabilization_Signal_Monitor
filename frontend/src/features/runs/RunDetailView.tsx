"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { usePolling } from "@/hooks/usePolling";
import { apiClient } from "@/lib/api/client";
import type { RunArtifactsResponse, RunDetailResponse, RunStatus, RunStatusResponse, RunSummaryResponse } from "@/types/api";

interface RunDetailState {
  loading: boolean;
  hardError: string | null;
  detail: RunDetailResponse | null;
  status: RunStatusResponse | null;
  summary: RunSummaryResponse | null;
  artifacts: RunArtifactsResponse | null;
  partialErrors: string[];
}

interface RunDetailViewProps {
  runId: string;
}

function formatDate(value?: string | null): string {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("de-DE");
}

function isTerminalStatus(status?: RunStatus | null): boolean {
  return status === "succeeded" || status === "failed" || status === "completed" || status === "cancelled";
}

export function RunDetailView({ runId }: RunDetailViewProps): React.JSX.Element {
  const [state, setState] = useState<RunDetailState>({
    loading: true,
    hardError: null,
    detail: null,
    status: null,
    summary: null,
    artifacts: null,
    partialErrors: [],
  });

  const loadRunWorkspace = useCallback(async () => {
    const [detailResult, statusResult, summaryResult, artifactsResult] = await Promise.allSettled([
      apiClient.getRunDetail(runId),
      apiClient.getRunStatus(runId),
      apiClient.getRunSummary(runId),
      apiClient.getRunArtifacts(runId),
    ]);

    const partialErrors: string[] = [];
    const detail = detailResult.status === "fulfilled" ? detailResult.value : null;
    const status = statusResult.status === "fulfilled" ? statusResult.value : null;
    const summary = summaryResult.status === "fulfilled" ? summaryResult.value : null;
    const artifacts = artifactsResult.status === "fulfilled" ? artifactsResult.value : null;

    if (detailResult.status === "rejected") {
      partialErrors.push("Run metadata unavailable.");
    }
    if (statusResult.status === "rejected") {
      partialErrors.push("Run status unavailable.");
    }
    if (summaryResult.status === "rejected") {
      partialErrors.push("Run summary unavailable.");
    }
    if (artifactsResult.status === "rejected") {
      partialErrors.push("Run artifacts unavailable.");
    }

    if (!detail && !status && !summary && !artifacts) {
      setState({
        loading: false,
        hardError: "No run detail endpoint delivered usable data.",
        detail: null,
        status: null,
        summary: null,
        artifacts: null,
        partialErrors,
      });
      return;
    }

    setState({
      loading: false,
      hardError: null,
      detail,
      status,
      summary,
      artifacts,
      partialErrors,
    });
  }, [runId]);

  const refreshRuntimeState = useCallback(async () => {
    try {
      const [status, artifacts] = await Promise.all([
        apiClient.getRunStatus(runId),
        apiClient.getRunArtifacts(runId),
      ]);
      setState((previous) => ({
        ...previous,
        status,
        artifacts,
      }));
    } catch {
      setState((previous) => previous);
    }
  }, [runId]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!cancelled) {
        await loadRunWorkspace();
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [loadRunWorkspace]);

  const shouldPoll = useMemo(() => {
    if (!state.status) {
      return false;
    }
    return !isTerminalStatus(state.status.status);
  }, [state.status]);

  usePolling(refreshRuntimeState, 12000, shouldPoll);

  if (state.loading) {
    return <StateCard tone="loading" title="Loading run detail" detail={`Resolving ${runId}`} />;
  }

  if (state.hardError) {
    return (
      <StateCard
        tone="error"
        title="Run detail unavailable"
        detail={`${state.hardError} Enable NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true for explicit mock detail mode.`}
      />
    );
  }

  const runRecord = state.detail?.run ?? null;
  const runStatus = state.status?.status ?? runRecord?.status ?? "unknown";
  const runCountries = runRecord?.countries ?? [];
  const compareQuery = runCountries.length > 0 ? runCountries.join(",") : "";
  const summaryEntries = Object.entries(state.summary?.summary ?? {});

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title={`Run Detail / ${runRecord?.run_id ?? runId}`}
          subtitle="Execution context, current status, summary diagnostics, and artifact access."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Runs", href: "/runs" },
            { label: runRecord?.run_id ?? runId },
          ]}
        >
          <StatusBadge status={runStatus} />
          <Link href="/runs" className="btn">
            Back
          </Link>
          {compareQuery ? (
            <Link href={`/compare?countries=${encodeURIComponent(compareQuery)}`} className="btn">
              Compare countries
            </Link>
          ) : null}
        </PageHeader>
      </div>

      {state.partialErrors.length > 0 ? (
        <div style={{ gridColumn: "span 12" }}>
          <StateCard tone="warn" title="Partial run payload" detail={state.partialErrors.join(" ")} />
        </div>
      ) : null}

      <div style={{ gridColumn: "span 8", display: "grid", gap: "1rem" }}>
        <Panel title="Run Snapshot">
          {!runRecord ? (
            <StateCard tone="warn" title="Run metadata unavailable" />
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Created</td>
                    <td>{formatDate(runRecord.created_at)}</td>
                  </tr>
                  <tr>
                    <td>Started</td>
                    <td>{formatDate(runRecord.started_at)}</td>
                  </tr>
                  <tr>
                    <td>Finished</td>
                    <td>{formatDate(runRecord.finished_at)}</td>
                  </tr>
                  <tr>
                    <td>Countries</td>
                    <td>{runCountries.length}</td>
                  </tr>
                  <tr>
                    <td>Warnings</td>
                    <td>{runRecord.warning_count ?? 0}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </Panel>

        <Panel title="Summary">
          {summaryEntries.length === 0 ? (
            <StateCard tone="empty" title="No summary payload available" />
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {summaryEntries.map(([key, value]) => (
                    <tr key={key}>
                      <td>{key}</td>
                      <td>
                        {typeof value === "number"
                          ? value.toLocaleString("de-DE", { maximumFractionDigits: 3 })
                          : value && typeof value === "object"
                            ? JSON.stringify(value)
                            : String(value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>

        <Panel title="Countries in Run">
          {runCountries.length === 0 ? (
            <StateCard tone="empty" title="No country list in run payload" />
          ) : (
            <div className="selection-grid">
              {runCountries.map((country) => (
                <Link key={country} href={`/countries/${country}`} className="btn">
                  {country}
                </Link>
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Warnings">
          {!state.summary || state.summary.warnings.length === 0 ? (
            <StateCard tone="empty" title="No warnings recorded for this run." />
          ) : (
            <div style={{ display: "grid", gap: "0.55rem" }}>
              {state.summary.warnings.map((warning) => (
                <div key={warning} className="panel high" style={{ padding: "0.65rem" }}>
                  <StatusBadge status="warn" label="warning" />
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {warning}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Panel>
      </div>

      <aside style={{ gridColumn: "span 4", display: "grid", gap: "1rem", alignContent: "start" }}>
        <Panel title="Runtime Status" high>
          {state.status ? (
            <div className="status-matrix">
              <div>
                <p className="panel-title">Status</p>
                <StatusBadge status={state.status.status} />
              </div>
              <div>
                <p className="panel-title">Phase</p>
                <p className="kpi-value" style={{ fontSize: "1.1rem" }}>
                  {state.status.progress?.phase ?? "-"}
                </p>
              </div>
              <div>
                <p className="panel-title">Progress</p>
                <p className="kpi-value">{state.status.progress?.percent ?? 0}%</p>
              </div>
              <div>
                <p className="panel-title">Updated</p>
                <p className="muted">{formatDate(state.status.updated_at)}</p>
              </div>
            </div>
          ) : (
            <StateCard tone="warn" title="No live status payload" />
          )}
        </Panel>

        <Panel title="Artifacts">
          {!state.artifacts ? (
            <StateCard tone="warn" title="Run artifacts unavailable" />
          ) : state.artifacts.artifacts.length === 0 ? (
            <StateCard tone="empty" title="No artifacts available." />
          ) : (
            <div style={{ display: "grid", gap: "0.6rem" }}>
              {state.artifacts.artifacts.map((artifact) => (
                <div key={artifact.id} className="panel">
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                    <strong>{artifact.label}</strong>
                    <StatusBadge
                      status={
                        artifact.available === false || artifact.status === "missing"
                          ? "error"
                          : artifact.status === "pending"
                            ? "warn"
                            : "ok"
                      }
                      label={artifact.status ?? (artifact.available === false ? "missing" : "available")}
                    />
                  </div>
                  <p className="muted" style={{ marginBottom: "0.45rem" }}>
                    {artifact.type}
                  </p>
                  {artifact.available === false ? (
                    <span className="muted">Unavailable</span>
                  ) : (
                    <a href={artifact.path} className="linkish">
                      Open
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Related Workspaces">
          <div style={{ display: "grid", gap: "0.5rem" }}>
            <Link href="/coverage" className="btn">
              Coverage
            </Link>
            <Link href="/artifacts" className="btn">
              Artifacts
            </Link>
            <Link href="/compare" className="btn">
              Compare
            </Link>
          </div>
        </Panel>
      </aside>
    </div>
  );
}
