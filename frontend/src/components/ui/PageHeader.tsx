import Link from "next/link";
import type { PropsWithChildren } from "react";

import { SectionHeader } from "@/components/ui/SectionHeader";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface PageHeaderProps extends PropsWithChildren {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  compact?: boolean;
}

export function PageHeader({
  title,
  subtitle,
  breadcrumbs = [],
  compact = false,
  children,
}: PageHeaderProps): React.JSX.Element {
  return (
    <div className="page-header-wrap">
      {breadcrumbs.length > 0 ? (
        <nav className="breadcrumb-nav" aria-label="Breadcrumb">
          {breadcrumbs.map((crumb, index) => (
            <span key={`${crumb.label}_${index}`} className="breadcrumb-item">
              {crumb.href ? (
                <Link href={crumb.href} className="breadcrumb-link">
                  {crumb.label}
                </Link>
              ) : (
                <span className="breadcrumb-current">{crumb.label}</span>
              )}
              {index < breadcrumbs.length - 1 ? <span className="breadcrumb-sep">/</span> : null}
            </span>
          ))}
        </nav>
      ) : null}

      <SectionHeader title={title} subtitle={subtitle} compact={compact}>
        {children}
      </SectionHeader>
    </div>
  );
}
