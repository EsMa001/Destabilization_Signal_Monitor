import type { RunStatus } from "@/types/api";

type StatusVariant = RunStatus | "active" | "ok" | "warn" | "error" | "info" | "partial";

interface StatusBadgeProps {
  status: StatusVariant;
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps): React.JSX.Element {
  return (
    <span className={`status-badge ${status}`}>
      <span aria-hidden="true">*</span>
      {label ?? status}
    </span>
  );
}
