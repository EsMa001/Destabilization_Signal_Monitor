import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

import { CoverageView } from "@/features/coverage/CoverageView";
import { apiClient } from "@/lib/api/client";

// Traceability: AP-07, AP-08
describe("CoverageView states", () => {
  it("shows empty-state card when coverage rows are empty", async () => {
    vi.spyOn(apiClient, "getCoverage").mockResolvedValue({
      generated_at: "2026-04-17T12:00:00Z",
      layers: ["event"],
      rows: [],
      warnings: [],
    });

    render(<CoverageView />);

    expect(
      await screen.findByText(/coverage matrix empty for current filter/i),
    ).toBeInTheDocument();
  });

  it("shows error state when coverage endpoint fails", async () => {
    vi.spyOn(apiClient, "getCoverage").mockRejectedValue(
      new Error("coverage endpoint unavailable"),
    );

    render(<CoverageView />);

    expect(await screen.findByText(/coverage unavailable/i)).toBeInTheDocument();
  });
});
