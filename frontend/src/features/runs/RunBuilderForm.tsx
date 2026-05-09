"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { BackendUnavailableError, apiClient } from "@/lib/api/client";
import type { BackendConnectivityStatus, RunCreateRequest, RunCreateResponse, RunOptionsResponse } from "@/types/api";

type SubmitState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; payload: RunCreateResponse }
  | { kind: "error"; message: string };

const DEFAULT_LAYERS = ["event", "market_food", "governance"];

export function RunBuilderForm(): React.JSX.Element {
  const [options, setOptions] = useState<RunOptionsResponse | null>(null);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<BackendConnectivityStatus | null>(null);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [selectedLayers, setSelectedLayers] = useState<string[]>(DEFAULT_LAYERS);
  const [horizon, setHorizon] = useState(30);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [note, setNote] = useState("");
  const [submitState, setSubmitState] = useState<SubmitState>({ kind: "idle" });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [optionsResult, backendStatusResult] = await Promise.allSettled([
        apiClient.getRunOptions(),
        apiClient.getBackendConnectivity(),
      ]);

      if (cancelled) {
        return;
      }

      if (optionsResult.status === "fulfilled") {
        const loaded = optionsResult.value;
        setOptions(loaded);
        setSelectedCountries(loaded.countries.slice(0, 3).map((entry) => entry.code));
        setHorizon(loaded.horizons[1] ?? loaded.horizons[0] ?? 30);
      } else {
        setOptionsError(
          optionsResult.reason instanceof Error ? optionsResult.reason.message : "Unable to load run options",
        );
      }

      if (backendStatusResult.status === "fulfilled") {
        setBackendStatus(backendStatusResult.value);
      } else {
        setBackendStatus({
          state: "unavailable",
          label: "Backend unavailable",
          detail:
            backendStatusResult.reason instanceof Error
              ? backendStatusResult.reason.message
              : "Backend connectivity probe failed.",
          checked_at: new Date().toISOString(),
          mock_fallback_enabled: false,
        });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const backendUnavailable = backendStatus?.state === "unavailable";
  const backendStatusBadge = useMemo(() => {
    if (!backendStatus) {
      return { status: "info" as const, label: "backend checking" };
    }
    if (backendStatus.state === "connected") {
      return { status: "ok" as const, label: "backend connected" };
    }
    if (backendStatus.state === "mock_mode") {
      return { status: "warn" as const, label: "mock mode active" };
    }
    return { status: "error" as const, label: "backend unavailable" };
  }, [backendStatus]);

  const summary = useMemo(() => {
    return {
      countryCount: selectedCountries.length,
      layerCount: selectedLayers.length,
      horizon,
      countriesPreview: selectedCountries.slice(0, 4).join(", "),
    };
  }, [selectedCountries, selectedLayers, horizon]);

  if (optionsError) {
    return (
      <StateCard
        tone="error"
        title="Run builder options unavailable"
        detail={`${optionsError}. Backend required unless NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true is enabled.`}
      />
    );
  }

  if (!options) {
    return <StateCard tone="loading" title="Loading run options" detail="Fetching countries and layers." />;
  }

  const submitDisabled =
    submitState.kind === "submitting" || selectedCountries.length === 0 || selectedLayers.length === 0 || backendUnavailable;

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const payload: RunCreateRequest = {
      countries: selectedCountries,
      horizon_days: horizon,
      layers: selectedLayers,
      advanced: {
        query_version: "v1",
        scoring_version: "v4.3",
        note: note || undefined,
      },
    };

    setSubmitState({ kind: "submitting" });
    try {
      const created = await apiClient.createRun(payload);
      setSubmitState({ kind: "success", payload: created });
    } catch (error) {
      const message =
        error instanceof BackendUnavailableError
          ? "Backend unavailable. Start the API service or enable NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true for explicit mock runs."
          : error instanceof Error
            ? error.message
            : "Run submit failed";
      setSubmitState({
        kind: "error",
        message,
      });
    }
  }

  return (
    <div className="page-grid" data-testid="run-builder-page">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title="Run Builder"
          subtitle="Define countries, layers, and horizon, then start an async analysis run."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Runs", href: "/runs" },
            { label: "Run Builder" },
          ]}
        >
          <div data-testid="run-builder-backend-state">
            <StatusBadge status={backendStatusBadge.status} label={backendStatusBadge.label} />
          </div>
          <Link href="/runs" className="btn">
            Monitor
          </Link>
        </PageHeader>
      </div>

      {backendStatus?.state === "unavailable" ? (
        <div style={{ gridColumn: "span 12" }}>
          <StateCard
            tone="error"
            title="Backend unavailable"
            detail="Run creation is blocked while mock fallback is disabled. Start backend API or explicitly enable NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true."
            data-testid="run-builder-backend-unavailable"
          />
        </div>
      ) : null}

      {backendStatus?.state === "mock_mode" ? (
        <div style={{ gridColumn: "span 12" }}>
          <StateCard
            tone="warn"
            title="Mock mode active"
            detail="Backend is unreachable. Run starts create mock runs only and do not execute Python pipeline logic."
            data-testid="run-builder-mock-mode"
          />
        </div>
      ) : null}

      <div style={{ gridColumn: "span 8" }}>
        <Panel title="Run Builder // Mission Setup">
          <form onSubmit={handleSubmit} data-testid="run-builder-form">
            <div className="form-grid">
              <section style={{ gridColumn: "span 6" }}>
                <label htmlFor="horizon" className="label">
                  Analysis Horizon
                </label>
                <select
                  id="horizon"
                  className="select"
                  value={horizon}
                  onChange={(event) => setHorizon(Number(event.target.value))}
                >
                  {options.horizons.map((value) => (
                    <option key={value} value={value}>
                      {value} days
                    </option>
                  ))}
                </select>
              </section>

              <section style={{ gridColumn: "span 6" }}>
                <label className="label">Selected Countries</label>
                <div className="chip ok">{selectedCountries.length} active</div>
              </section>

              <section style={{ gridColumn: "span 12" }}>
                <label className="label">Country Selection</label>
                <div className="panel high" style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "0.5rem" }}>
                  {options.countries.map((country) => {
                    const checked = selectedCountries.includes(country.code);
                    return (
                      <label key={country.code} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <input
                          type="checkbox"
                          checked={checked}
                          data-testid={`run-builder-country-toggle-${country.code.toLowerCase()}`}
                          onChange={(event) => {
                            setSelectedCountries((previous) =>
                              event.target.checked
                                ? [...previous, country.code]
                                : previous.filter((item) => item !== country.code),
                            );
                          }}
                        />
                        <span>{country.label}</span>
                      </label>
                    );
                  })}
                </div>
              </section>

              <section style={{ gridColumn: "span 12" }}>
                <label className="label">Layer/Group Selection</label>
                <div
                  className="panel high"
                  style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: "0.5rem" }}
                >
                  {options.layers.map((layer) => {
                    const checked = selectedLayers.includes(layer.key);
                    return (
                      <label key={layer.key} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <input
                          type="checkbox"
                          checked={checked}
                          data-testid={`run-builder-layer-toggle-${layer.key.toLowerCase()}`}
                          onChange={(event) => {
                            setSelectedLayers((previous) =>
                              event.target.checked
                                ? [...previous, layer.key]
                                : previous.filter((item) => item !== layer.key),
                            );
                          }}
                        />
                        <span>{layer.label}</span>
                      </label>
                    );
                  })}
                </div>
              </section>

              <section style={{ gridColumn: "span 12" }}>
                <button
                  type="button"
                  className="btn"
                  onClick={() => setAdvancedOpen((previous) => !previous)}
                  aria-expanded={advancedOpen}
                >
                  {advancedOpen ? "Hide Advanced Settings" : "Show Advanced Settings"}
                </button>
              </section>

              {advancedOpen ? (
                <section style={{ gridColumn: "span 12" }}>
                  <label htmlFor="note" className="label">
                    Analyst Note
                  </label>
                  <textarea
                    id="note"
                    className="textarea"
                    rows={3}
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="Optional run rationale..."
                  />
                </section>
              ) : null}

              <section style={{ gridColumn: "span 12", display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <button type="submit" className="btn primary" disabled={submitDisabled} data-testid="run-builder-submit">
                  {submitState.kind === "submitting" ? "Starting..." : "Start Run"}
                </button>
                <Link href="/runs" className="btn">
                  Open Run Monitor
                </Link>
                {backendUnavailable ? <span className="muted">Backend unavailable</span> : null}
              </section>
            </div>
          </form>
        </Panel>

        {submitState.kind === "error" ? (
          <div style={{ marginTop: "1rem" }} data-testid="run-builder-submit-error">
            <StateCard tone="error" title="Run start failed" detail={submitState.message} />
          </div>
        ) : null}

        {submitState.kind === "success" ? (
          <div style={{ marginTop: "1rem" }} className="panel high" data-testid="run-builder-submit-success">
            <strong>Run created:</strong> {submitState.payload.run_id}
            {submitState.payload.source === "mock" ? (
              <p className="muted" style={{ margin: "0.4rem 0 0" }}>
                Mock run only. No backend execution was started.
              </p>
            ) : null}
            <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
              <StatusBadge
                status={submitState.payload.source === "mock" ? "warn" : submitState.payload.status}
                label={submitState.payload.source === "mock" ? "mock run" : undefined}
              />
              <Link href={`/runs/${submitState.payload.run_id}`} className="linkish">
                Open run detail
              </Link>
              <Link href="/runs" className="linkish">
                Back to monitor
              </Link>
            </div>
          </div>
        ) : null}
      </div>

      <aside style={{ gridColumn: "span 4", display: "grid", gap: "1rem", alignContent: "start" }}>
        <Panel title="Live Summary" high>
          <p className="muted" style={{ marginTop: 0 }}>
            Planned execution preview for the next run submission.
          </p>
          <div className="panel">
            <p className="panel-title">Countries</p>
            <p className="kpi-value">{summary.countryCount}</p>
            <p className="muted">{summary.countriesPreview || "No countries selected"}</p>
          </div>
          <div className="panel">
            <p className="panel-title">Horizon</p>
            <p className="kpi-value">{summary.horizon}d</p>
          </div>
          <div className="panel">
            <p className="panel-title">Layers</p>
            <p className="kpi-value">{summary.layerCount}</p>
          </div>
        </Panel>

        <Panel title="MVP Notes">
          <ul style={{ margin: 0, paddingLeft: "1rem", display: "grid", gap: "0.45rem" }}>
            <li>Submit always goes through `apiClient`, no direct fetch in page code.</li>
            <li>Advanced settings are optional and safe to extend in later phases.</li>
            <li>Validation remains lightweight for MVP.</li>
          </ul>
        </Panel>
      </aside>
    </div>
  );
}
