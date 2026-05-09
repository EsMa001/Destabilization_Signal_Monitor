"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { FOOTER_NAV, MAIN_NAV } from "@/components/layout/navigation";

function isActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname.startsWith(href);
}

export function SidebarNav(): React.JSX.Element {
  const pathname = usePathname();
  const footerActive = isActive(pathname, FOOTER_NAV.href);

  return (
    <aside className="sidebar" aria-label="Primary navigation" data-testid="sidebar-nav">
      <div className="sidebar-brand">
        <h1 className="brand-title">STRATOS-4</h1>
        <p className="brand-subtitle">SECTOR-7 // ACTIVE</p>
      </div>

      <nav className="sidebar-nav">
        {MAIN_NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-link ${isActive(pathname, item.href) ? "active" : ""}`}
            data-testid={`nav-link-${item.href === "/" ? "overview" : item.href.slice(1)}`}
          >
            <span className="nav-icon" aria-hidden="true">
              {item.icon}
            </span>
            <span className="nav-link-label">{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="nav-icon" aria-hidden="true">
          {FOOTER_NAV.icon}
        </span>
        <Link href={FOOTER_NAV.href} className={`nav-link-label ${footerActive ? "active" : "muted"}`}>
          {FOOTER_NAV.label}
        </Link>
        <span className="status-dot" aria-hidden="true" />
      </div>
    </aside>
  );
}
