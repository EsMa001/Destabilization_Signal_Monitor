import { render, screen } from "@testing-library/react";

import { PageHeader } from "@/components/ui/PageHeader";

describe("PageHeader", () => {
  it("renders breadcrumb trail and title", () => {
    render(
      <PageHeader
        title="Coverage"
        subtitle="Status workspace"
        breadcrumbs={[
          { label: "Workspace", href: "/" },
          { label: "Coverage" },
        ]}
      />,
    );

    expect(screen.getByRole("navigation", { name: /breadcrumb/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /workspace/i })).toHaveAttribute("href", "/");
    expect(screen.getByRole("heading", { name: "Coverage" })).toBeInTheDocument();
  });
});
