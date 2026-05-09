import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ArtifactsView } from "@/features/artifacts/ArtifactsView";
import { apiClient } from "@/lib/api/client";

describe("ArtifactsView", () => {
  it("renders grouped artifacts and supports available-only mode", async () => {
    vi.spyOn(apiClient, "getArtifactsOverview").mockResolvedValue({
      generated_at: "2026-04-16T10:00:00Z",
      runs: [
        {
          run_id: "run_123",
          status: "completed",
          created_at: "2026-04-16T08:00:00Z",
          artifacts: [
            {
              id: "summary",
              label: "Summary Export",
              type: "json",
              path: "/api/v1/runs/run_123/summary",
              available: true,
              status: "available",
            },
            {
              id: "pending_plot",
              label: "Plot Pack",
              type: "png",
              path: "/api/v1/runs/run_123/plot-pack",
              available: false,
              status: "pending",
            },
            {
              id: "bundle",
              label: "Bundle",
              type: "bundle",
              path: "/api/v1/runs/run_123/bundle",
              available: true,
              status: "available",
            },
          ],
          bundle: {
            id: "bundle",
            label: "Bundle",
            type: "bundle",
            path: "/api/v1/runs/run_123/bundle",
            available: true,
            status: "available",
          },
        },
      ],
    });

    render(<ArtifactsView />);

    expect(await screen.findByText(/artifacts \/ reports/i)).toBeInTheDocument();
    expect(screen.getByText("Summary Export")).toBeInTheDocument();
    expect(screen.getByText("Plot Pack")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("checkbox", { name: /available only/i }));
    expect(screen.queryByText("Plot Pack")).not.toBeInTheDocument();
    expect(screen.getByText("Summary Export")).toBeInTheDocument();
  });
});
