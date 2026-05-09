import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/runs",
}));

vi.mock("@/components/layout/TopBar", () => ({
  TopBar: () => <div data-testid="topbar-stub">TopBar</div>,
}));

import { AppShell } from "@/components/layout/AppShell";

describe("AppShell", () => {
  it("renders sidebar, topbar and active run navigation", () => {
    render(
      <AppShell>
        <div>workspace content</div>
      </AppShell>,
    );

    expect(screen.getByText("STRATOS-4")).toBeInTheDocument();
    expect(screen.getByTestId("topbar-stub")).toBeInTheDocument();
    expect(screen.getByText("workspace content")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /runs/i })).toHaveClass("active");
  });
});
