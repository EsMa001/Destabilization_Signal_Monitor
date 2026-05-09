import { fireEvent, render, screen } from "@testing-library/react";

import { TrendLineChart } from "@/components/charts/TrendLineChart";

describe("TrendLineChart", () => {
  it("shows hover card with series values", () => {
    render(
      <TrendLineChart
        series={[
          {
            id: "score",
            label: "Score",
            color: "#51e1a5",
            points: [
              { timestamp: "2026-01-01T00:00:00Z", value: 10 },
              { timestamp: "2026-01-02T00:00:00Z", value: 12.5 },
            ],
          },
          {
            id: "confidence",
            label: "Confidence",
            color: "#8ed0ff",
            points: [
              { timestamp: "2026-01-01T00:00:00Z", value: 70 },
              { timestamp: "2026-01-02T00:00:00Z", value: 73 },
            ],
          },
        ]}
      />,
    );

    const chart = screen.getByRole("img", { name: /trend chart/i });
    fireEvent.mouseMove(chart, { clientX: 220, clientY: 100 });

    expect(screen.getAllByText(/score/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/confidence/i).length).toBeGreaterThan(0);
  });
});
