import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { RunMonitorTable } from "@/features/runs/RunMonitorTable";
import { apiClient } from "@/lib/api/client";

// Traceability: AP-07, AP-08
describe("RunMonitorTable states", () => {
  it("shows loading state while run list is pending", () => {
    vi.spyOn(apiClient, "listRuns").mockImplementation(
      () => new Promise(() => {}),
    );

    render(<RunMonitorTable />);

    expect(screen.getByText(/loading runs/i)).toBeInTheDocument();
  });

  it("shows empty state when no runs are returned", async () => {
    vi.spyOn(apiClient, "listRuns").mockResolvedValue({ runs: [] });

    render(<RunMonitorTable />);

    expect(
      await screen.findByText(/no runs found for current filter/i),
    ).toBeInTheDocument();
  });

  it("shows error state when run list fails", async () => {
    vi.spyOn(apiClient, "listRuns").mockRejectedValue(
      new Error("run endpoint unavailable"),
    );

    render(<RunMonitorTable />);

    expect(await screen.findByText(/run monitor unavailable/i)).toBeInTheDocument();
  });
});
