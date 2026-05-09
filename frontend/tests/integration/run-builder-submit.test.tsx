import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { RunBuilderForm } from "@/features/runs/RunBuilderForm";
import { apiClient } from "@/lib/api/client";

describe("RunBuilderForm", () => {
  it("submits run request via api client and shows success state", async () => {
    vi.spyOn(apiClient, "getRunOptions").mockResolvedValue({
      countries: [
        { code: "Germany", label: "Germany" },
        { code: "Israel", label: "Israel" },
        { code: "Iran", label: "Iran" },
      ],
      layers: [
        { key: "event", label: "Event" },
        { key: "governance", label: "Governance" },
        { key: "market_food", label: "Market/Food" },
      ],
      horizons: [7, 30, 356],
    });
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "connected",
      label: "Backend connected",
      detail: "Health endpoint reachable.",
      checked_at: "2026-04-16T00:00:00Z",
      mock_fallback_enabled: false,
    });

    const createRun = vi.spyOn(apiClient, "createRun").mockResolvedValue({
      run_id: "run_test_123",
      status: "queued",
      created_at: "2026-04-15T12:00:00Z",
      source: "api",
    });

    render(<RunBuilderForm />);

    const submitButton = await screen.findByRole("button", { name: /start run/i });
    expect(screen.getByTestId("run-builder-country-toggle-germany")).toBeInTheDocument();
    expect(screen.getByTestId("run-builder-layer-toggle-event")).toBeInTheDocument();
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(createRun).toHaveBeenCalledTimes(1);
    });

    expect(await screen.findByText(/run created:/i)).toBeInTheDocument();
    expect(screen.getByText(/run_test_123/i)).toBeInTheDocument();
  });

  it("marks run creation as mock when backend is in mock mode", async () => {
    vi.spyOn(apiClient, "getRunOptions").mockResolvedValue({
      countries: [
        { code: "Germany", label: "Germany" },
        { code: "Israel", label: "Israel" },
        { code: "Iran", label: "Iran" },
      ],
      layers: [
        { key: "event", label: "Event" },
        { key: "governance", label: "Governance" },
      ],
      horizons: [7, 30, 356],
    });
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "mock_mode",
      label: "Mock mode active",
      detail: "Backend not reachable.",
      checked_at: "2026-04-16T00:00:00Z",
      mock_fallback_enabled: true,
    });
    vi.spyOn(apiClient, "createRun").mockResolvedValue({
      run_id: "mock_run_123",
      status: "queued",
      created_at: "2026-04-16T01:00:00Z",
      source: "mock",
    });

    render(<RunBuilderForm />);
    const submitButton = await screen.findByRole("button", { name: /start run/i });
    await userEvent.click(submitButton);

    expect(await screen.findByText(/mock run only/i)).toBeInTheDocument();
    expect(screen.getAllByText(/mock run/i).length).toBeGreaterThan(0);
  });

  it("blocks run start when backend is unavailable and mock mode is disabled", async () => {
    vi.spyOn(apiClient, "getRunOptions").mockResolvedValue({
      countries: [
        { code: "Germany", label: "Germany" },
        { code: "Israel", label: "Israel" },
      ],
      layers: [{ key: "event", label: "Event" }],
      horizons: [7, 30, 356],
    });
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "unavailable",
      label: "Backend unavailable",
      detail: "Health probe failed.",
      checked_at: "2026-04-16T00:00:00Z",
      mock_fallback_enabled: false,
    });
    const createRun = vi.spyOn(apiClient, "createRun");

    render(<RunBuilderForm />);

    expect((await screen.findAllByText(/backend unavailable/i)).length).toBeGreaterThan(0);
    const submitButton = await screen.findByRole("button", { name: /start run/i });
    expect(submitButton).toBeDisabled();
    expect(createRun).not.toHaveBeenCalled();
  });
});
