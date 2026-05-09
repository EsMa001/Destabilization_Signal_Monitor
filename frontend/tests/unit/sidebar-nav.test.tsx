import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/runs/new",
}));

import { SidebarNav } from "@/components/layout/SidebarNav";

// Traceability: AP-06, AP-07
describe("SidebarNav", () => {
  it("renders navigation items and marks active section", () => {
    render(<SidebarNav />);

    expect(screen.getByTestId("sidebar-nav")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /runs/i })).toHaveClass("active");
    expect(screen.getByTestId("nav-link-overview")).toBeInTheDocument();
    expect(screen.getByTestId("nav-link-runs")).toBeInTheDocument();
    expect(screen.getByTestId("nav-link-countries")).toBeInTheDocument();
  });
});
