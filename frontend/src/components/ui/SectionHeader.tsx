import type { PropsWithChildren } from "react";

interface SectionHeaderProps extends PropsWithChildren {
  title: string;
  subtitle?: string;
  compact?: boolean;
}

export function SectionHeader({ title, subtitle, compact = false, children }: SectionHeaderProps): React.JSX.Element {
  return (
    <header className={`section-header ${compact ? "compact" : ""}`}>
      <div>
        <h2>{title}</h2>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {children ? <div className="section-header-actions">{children}</div> : null}
    </header>
  );
}
