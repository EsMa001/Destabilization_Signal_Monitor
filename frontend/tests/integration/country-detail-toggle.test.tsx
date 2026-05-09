import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { CountryDetailView } from "@/features/countries/CountryDetailView";
import { apiClient } from "@/lib/api/client";

describe("CountryDetailView", () => {
  it("toggles between daily and long-term content", async () => {
    vi.spyOn(apiClient, "getCountryDetail").mockResolvedValue({
      country_code: "Germany",
      country_label: "Germany",
      generated_at: "2026-04-16T10:00:00Z",
      source_run_id: "run_2026_04_16_a1",
      summary: {
        status: "stable",
        confidence: 0.83,
        freshness_hours: 12,
        last_updated: "2026-04-16T09:00:00Z",
      },
      kpis: [{ id: "score", label: "Score", value: 31.4 }],
      daily_briefing: ["Daily briefing entry"],
      long_term_notes: ["Long-term note"],
      trend: [
        { timestamp: "2026-04-15T00:00:00Z", value: 30.1, confidence: 0.82, freshness_hours: 14 },
        { timestamp: "2026-04-16T00:00:00Z", value: 31.4, confidence: 0.83, freshness_hours: 12 },
      ],
      layers: [{ layer: "event", value: 0.31, status: "ok", freshness_hours: 12 }],
      coverage: {
        available_layers: 6,
        expected_layers: 7,
        coverage_ratio: 0.86,
      },
      artifacts: [],
      notes: [],
    });

    render(<CountryDetailView countryCode="Germany" />);

    expect(await screen.findByTestId("country-briefing-content")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("tab", { name: /long-term trends/i }));

    expect(screen.getByTestId("country-trend-content")).toBeInTheDocument();
  });
});
