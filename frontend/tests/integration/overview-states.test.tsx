import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

import { OverviewPage } from "@/features/overview/OverviewPage";
import { apiClient } from "@/lib/api/client";

describe("OverviewPage states", () => {
  it("renders loading state while overview payload is pending", () => {
    vi.spyOn(apiClient, "getHealth").mockImplementation(() => new Promise(() => {}));
    vi.spyOn(apiClient, "getOverviewSnapshot").mockImplementation(() => new Promise(() => {}));

    render(<OverviewPage />);

    expect(screen.getByText(/loading overview/i)).toBeInTheDocument();
  });

  it("renders error state when overview loading fails", async () => {
    vi.spyOn(apiClient, "getHealth").mockRejectedValue(new Error("health unavailable"));
    vi.spyOn(apiClient, "getOverviewSnapshot").mockRejectedValue(new Error("overview unavailable"));

    render(<OverviewPage />);

    expect(await screen.findByText(/overview currently unavailable/i)).toBeInTheDocument();
  });

  it("renders empty state when overview returns no snapshot payload", async () => {
    vi.spyOn(apiClient, "getHealth").mockResolvedValue({
      status: "ok",
      api_version: "v1",
      timestamp: "2026-04-17T11:00:00Z",
    });
    vi.spyOn(apiClient, "getOverviewSnapshot").mockResolvedValue(null as never);

    render(<OverviewPage />);

    expect(await screen.findByText(/no overview data yet/i)).toBeInTheDocument();
  });
});
