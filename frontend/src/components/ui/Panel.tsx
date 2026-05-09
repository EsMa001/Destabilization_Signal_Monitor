import type { HTMLAttributes, PropsWithChildren } from "react";

interface PanelProps extends PropsWithChildren, HTMLAttributes<HTMLElement> {
  title?: string;
  high?: boolean;
}

export function Panel({ title, high = false, className, children, ...rest }: PanelProps): React.JSX.Element {
  return (
    <section className={`panel ${high ? "high" : ""} ${className ?? ""}`.trim()} {...rest}>
      {title ? <h2 className="panel-title">{title}</h2> : null}
      {children}
    </section>
  );
}
