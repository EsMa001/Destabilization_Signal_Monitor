import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("@/features/runs/RunDetailView", () => ({
  RunDetailView: ({ runId }: { runId: string }) => <div>run detail {runId}</div>,
}));

vi.mock("@/features/countries/CountryDetailView", () => ({
  CountryDetailView: ({ countryCode }: { countryCode: string }) => <div>country detail {countryCode}</div>,
}));

import CountryDetailPage from "@/app/countries/[countryCode]/page";
import RunDetailPage from "@/app/runs/[runId]/page";

describe("dynamic app-router params", () => {
  it("awaits runId params promise in run detail page", async () => {
    const view = await RunDetailPage({ params: Promise.resolve({ runId: "run_123" }) });
    render(view);
    expect(screen.getByText(/run detail run_123/i)).toBeInTheDocument();
  });

  it("awaits countryCode params promise in country detail page", async () => {
    const view = await CountryDetailPage({ params: Promise.resolve({ countryCode: "Germany" }) });
    render(view);
    expect(screen.getByText(/country detail Germany/i)).toBeInTheDocument();
  });
});
