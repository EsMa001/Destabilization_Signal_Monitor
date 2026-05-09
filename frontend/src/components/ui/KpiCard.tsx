import { StatusBadge } from "@/components/ui/StatusBadge";

interface KpiCardProps {
  label: string;
  value: string | number;
  unit?: string;
  delta?: number | null;
  status?: "ok" | "info" | "warn" | "critical";
}

function formatDelta(delta?: number | null): string | null {
  if (delta === null || delta === undefined || Number.isNaN(delta)) {
    return null;
  }
  return `${delta > 0 ? "+" : ""}${delta.toFixed(2)}`;
}

export function KpiCard({ label, value, unit, delta, status }: KpiCardProps): React.JSX.Element {
  const deltaLabel = formatDelta(delta);
  const renderedValue =
    typeof value === "number" && Number.isFinite(value) ? value.toLocaleString("de-DE", { maximumFractionDigits: 2 }) : value;

  return (
    <div className="kpi-card">
      <p className="panel-title" style={{ marginBottom: "0.35rem" }}>
        {label}
      </p>
      <p className="kpi-value">
        {renderedValue}
        {unit ? <span className="kpi-unit">{unit}</span> : null}
      </p>
      <div className="kpi-meta">
        {deltaLabel ? (
          <span className={delta !== null && delta !== undefined && delta > 0 ? "kpi-delta up" : "kpi-delta down"}>{deltaLabel}</span>
        ) : (
          <span className="muted">No delta</span>
        )}
        {status ? <StatusBadge status={status === "critical" ? "error" : status} /> : null}
      </div>
    </div>
  );
}
