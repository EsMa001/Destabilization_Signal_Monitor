import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { InteractiveWorldMap } from "@/components/map/InteractiveWorldMap";

describe("InteractiveWorldMap", () => {
  it("shows tooltip on hover and triggers selection on click", () => {
    const onCountrySelect = vi.fn();

    render(
      <InteractiveWorldMap
        onCountrySelect={onCountrySelect}
        countries={[
          {
            country: "Germany",
            country_code: "Germany",
            status: "stable",
            has_data: true,
            score: 33.2,
            delta_7d: 0.7,
            freshness_hours: 12,
            coverage_ratio: 0.82,
          },
        ]}
      />,
    );

    const germany = screen.getByLabelText(/germany open detail/i);
    fireEvent.mouseEnter(germany);
    fireEvent.mouseMove(germany, { clientX: 100, clientY: 120 });

    expect(screen.getByText("Germany")).toBeInTheDocument();
    fireEvent.click(germany);
    expect(onCountrySelect).toHaveBeenCalledWith("Germany");
  });
});
