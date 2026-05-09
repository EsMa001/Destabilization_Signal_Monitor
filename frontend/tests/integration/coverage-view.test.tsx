import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

import { CoverageView } from "@/features/coverage/CoverageView";
import { apiClient } from "@/lib/api/client";

describe("CoverageView", () => {
  it("renders matrix rows and filters by status", async () => {
    vi.spyOn(apiClient, "getCoverage").mockResolvedValue({
      generated_at: "2026-04-16T10:00:00Z",
      layers: ["event", "governance"],
      rows: [
        {
          country: "Germany",
          country_code: "Germany",
          status: "ok",
          available_layers: 2,
          expected_layers: 2,
          coverage_ratio: 1,
          freshness_hours: 10,
          last_updated: "2026-04-16T09:00:00Z",
          layer_status: { event: "ok", governance: "ok" },
          warnings: [],
        },
        {
          country: "Iran",
          country_code: "Iran",
          status: "missing",
          available_layers: 0,
          expected_layers: 2,
          coverage_ratio: 0,
          freshness_hours: 88,
          last_updated: "2026-04-15T09:00:00Z",
          layer_status: { event: "missing", governance: "missing" },
          warnings: ["No source data"],
        },
      ],
      warnings: ["Derived mode active"],
    });

    render(<CoverageView />);

    expect(await screen.findByText(/coverage \/ data status/i)).toBeInTheDocument();
    expect(screen.getByText("Germany")).toBeInTheDocument();
    expect(screen.getByText("Iran")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /missing/i }));

    expect(screen.queryByText("Germany")).not.toBeInTheDocument();
    expect(screen.getByText("Iran")).toBeInTheDocument();
    expect(screen.getByText("Derived mode active")).toBeInTheDocument();
  });
});
