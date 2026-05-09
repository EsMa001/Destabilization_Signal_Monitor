import { hydrateRoot } from "react-dom/client";
import { renderToString } from "react-dom/server";
import { act } from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/runs/new",
}));

import { TopBar } from "@/components/layout/TopBar";
import { apiClient } from "@/lib/api/client";

// Traceability: AP-01, AP-06, AP-07
describe("TopBar", () => {
  it("shows backend state and clock metadata", async () => {
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "connected",
      label: "Backend connected",
      detail: "Health endpoint reachable.",
      checked_at: "2026-04-16T00:00:00Z",
      mock_fallback_enabled: false,
    });

    render(<TopBar />);

    expect(await screen.findByTestId("backend-status-chip")).toHaveTextContent(/backend connected/i);
    expect(screen.getByTestId("mock-mode-chip")).toHaveTextContent(/mock fallback off/i);
    expect(screen.getByTestId("utc-clock-chip")).toHaveTextContent(/UTC/);
  });

  it("surfaces explicit mock mode state", async () => {
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "mock_mode",
      label: "Mock mode active",
      detail: "Backend unavailable; explicit fallback mode.",
      checked_at: "2026-04-16T00:00:00Z",
      mock_fallback_enabled: true,
    });

    render(<TopBar />);

    expect(await screen.findByTestId("backend-status-chip")).toHaveTextContent(/mock mode active/i);
    expect(screen.getByTestId("mock-mode-chip")).toHaveTextContent(/mock fallback on/i);
  });

  it("hydrates without hydration mismatch warnings", async () => {
    vi.spyOn(apiClient, "getBackendConnectivity").mockResolvedValue({
      state: "connected",
      label: "Backend connected",
      detail: "Health endpoint reachable.",
      checked_at: "2026-04-16T00:00:00Z",
      mock_fallback_enabled: false,
    });

    const serverMarkup = renderToString(<TopBar />);
    const container = document.createElement("div");
    container.innerHTML = serverMarkup;

    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    const root = hydrateRoot(container, <TopBar />);
    await act(async () => {
      await Promise.resolve();
    });

    const hydrationWarnings = errorSpy.mock.calls
      .flat()
      .map((entry) => String(entry))
      .filter((message) => message.toLowerCase().includes("hydration"));
    expect(hydrationWarnings).toHaveLength(0);
    root.unmount();
    errorSpy.mockRestore();
  });
});
