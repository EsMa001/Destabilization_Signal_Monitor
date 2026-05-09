import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { RunBuilderForm } from "@/features/runs/RunBuilderForm";
import { apiClient } from "@/lib/api/client";

// Traceability: AP-07, AP-08
describe("RunBuilderForm states", () => {
  it("shows loading state while options are pending", async () => {
    vi.spyOn(apiClient, "getRunOptions").mockImplementation(
      () => new Promise(() => {}),
    );
    vi.spyOn(apiClient, "getBackendConnectivity").mockImplementation(
      () => new Promise(() => {}),
    );

    render(<RunBuilderForm />);

    expect(screen.getByText(/loading run options/i)).toBeInTheDocument();
  });

  it("shows error state when options cannot be loaded", async () => {
    vi.spyOn(apiClient, "getRunOptions").mockRejectedValue(
      new Error("options unavailable"),
    );
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "unavailable",
      label: "Backend unavailable",
      detail: "Health probe failed.",
      checked_at: "2026-04-17T00:00:00Z",
      mock_fallback_enabled: false,
    });

    render(<RunBuilderForm />);

    expect(
      await screen.findByText(/run builder options unavailable/i),
    ).toBeInTheDocument();
  });
});
