import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

let searchValue = "";
const replace = vi.fn();
const router = { replace };

vi.mock("next/navigation", () => ({
  usePathname: () => "/compare",
  useRouter: () => router,
  useSearchParams: () => new URLSearchParams(searchValue),
}));

import { CompareView } from "@/features/compare/CompareView";
import { apiClient } from "@/lib/api/client";

// Traceability: AP-08
describe("CompareView", () => {
  it("loads compare data and updates on country selection", async () => {
    searchValue = "";
    vi.spyOn(apiClient, "getRunOptions").mockResolvedValue({
      countries: [
        { code: "Germany", label: "Germany" },
        { code: "Iran", label: "Iran" },
        { code: "Israel", label: "Israel" },
      ],
      layers: [{ key: "event", label: "Event" }],
      horizons: [7, 30, 356],
    });

    const getCompare = vi.spyOn(apiClient, "getCompare").mockResolvedValue({
      generated_at: "2026-04-16T10:00:00Z",
      warnings: [],
      countries: [
        {
          country: "Germany",
          status: "stable",
          score: 30,
          delta_7d: 0.4,
          confidence: 0.82,
          freshness_hours: 12,
          trend: [{ timestamp: "2026-01-01T00:00:00Z", value: 20 }],
          kpis: [{ id: "score", label: "Score", value: 30 }],
        },
        {
          country: "Iran",
          status: "active",
          score: 54,
          delta_7d: 2.1,
          confidence: 0.79,
          freshness_hours: 14,
          trend: [{ timestamp: "2026-01-01T00:00:00Z", value: 40 }],
          kpis: [{ id: "score", label: "Score", value: 54 }],
        },
      ],
    });

    render(<CompareView />);

    expect(await screen.findByText(/country compare/i)).toBeInTheDocument();
    expect((await screen.findAllByText("Germany")).length).toBeGreaterThan(0);
    expect((await screen.findAllByText("Iran")).length).toBeGreaterThan(0);

    await userEvent.click(screen.getByLabelText("Israel"));
    await waitFor(() => {
      expect(getCompare).toHaveBeenCalled();
    });
  });

  it("uses countries from deep link query when available", async () => {
    searchValue = "countries=Iran,Israel";
    vi.spyOn(apiClient, "getRunOptions").mockResolvedValue({
      countries: [
        { code: "Germany", label: "Germany" },
        { code: "Iran", label: "Iran" },
        { code: "Israel", label: "Israel" },
      ],
      layers: [{ key: "event", label: "Event" }],
      horizons: [7, 30, 356],
    });
    vi.spyOn(apiClient, "getCompare").mockResolvedValue({
      generated_at: "2026-04-16T10:00:00Z",
      warnings: [],
      countries: [
        {
          country: "Iran",
          status: "active",
          score: 54,
          delta_7d: 2.1,
          confidence: 0.79,
          freshness_hours: 14,
          trend: [{ timestamp: "2026-01-01T00:00:00Z", value: 40 }],
          kpis: [{ id: "score", label: "Score", value: 54 }],
        },
        {
          country: "Israel",
          status: "watch",
          score: 51,
          delta_7d: 0.4,
          confidence: 0.77,
          freshness_hours: 9,
          trend: [{ timestamp: "2026-01-01T00:00:00Z", value: 38 }],
          kpis: [{ id: "score", label: "Score", value: 51 }],
        },
      ],
    });

    render(<CompareView />);

    expect(await screen.findByText(/country compare/i)).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "Iran" })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "Israel" })).toBeChecked();
  });
});
