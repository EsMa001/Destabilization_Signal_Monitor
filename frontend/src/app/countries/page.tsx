"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/ui/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { StateCard } from "@/components/ui/StateCard";
import { apiClient } from "@/lib/api/client";
import type { RunOptionsResponse } from "@/types/api";

export default function CountriesIndexPage(): React.JSX.Element {
  const [options, setOptions] = useState<RunOptionsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const loaded = await apiClient.getRunOptions();
        if (!cancelled) {
          setOptions(loaded);
          setError(null);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Country options unavailable");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return <StateCard tone="error" title="Country list unavailable" detail={error} />;
  }

  if (!options) {
    return <StateCard tone="loading" title="Loading countries" />;
  }

  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 12" }}>
        <PageHeader
          title="Countries"
          subtitle="Entry point for country-level analyst detail workspaces."
          breadcrumbs={[
            { label: "Workspace", href: "/" },
            { label: "Countries" },
          ]}
        />
      </div>

      <div style={{ gridColumn: "span 12" }}>
        <Panel title="Countries">
          <p className="muted">Select a country to open the analyst detail workspace.</p>
          <div className="selection-grid">
            {options.countries.map((country) => (
              <Link key={country.code} href={`/countries/${country.code}`} className="btn">
                {country.label}
              </Link>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
