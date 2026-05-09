import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { RunMonitorTable } from "@/features/runs/RunMonitorTable";
import { apiClient } from "@/lib/api/client";

describe("RunMonitorTable", () => {
  it("renders run rows from API client", async () => {
    vi.spyOn(apiClient, "listRuns").mockResolvedValue({
      runs: [
        {
          run_id: "run_alpha",
          status: "running",
          created_at: "2026-04-15T11:00:00Z",
          started_at: "2026-04-15T11:00:10Z",
          finished_at: null,
          countries: ["Germany", "Iran"],
          progress_percent: 42,
        },
      ],
    });

    render(<RunMonitorTable />);

    expect(await screen.findByText("run_alpha")).toBeInTheDocument();
    expect(screen.getByText(/42%/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open/i })).toBeInTheDocument();
  });
});
