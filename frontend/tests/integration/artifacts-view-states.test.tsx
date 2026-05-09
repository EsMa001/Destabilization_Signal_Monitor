import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { ArtifactsView } from "@/features/artifacts/ArtifactsView";
import { apiClient } from "@/lib/api/client";

// Traceability: AP-07, AP-08
describe("ArtifactsView states", () => {
  it("shows empty-state card when artifact groups are empty", async () => {
    vi.spyOn(apiClient, "getArtifactsOverview").mockResolvedValue({
      generated_at: "2026-04-17T12:00:00Z",
      runs: [],
    });

    render(<ArtifactsView />);

    expect(
      await screen.findByText(/no artifacts found for current filter/i),
    ).toBeInTheDocument();
  });

  it("shows error state when artifacts endpoint fails", async () => {
    vi.spyOn(apiClient, "getArtifactsOverview").mockRejectedValue(
      new Error("artifacts endpoint unavailable"),
    );

    render(<ArtifactsView />);

    expect(await screen.findByText(/artifacts unavailable/i)).toBeInTheDocument();
  });
});
