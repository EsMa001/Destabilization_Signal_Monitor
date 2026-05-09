"use client";

import { usePathname } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { apiClient } from "@/lib/api/client";
import type { BackendConnectivityStatus } from "@/types/api";

const CLOCK_PLACEHOLDER = "---- -- -- --:--:--";
const CONNECTIVITY_POLL_MS = 30_000;

function formatUtcClock(value: Date): string {
  return value.toISOString().replace("T", " ").slice(0, 19);
}

function segmentToLabel(segment: string): string {
  const normalized = segment.trim().toLowerCase();
  switch (normalized) {
    case "":
      return "overview";
    case "runs":
      return "runs";
    case "new":
      return "run builder";
    case "countries":
      return "countries";
    case "compare":
      return "compare";
    case "artifacts":
      return "artifacts";
    case "coverage":
      return "coverage";
    case "settings":
      return "settings";
    default:
      return normalized;
  }
}

export function TopBar(): React.JSX.Element {
  const pathname = usePathname();
  const [now, setNow] = useState<string>(CLOCK_PLACEHOLDER);
  const [backendStatus, setBackendStatus] = useState<BackendConnectivityStatus | null>(null);
  const [backendStatusLoading, setBackendStatusLoading] = useState(true);

  useEffect(() => {
    const kickoff = window.setTimeout(() => {
      setNow(formatUtcClock(new Date()));
    }, 0);
    const id = window.setInterval(() => {
      setNow(formatUtcClock(new Date()));
    }, 1000);
    return () => {
      window.clearTimeout(kickoff);
      window.clearInterval(id);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function refreshConnectivity(): Promise<void> {
      const status = await apiClient.getBackendConnectivity();
      if (!cancelled) {
        setBackendStatus(status);
        setBackendStatusLoading(false);
      }
    }

    void refreshConnectivity();
    const id = window.setInterval(() => {
      void refreshConnectivity();
    }, CONNECTIVITY_POLL_MS);

    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const routeLabel = useMemo(() => {
    const segments = pathname.split("/").filter(Boolean);
    if (segments.length === 0) {
      return "overview";
    }
    return segments.map(segmentToLabel).join(" / ");
  }, [pathname]);

  const backendChip = useMemo(() => {
    if (backendStatusLoading || !backendStatus) {
      return {
        className: "chip info",
        label: "Backend checking",
        detail: "Probing health endpoint.",
      };
    }
    if (backendStatus.state === "connected") {
      return {
        className: "chip ok",
        label: "Backend connected",
        detail: backendStatus.detail,
      };
    }
    if (backendStatus.state === "mock_mode") {
      return {
        className: "chip warn",
        label: "Mock mode active",
        detail: backendStatus.detail,
      };
    }
    return {
      className: "chip error",
      label: "Backend unavailable",
      detail: backendStatus.detail,
    };
  }, [backendStatus, backendStatusLoading]);

  return (
    <header className="topbar" data-testid="topbar">
      <div style={{ display: "flex", alignItems: "center", gap: "0.9rem" }}>
        <span className="topbar-title">Tactical Intel Ops</span>
        <span className="chip">{routeLabel}</span>
        <input className="topbar-search" placeholder="QUERY_SYSTEM..." aria-label="System query" />
      </div>

      <div className="topbar-meta">
        <span className={backendChip.className} title={backendChip.detail} data-testid="backend-status-chip">
          {backendChip.label}
        </span>
        <span className={backendStatus?.mock_fallback_enabled ? "chip warn" : "chip"} data-testid="mock-mode-chip">
          {backendStatus?.mock_fallback_enabled ? "Mock fallback on" : "Mock fallback off"}
        </span>
        <span className="chip" data-testid="utc-clock-chip">
          {now} UTC
        </span>
      </div>
    </header>
  );
}
