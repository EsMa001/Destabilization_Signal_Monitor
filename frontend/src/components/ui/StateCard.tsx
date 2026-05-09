import type { HTMLAttributes } from "react";

interface StateCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string;
  detail?: string;
  tone: "loading" | "empty" | "error" | "warn" | "info";
}

export function StateCard({ title, detail, tone, className, ...rest }: StateCardProps): React.JSX.Element {
  return (
    <div
      className={className ? `state-card ${tone} ${className}` : `state-card ${tone}`}
      role={tone === "error" ? "alert" : "status"}
      {...rest}
    >
      <strong>{title}</strong>
      {detail ? <p style={{ margin: "0.4rem 0 0" }}>{detail}</p> : null}
    </div>
  );
}
